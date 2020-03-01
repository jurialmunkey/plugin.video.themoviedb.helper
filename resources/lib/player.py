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
from resources.lib.traktapi import TraktAPI
from resources.lib.listitem import ListItem
try:
    from urllib.parse import quote_plus  # Py3
except ImportError:
    from urllib import quote_plus  # Py2


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
        self.traktapi = TraktAPI()
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

    def get_itemindex(self, force_dialog=False):
        default_player_movies = self.addon.getSettingString('default_player_movies')
        default_player_episodes = self.addon.getSettingString('default_player_episodes')
        if force_dialog or (self.itemtype == 'movie' and not default_player_movies) or (self.itemtype == 'episode' and not default_player_episodes):
            return xbmcgui.Dialog().select(self.addon.getLocalizedString(32042), self.itemlist)
        itemindex = -1
        for index in range(0, len(self.itemlist)):
            label = self.itemlist[index].getLabel()
            if (label == default_player_movies and self.itemtype == 'movie') or (label == default_player_episodes and self.itemtype == 'episode'):
                return index
        return itemindex

    def play_external(self, force_dialog=False):
        itemindex = self.get_itemindex(force_dialog=force_dialog)

        # User cancelled dialog
        if not itemindex > -1:
            return False

        player = self.actions[itemindex]
        if not player or not player[1]:
            return False

        # External player has list of actions so let's iterate through them to find our item
        resolve_url = False
        if isinstance(player[1], list):
            actionlist = player[1]
            player = (False, actionlist[0])
            for d in actionlist[1:]:
                if d.get('no_folder'):
                    resolve_url = True
                    player = (resolve_url, actionlist[0])

                if player[0]:
                    break  # Playable item was found in last action so let's break and play it
                folder = KodiLibrary().get_directory(string_format_map(player[1], self.item))  # Get the next folder from the plugin

                if d.get('dialog'):  # Special option to show dialog of items to select from
                    d_items = []
                    for f in folder:  # Create our list of items
                        if f.get('season') and f.get('episode'):
                            li = u'{}x{}. {}'.format(f.get('season'), f.get('episode'), f.get('label'))
                        else:
                            li = u'{} ({})'.format(f.get('label'), f.get('year'))
                        d_items.append(li)
                    idx = xbmcgui.Dialog().select('Select Item to Play', d_items)
                    if idx > -1:  # If user didn't exit dialog get the item
                        resolve_url = True if folder[idx].get('filetype') == 'file' else False  # Set true for files so we can play
                        player = (resolve_url, folder[idx].get('file'))  # Set the folder path to open/play
                    else:
                        player = None
                    break  # Move onto next action

                x = 0
                for f in folder:  # Iterate through plugin folder looking for a matching item
                    x += 1  # Keep an index for position matching
                    for k, v in d.items():  # Iterate through our key (infolabel) / value (infolabel must match) pairs of our action
                        if k == 'position':  # We're looking for an item position not an infolabel
                            if utils.try_parse_int(string_format_map(v, self.item)) != x:  # Format our position value
                                break  # Not the item position we want so let's go to next item in folder
                        elif not f.get(k) or string_format_map(v, self.item) not in u'{}'.format(f.get(k, '')):  # Format our value and check if it matches the infolabel key
                            break  # Item's key value doesn't match value we are looking for so let's got to next item in folder
                    else:  # Item matched our criteria so let's open it up
                        resolve_url = True if f.get('filetype') == 'file' else False  # Set true for files so we can play
                        player = (resolve_url, f.get('file'))  # Get ListItem.FolderPath for item
                        break  # Move onto next action (either open next folder or play file)
                else:
                    xbmcgui.Dialog().notification(self.itemlist[itemindex].getLabel(), self.addon.getLocalizedString(32040))
                    del self.actions[itemindex]  # Item not found so remove the player's action list
                    del self.itemlist[itemindex]  # Item not found so remove the player's select dialog entry
                    return self.play_external(force_dialog=True)  # Ask user to select a different player

        # Play/Search found item
        if player and player[1]:
            action = string_format_map(player[1], self.item)
            if player[0]:  # Action is play so let's play the item and return
                xbmc.Player().play(action, ListItem(library='video', **self.details).set_listitem())
                return action
            # Action is search so let's load the plugin path
            action = u'Container.Update({0})'.format(action) if xbmc.getCondVisibility("Window.IsMedia") else u'ActivateWindow(videos,{0},return)'.format(action)
            xbmc.executebuiltin(utils.try_decode_string(action))
            return action

    def play(self, itemtype, tmdb_id, season=None, episode=None, force_dialog=False):
        """ Entry point for player method """
        if not tmdb_id or not itemtype:
            return

        # Get the details for the item
        self.itemtype, self.tmdb_id, self.season, self.episode = itemtype, tmdb_id, season, episode
        self.tmdbtype = 'tv' if self.itemtype in ['episode', 'tv'] else 'movie'
        self.details = self.tmdb.get_detailed_item(self.tmdbtype, tmdb_id, season=season, episode=episode)
        self.item['imdb_id'] = self.details.get('infolabels', {}).get('imdbnumber')
        self.item['originaltitle'] = self.details.get('infolabels', {}).get('originaltitle')
        self.item['title'] = self.details.get('infolabels', {}).get('tvshowtitle') or self.details.get('infolabels', {}).get('title')
        self.item['year'] = self.details.get('infolabels', {}).get('year')

        # Attempt to play local file first
        is_local = False
        if self.details and self.itemtype == 'movie':
            is_local = self.playmovie()
        if self.details and self.itemtype == 'episode':
            is_local = self.playepisode()
        if is_local:
            return is_local

        self.setup_players(details=True)

        if not self.itemlist:
            return False

        return self.play_external(force_dialog=force_dialog)

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
            self.item['name'] = u'{0} S{1:02d}E{2:02d}'.format(self.item.get('showname'), int(utils.try_parse_int(self.season)), int(utils.try_parse_int(self.episode)))
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
            self.item[k + '_url'] = quote_plus(utils.try_encode_string(v))

    def build_players(self, tmdbtype=None):
        basedirs = ['special://profile/addon_data/plugin.video.themoviedb.helper/players/']
        if self.addon.getSettingBool('bundled_players'):
            basedirs.append('special://home/addons/plugin.video.themoviedb.helper/resources/players/')
        for basedir in basedirs:
            files = [x for x in xbmcvfs.listdir(basedir)[1] if x.endswith('.json')]
            for file in files:
                vfs_file = xbmcvfs.File(basedir + file)
                try:
                    content = vfs_file.read()
                    meta = loads(content) or {}
                finally:
                    vfs_file.close()
                if not meta.get('plugin') or not xbmc.getCondVisibility(u'System.HasAddon({0})'.format(meta.get('plugin'))):
                    continue  # Don't have plugin so skip

                tmdbtype = tmdbtype or self.tmdbtype
                priority = utils.try_parse_int(meta.get('priority')) or 1000
                if tmdbtype == 'movie' and meta.get('search_movie'):
                    self.search_movie.append((vfs_file, priority))
                if tmdbtype == 'movie' and meta.get('play_movie'):
                    self.play_movie.append((vfs_file, priority))
                if tmdbtype == 'tv' and meta.get('search_episode'):
                    self.search_episode.append((vfs_file, priority))
                if tmdbtype == 'tv' and meta.get('play_episode'):
                    self.play_episode.append((vfs_file, priority))
                self.players[vfs_file] = meta

    def build_selectbox(self, clearsetting=False):
        self.itemlist, self.actions = [], []
        if clearsetting:
            self.itemlist.append(xbmcgui.ListItem(xbmc.getLocalizedString(13403)))  # Clear Default
        for i in sorted(self.play_movie, key=lambda x: x[1]):
            self.itemlist.append(xbmcgui.ListItem(u'{0} {1}'.format(self.addon.getLocalizedString(32061), self.players.get(i[0], {}).get('name', ''))))
            self.actions.append((True, self.players.get(i[0], {}).get('play_movie', '')))
        for i in sorted(self.search_movie, key=lambda x: x[1]):
            self.itemlist.append(xbmcgui.ListItem(u'{0} {1}' .format(xbmc.getLocalizedString(137), self.players.get(i[0], {}).get('name', ''))))
            self.actions.append((False, self.players.get(i[0], {}).get('search_movie', '')))
        for i in sorted(self.play_episode, key=lambda x: x[1]):
            self.itemlist.append(xbmcgui.ListItem(u'{0} {1}'.format(self.addon.getLocalizedString(32061), self.players.get(i[0], {}).get('name', ''))))
            self.actions.append((True, self.players.get(i[0], {}).get('play_episode', '')))
        for i in sorted(self.search_episode, key=lambda x: x[1]):
            self.itemlist.append(xbmcgui.ListItem(u'{0} {1}'.format(xbmc.getLocalizedString(137), self.players.get(i[0], {}).get('name', ''))))
            self.actions.append((False, self.players.get(i[0], {}).get('search_episode', '')))

    def playfile(self, file):
        if not file:
            return
        if file.endswith('.strm'):
            f = xbmcvfs.File(file)
            contents = f.read()
            f.close()
            if contents.startswith('plugin://plugin.video.themoviedb.helper'):
                return
        xbmc.executebuiltin(u'PlayMedia({0})'.format(file))
        return file

    def playmovie(self):
        fuzzy_match = self.addon.getSettingBool('fuzzymatch_movie')
        return self.playfile(KodiLibrary(dbtype='movie').get_info('file', fuzzy_match=fuzzy_match, **self.item))

    def playepisode(self):
        fuzzy_match = self.addon.getSettingBool('fuzzymatch_tv')
        fuzzy_match = True  # TODO: Get tvshow year to match against but for now force fuzzy match
        dbid = KodiLibrary(dbtype='tvshow').get_info('dbid', fuzzy_match=fuzzy_match, **self.item)
        return self.playfile(KodiLibrary(dbtype='episode', tvshowid=dbid).get_info('file', season=self.season, episode=self.episode))
