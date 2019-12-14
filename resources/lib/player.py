import sys
import xbmc
import xbmcgui
import xbmcvfs
import datetime
import resources.lib.utils as utils
from json import loads
from string import Formatter
from collections import defaultdict
from resources.lib.plugin import Plugin
from resources.lib.kodilibrary import KodiLibrary
from resources.lib.traktapi import traktAPI


def string_format_map(fmt, d):
    try:
        str.format_map
    except AttributeError:
        parts = Formatter().parse(fmt)
        return fmt.format(**{part[1]: d[part[1]] for part in parts})
    else:
        return fmt.format(**d)


class Player(Plugin):
    def __init__(self):
        super(Player, self).__init__()
        self.traktapi = traktAPI()
        self.search_movie, self.search_episode, self.play_movie, self.play_episode = [], [], [], []
        self.item = defaultdict(lambda: '+')
        self.itemlist = []
        self.actions = []
        self.players = {}

    def setup_players(self, tmdbtype=None, details=False, clearsetting=False):
        self.build_players(tmdbtype)
        if details:
            self.build_details()
        self.build_selectbox(clearsetting)

    def play(self, itemtype, tmdb_id, season=None, episode=None):
        self.itemtype, self.tmdb_id, self.season, self.episode = itemtype, tmdb_id, season, episode
        self.tmdbtype = 'tv' if self.itemtype == 'episode' or self.itemtype == 'tv' else 'movie'
        self.details = self.tmdb.get_detailed_item(self.tmdbtype, tmdb_id, season=season, episode=episode)
        self.item['imdb_id'] = self.details.get('infolabels', {}).get('imdbnumber')
        self.item['originaltitle'] = self.details.get('infolabels', {}).get('originaltitle')
        self.item['title'] = self.details.get('infolabels', {}).get('tvshowtitle') or self.details.get('infolabels', {}).get('title')
        self.item['year'] = self.details.get('infolabels', {}).get('year')
        if self.details and self.itemtype == 'movie':
            is_local = self.playmovie()
        if self.details and self.itemtype == 'episode':
            is_local = self.playepisode()
        if is_local:
            return True
        with utils.busy_dialog():
            self.setup_players(details=True)
        if self.itemlist:
            default_player_movies = self.addon.getSetting('default_player_movies')
            default_player_episodes = self.addon.getSetting('default_player_episodes')
            itemindex = -1

            if (self.itemtype == 'movie' and not default_player_movies) or (self.itemtype == 'episode' and not default_player_episodes):
                itemindex = xbmcgui.Dialog().select('Choose Action', self.itemlist)
            else:
                for index in range(0, len(self.itemlist)):
                    item = self.itemlist[index]
                    label = item.getLabel()
                    if (label == default_player_movies and self.itemtype == 'movie') or (label == default_player_episodes and self.itemtype == 'episode'):
                        itemindex = index
                        break

            if itemindex > -1:
                action = self.actions[itemindex]
                utils.kodi_log(action, 1)
                xbmc.executebuiltin(action) if sys.version_info.major == 3 else xbmc.executebuiltin(action.encode('utf-8'))
                return True

    def build_details(self):
        self.item['id'] = self.tmdb_id
        self.item['tmdb'] = self.tmdb_id
        self.item['imdb'] = self.details.get('infolabels', {}).get('imdbnumber')
        self.item['name'] = u'{0} ({1})'.format(self.item.get('title'), self.item.get('year'))
        self.item['firstaired'] = self.details.get('infolabels', {}).get('premiered')
        self.item['premiered'] = self.details.get('infolabels', {}).get('premiered')
        self.item['released'] = self.details.get('infolabels', {}).get('premiered')
        self.item['showname'] = self.item.get('title')
        self.item['clearname'] = self.item.get('title')
        self.item['tvshowtitle'] = self.item.get('title')
        self.item['title'] = self.item.get('title')
        self.item['thumbnail'] = self.details.get('thumb')
        self.item['poster'] = self.details.get('poster')
        self.item['fanart'] = self.details.get('fanart')
        self.item['now'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

        if self.traktapi:
            slug_type = utils.type_convert(self.tmdbtype, 'trakt')
            trakt_details = self.traktapi.get_details(slug_type, self.traktapi.get_traktslug(slug_type, 'tmdb', self.tmdb_id))
            self.item['trakt'] = trakt_details.get('ids', {}).get('trakt')
            self.item['imdb'] = trakt_details.get('ids', {}).get('imdb')
            self.item['tvdb'] = trakt_details.get('ids', {}).get('tvdb')
            self.item['slug'] = trakt_details.get('ids', {}).get('slug')

        if self.itemtype == 'episode':  # Do some special episode stuff
            self.item['id'] = self.item.get('tvdb')
            self.item['title'] = self.details.get('infolabels', {}).get('title')  # Set Episode Title
            self.item['name'] = u'{0} S{1:02d}E{2:02d}'.format(self.item.get('showname'), int(self.season), int(self.episode))
            self.item['season'] = self.season
            self.item['episode'] = self.episode

        if self.traktapi and self.itemtype == 'episode':
            trakt_details = self.traktapi.get_details(slug_type, self.item.get('slug'), season=self.season, episode=self.episode)
            self.item['epid'] = trakt_details.get('ids', {}).get('tvdb')
            self.item['epimdb'] = trakt_details.get('ids', {}).get('imdb')
            self.item['eptmdb'] = trakt_details.get('ids', {}).get('tmdb')
            self.item['eptrakt'] = trakt_details.get('ids', {}).get('trakt')

        for k, v in self.item.copy().items():
            v = u'{0}'.format(v)
            self.item[k] = v.replace(',', '')
            self.item[k + '_+'] = v.replace(' ', '+')
            self.item[k + '_-'] = v.replace(' ', '-')
            self.item[k + '_escaped'] = v.replace(' ', '%2520')
            self.item[k + '_escaped+'] = v.replace(' ', '%252B')

    def build_players(self, tmdbtype=None):
        basedirs = [
            'special://profile/addon_data/plugin.video.themoviedb.helper/players/',
            'special://home/addons/plugin.video.themoviedb.helper/resources/players/']
        for basedir in basedirs:
            files = [x for x in xbmcvfs.listdir(basedir)[1] if x.endswith('.json')]
            for file in files:
                f = xbmcvfs.File(basedir + file)
                try:
                    content = f.read()
                    meta = loads(content) or {}
                finally:
                    f.close()
                if not meta.get('plugin') or not xbmc.getCondVisibility(u'System.HasAddon({0})'.format(meta.get('plugin'))):
                    continue  # Don't have plugin so skip

                tmdbtype = tmdbtype or self.tmdbtype
                if tmdbtype == 'movie' and meta.get('search_movie'):
                    self.search_movie.append(meta.get('plugin'))
                if tmdbtype == 'movie' and meta.get('play_movie'):
                    self.play_movie.append(meta.get('plugin'))
                if tmdbtype == 'tv' and meta.get('search_episode'):
                    self.search_episode.append(meta.get('plugin'))
                if tmdbtype == 'tv' and meta.get('play_episode'):
                    self.play_episode.append(meta.get('plugin'))
                self.players[meta.get('plugin')] = meta

    def build_selectbox(self, clearsetting=False):
        self.itemlist, self.actions = [], []
        if clearsetting:
            self.itemlist.append(xbmcgui.ListItem('Clear Default'))
        call = u'call_update=' if xbmc.getCondVisibility("Window.IsMedia") else u'call_path='
        for i in self.play_movie:
            self.itemlist.append(xbmcgui.ListItem(u'Play with {0}'.format(self.players.get(i, {}).get('name', ''))))
            action = string_format_map(self.players.get(i, {}).get('play_movie', ''), self.item)
            self.actions.append(u'RunPlugin({0})'.format(action))
        for i in self.search_movie:
            self.itemlist.append(xbmcgui.ListItem(u'Search {0}' .format(self.players.get(i, {}).get('name', ''))))
            action = string_format_map(self.players.get(i, {}).get('search_movie', ''), self.item)
            self.actions.append(u'RunScript(plugin.video.themoviedb.helper,{0}{1})'.format(call, action))
        for i in self.play_episode:
            self.itemlist.append(xbmcgui.ListItem(u'Play with {0}'.format(self.players.get(i, {}).get('name', ''))))
            action = string_format_map(self.players.get(i, {}).get('play_episode', ''), self.item)
            self.actions.append(u'RunPlugin({0})'.format(action))
        for i in self.search_episode:
            self.itemlist.append(xbmcgui.ListItem(u'Search {0}'.format(self.players.get(i, {}).get('name', ''))))
            action = string_format_map(self.players.get(i, {}).get('search_episode', ''), self.item)
            self.actions.append(u'RunScript(plugin.video.themoviedb.helper,{0}{1})'.format(call, action))

    def playfile(self, file):
        if file:
            xbmc.executebuiltin(u'PlayMedia({0})'.format(file))
            return True

    def playmovie(self):
        if self.playfile(KodiLibrary(dbtype='movie').get_info('file', **self.item)):
            return True

    def playepisode(self):
        dbid = KodiLibrary(dbtype='tvshow').get_info('dbid', **self.item)
        if self.playfile(KodiLibrary(dbtype='episode', tvshowid=dbid).get_info('file', season=self.season, episode=self.episode)):
            return True
