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
    def __init__(self, itemtype, tmdb_id, season=None, episode=None):
        super(Player, self).__init__()
        self.traktapi = traktAPI() if self.addon.getSetting('trakt_token') else None
        self.itemtype, self.tmdb_id, self.season, self.episode = itemtype, tmdb_id, season, episode
        self.search_movie, self.search_episode, self.play_movie, self.play_episode = [], [], [], []
        self.tmdbtype = 'tv' if self.itemtype == 'episode' or self.itemtype == 'tv' else 'movie'
        self.details = self.tmdb.get_detailed_item(self.tmdbtype, tmdb_id, season=season, episode=episode)
        self.item = defaultdict(lambda: '+')
        self.item['imdb_id'] = self.details.get('infolabels', {}).get('imdbnumber')
        self.item['originaltitle'] = self.details.get('infolabels', {}).get('originaltitle')
        self.item['title'] = self.details.get('infolabels', {}).get('tvshowtitle') or self.details.get('infolabels', {}).get('title')
        self.item['year'] = self.details.get('infolabels', {}).get('year')
        self.players = {}
        self.router()

    def router(self):
        if self.details and self.itemtype == 'movie':
            is_local = self.playmovie()
        if self.details and self.itemtype == 'episode':
            is_local = self.playepisode()
        if not is_local:
            self.build_players()
            self.build_details()
            self.build_selectbox()

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

        for k, v in self.item.items():
            v = u'{0}'.format(v)
            self.item[k] = v.replace(',', '')
            self.item[k + '_+'] = v.replace(' ', '+')
            self.item[k + '_-'] = v.replace(' ', '-')
            self.item[k + '_escaped'] = v.replace(' ', '%2520')
            self.item[k + '_escaped+'] = v.replace(' ', '%252B')

    def build_players(self):
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
                if self.tmdbtype == 'movie' and meta.get('search_movie'):
                    self.search_movie.append(meta.get('plugin'))
                if self.tmdbtype == 'movie' and meta.get('play_movie'):
                    self.play_movie.append(meta.get('plugin'))
                if self.tmdbtype == 'tv' and meta.get('search_episode'):
                    self.search_episode.append(meta.get('plugin'))
                if self.tmdbtype == 'tv' and meta.get('play_episode'):
                    self.play_episode.append(meta.get('plugin'))
                self.players[meta.get('plugin')] = meta

    def build_selectbox(self):
        itemlist, actions = [], []
        prefix = 'ActivateWindow(videos, ' if not xbmc.getCondVisibility('Window.IsVisible(MyVideoNav.xml)') else 'Container.Update('
        suffix = ', return)' if not xbmc.getCondVisibility('Window.IsVisible(MyVideoNav.xml)') else ')'
        for i in self.play_movie:
            itemlist.append(xbmcgui.ListItem('Play with ' + self.players.get(i, {}).get('name', '')))
            action = string_format_map(self.players.get(i, {}).get('play_movie', ''), self.item)
            actions.append(u'PlayMedia({0})'.format(action))
        for i in self.search_movie:
            itemlist.append(xbmcgui.ListItem('Search ' + self.players.get(i, {}).get('name', '')))
            action = string_format_map(self.players.get(i, {}).get('search_movie', ''), self.item)
            actions.append(u'{0}{1}{2}'.format(prefix, action, suffix))
        for i in self.play_episode:
            itemlist.append(xbmcgui.ListItem('Play with ' + self.players.get(i, {}).get('name', '')))
            action = string_format_map(self.players.get(i, {}).get('play_episode', ''), self.item)
            actions.append(u'PlayMedia({0})'.format(action))
        for i in self.search_episode:
            itemlist.append(xbmcgui.ListItem('Search ' + self.players.get(i, {}).get('name', '')))
            action = string_format_map(self.players.get(i, {}).get('search_episode', ''), self.item)
            actions.append(u'{0}{1}{2}'.format(prefix, action, suffix))
        itemindex = xbmcgui.Dialog().select('Choose Action', itemlist)
        if itemindex > -1:
            utils.kodi_log(actions[itemindex], 1)
            xbmc.executebuiltin(actions[itemindex])

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
