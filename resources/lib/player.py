import sys
import xbmc
import xbmcaddon
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
_addonname = 'plugin.video.themoviedb.helper'
_addon = xbmcaddon.Addon(_addonname)


def string_format_map(fmt, d):
    try:
        str.format_map
    except AttributeError:
        parts = Formatter().parse(fmt)
        return fmt.format(**{part[1]: d[part[1]] for part in parts})
    else:
        return fmt.format(**d)


def update_players():
    from io import BytesIO
    import os
    import shutil
    import zipfile
    
    _players_url = _addon.getSetting('players_url')
    _player_path = 'special://profile/addon_data/plugin.video.themoviedb.helper/players'
    _extract_to = xbmc.translatePath(_player_path)
    _temp_zip = os.path.join(_extract_to, 'temp.zip')
    
    response = utils.open_url(_players_url)
    
    if response:
        clear = xbmcgui.Dialog().yesno(_addon.getAddonInfo('name'), 'Would you like to clear existing players first?')
    
        if clear:
            for filename in os.listdir(_extract_to):
                file_path = os.path.join(_extract_to, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except:
                    pass
    
        with zipfile.ZipFile(BytesIO(response.content)) as player_zip:
            for item in [x for x in player_zip.namelist() if x.endswith('.json')]:
                filename = os.path.basename(item)
                if not filename:
                    continue
                    
                file = player_zip.open(item)
                target = open(os.path.join(_extract_to, filename), 'w')
                
                with file, target:
                    shutil.copyfileobj(file, target)
        
        try:
            os.remove(_temp_zip)
        except:
            pass
    else:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), 'The provided player URL is either invalid or inaccesible.')
        

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
        self.itemlist = []
        self.actions = []
        self.players = {}
        self.router()

    def router(self):
        if self.details and self.itemtype == 'movie':
            is_local = self.playmovie()
        if self.details and self.itemtype == 'episode':
            is_local = self.playepisode()
        if not is_local:
            with utils.busy_dialog():
                self.build_players()
                self.build_details()
                self.build_selectbox()
        if self.itemlist:
            itemindex = xbmcgui.Dialog().select('Choose Action', self.itemlist)
            if itemindex > -1:
                utils.kodi_log(self.actions[itemindex], 1)
                xbmc.executebuiltin(self.actions[itemindex]) if sys.version_info.major == 3 else xbmc.executebuiltin(self.actions[itemindex].encode('utf-8'))

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
        self.itemlist, self.actions = [], []
        prefix = u'ActivateWindow(videos, ' if not xbmc.getCondVisibility('Window.IsVisible(MyVideoNav.xml)') else u'Container.Update('
        suffix = u', return)' if not xbmc.getCondVisibility('Window.IsVisible(MyVideoNav.xml)') else u')'
        for i in self.play_movie:
            self.itemlist.append(xbmcgui.ListItem(u'Play with {0}'.format(self.players.get(i, {}).get('name', ''))))
            action = string_format_map(self.players.get(i, {}).get('play_movie', ''), self.item)
            self.actions.append(u'PlayMedia({0})'.format(action))
        for i in self.search_movie:
            self.itemlist.append(xbmcgui.ListItem(u'Search {0}' .format(self.players.get(i, {}).get('name', ''))))
            action = string_format_map(self.players.get(i, {}).get('search_movie', ''), self.item)
            self.actions.append(u'{0}{1}{2}'.format(prefix, action, suffix))
        for i in self.play_episode:
            self.itemlist.append(xbmcgui.ListItem(u'Play with {0}'.format(self.players.get(i, {}).get('name', ''))))
            action = string_format_map(self.players.get(i, {}).get('play_episode', ''), self.item)
            self.actions.append(u'PlayMedia({0})'.format(action))
        for i in self.search_episode:
            self.itemlist.append(xbmcgui.ListItem(u'Search {0}'.format(self.players.get(i, {}).get('name', ''))))
            action = string_format_map(self.players.get(i, {}).get('search_episode', ''), self.item)
            self.actions.append(u'{0}{1}{2}'.format(prefix, action, suffix))
            
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
