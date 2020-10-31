import xbmc
import xbmcgui
from resources.lib.helpers.constants import ACCEPTED_MEDIATYPES
from resources.lib.helpers.plugin import ADDON, ADDONPATH, PLUGINPATH, kodi_log, viewitems
from resources.lib.helpers.parser import try_int, encode_url
from resources.lib.helpers.timedate import is_future_timestamp
from resources.lib.helpers.setutils import merge_two_dicts
from json import dumps
# from resources.lib.helpers.decorators import timer_report


""" ListItem methods:
_set_as_next_page   : Internal method to set next page item
set_art_fallbacks   : Set a default fallback thumb and fanart if not already set
get_trakt_type      : Gets Trakt type based on ListItem.DBType
get_tmdb_type       : Gets TMDb type based on ListItem.DBType
get_ftv_type        : Gets Fanart.tv type based on ListItem.DBType
get_ftv_id          : Gets the correct unique ID needed for Fanart.tv lookups based on ListItem.DBType
get_tmdb_id         : Gets the correct TMDb  (tmdb or tvshow.tmdb) for TMDb lookups based on ListItem.DBType
is_unaired          : Checks if the premiered date is in the future and formats label if it is
set_context_menu    : Sets default context menu items (related, trakt, artwork, refresh)
set_playcount       : Sets passed playcount value appropriately based on ListItem.DBType
set_params_reroute  : Sets rerouted params based on certain conditions
set_episode_label   : Sets the episode label to match Kodi default of "1x01. Title"
set_uids_to_info    : Sets all the unique id values to ListItem.Property(uid) for skin access
get_url             : Encodes the listitem params into a Kodi plugin paramstring URI
get_listitem        : Creates and returns an xbmcgui.ListItem object from the info dicts
"""


class ListItem(object):
    def __init__(
            self, label=None, label2=None, path=None, library=None, is_folder=True, params=None, next_page=None,
            parent_params=None, infolabels=None, infoproperties=None, art=None, cast=None,
            context_menu=None, stream_details=None, unique_ids=None,
            **kwargs):
        self.label = label or ''
        self.label2 = label2 or ''
        self.path = path or PLUGINPATH
        self.params = params or {}
        self.parent_params = parent_params or {}
        self.library = library or 'video'
        self.is_folder = is_folder
        self.infolabels = infolabels or {}
        self.infoproperties = infoproperties or {}
        self.art = art or {}
        self.cast = cast or []
        self.context_menu = context_menu or []
        self.stream_details = stream_details or {}
        self.unique_ids = unique_ids or {}
        self._set_as_next_page(next_page)

    def _set_as_next_page(self, next_page=None):
        if not next_page:
            return
        self.label = xbmc.getLocalizedString(33078)
        self.art['thumb'] = '{}/resources/icons/tmdb/nextpage.png'.format(ADDONPATH)
        self.art['landscape'] = '{}/resources/icons/tmdb/nextpage_wide.png'.format(ADDONPATH)
        self.infoproperties['specialsort'] = 'bottom'
        self.params = self.parent_params.copy()
        self.params['page'] = next_page
        self.params.pop('update_listing', None)  # Just in case we updated the listing for search results
        self.path = PLUGINPATH
        self.is_folder = True

    def set_art_fallbacks(self):
        if not self.art.get('thumb'):
            self.art['thumb'] = '{}/resources/poster.png'.format(ADDONPATH)
        if not self.art.get('fanart'):
            self.art['fanart'] = '{}/fanart.jpg'.format(ADDONPATH)
        return self.art

    def get_trakt_type(self):
        if self.infolabels.get('mediatype') == 'movie':
            return 'movie'
        if self.infolabels.get('mediatype') == 'tvshow':
            return 'show'
        if self.infolabels.get('mediatype') == 'season':
            return 'season'
        if self.infolabels.get('mediatype') == 'episode':
            return 'episode'

    def get_tmdb_type(self):
        if self.infolabels.get('mediatype') == 'movie':
            return 'movie'
        if self.infolabels.get('mediatype') in ['tvshow', 'season', 'episode']:
            return 'tv'
        if self.infoproperties.get('tmdb_type') == 'person':
            return 'person'

    def get_ftv_type(self):
        if self.infolabels.get('mediatype') == 'movie':
            return 'movies'
        if self.infolabels.get('mediatype') in ['tvshow', 'season', 'episode']:
            return 'tv'

    def get_ftv_id(self):
        if self.infolabels.get('mediatype') == 'movie':
            return self.unique_ids.get('tmdb')
        if self.infolabels.get('mediatype') == 'tvshow':
            return self.unique_ids.get('tvdb')
        if self.infolabels.get('mediatype') in ['season', 'episode']:
            return self.unique_ids.get('tvshow.tvdb')

    def get_tmdb_id(self):
        if self.infolabels.get('mediatype') in ['season', 'episode']:
            return self.unique_ids.get('tvshow.tmdb')
        return self.unique_ids.get('tmdb')

    def is_unaired(self, format_label=u'[COLOR=ffcc0000][I]{}[/I][/COLOR]', check_hide_settings=True):
        if not self.infolabels.get('mediatype') in ['movie', 'tvshow', 'season', 'episode']:
            return
        try:
            if is_future_timestamp(self.infolabels.get('premiered'), "%Y-%m-%d", 10):
                if format_label:
                    self.label = format_label.format(self.label)
                if not check_hide_settings:
                    return True
                elif self.infolabels.get('mediatype') == 'movie':
                    if ADDON.getSettingBool('hide_unaired_movies'):
                        return True
                elif self.infolabels.get('mediatype') in ['tv', 'season', 'episode']:
                    if ADDON.getSettingBool('hide_unaired_episodes'):
                        return True
        except Exception as exc:
            kodi_log(u'Error: {}'.format(exc), 1)

    def _context_item_get_ftv_artwork(self):
        if self.infolabels.get('mediatype') not in ['movie', 'tvshow']:
            return []
        ftv_id, ftv_type = self.get_ftv_id(), self.get_ftv_type()
        if not ftv_type or not ftv_id:
            return []
        return [('tmdbhelper.context.artwork', dumps({'ftv_type': ftv_type, 'ftv_id': ftv_id}))]

    def _context_item_refresh_details(self):
        tmdb_id, tmdb_type = self.get_tmdb_id(), self.get_tmdb_type()
        if not tmdb_type or not tmdb_id:
            return []
        params = {'tmdb_type': tmdb_type, 'tmdb_id': tmdb_id}
        if self.infolabels.get('mediatype') in ['season', 'episode']:
            params['season'] = self.infolabels.get('season', 0)
        if self.infolabels.get('mediatype') == 'episode':
            params['episode'] = self.infolabels.get('episode', 0)
        return [('tmdbhelper.context.refresh', dumps(params))]

    def _context_item_related_lists(self):
        tmdb_id, tmdb_type = self.get_tmdb_id(), self.get_tmdb_type()
        if not tmdb_type or not tmdb_id:
            return []
        params = {'tmdb_type': tmdb_type, 'tmdb_id': tmdb_id}
        if self.infolabels.get('mediatype') == 'episode':
            params['season'] = self.infolabels.get('season')
            params['episode'] = self.infolabels.get('episode')
        return [('tmdbhelper.context.related', dumps(params))]

    def _context_item_add_to_library(self):
        tmdb_id, tmdb_type = self.get_tmdb_id(), self.get_tmdb_type()
        if not tmdb_type or not tmdb_id or tmdb_type not in ['movie', 'tv']:
            return []
        params = {'tmdb_type': tmdb_type, 'tmdb_id': tmdb_id, 'imdb_id': self.unique_ids.get('imdb')}
        if tmdb_type == 'movie':
            params['folder'] = u'{} ({})'.format(self.infolabels.get('title', ''), self.infolabels.get('year', ''))
        elif tmdb_type == 'tv':
            params['folder'] = u'{}'.format(self.infolabels.get('title', ''))
        return [('tmdbhelper.context.addlibrary', dumps(params))]

    def _context_item_trakt_sync(self):
        tmdb_id, trakt_type = self.get_tmdb_id(), self.get_trakt_type()
        if not trakt_type or not tmdb_id:
            return []
        params = {'trakt_type': trakt_type, 'unique_id': tmdb_id, 'id_type': 'tmdb'}
        if self.infolabels.get('mediatype') == 'season':
            return []  # Seasons disabled for now as difficult to manage properly TODO: FIX IT!
        if self.infolabels.get('mediatype') == 'episode':
            params['season'] = self.infolabels.get('season')
            params['episode'] = self.infolabels.get('episode')
        return [('tmdbhelper.context.trakt', dumps(params))]

    def set_context_menu(self):
        context_items = []
        context_items += self._context_item_related_lists()
        context_items += self._context_item_get_ftv_artwork()
        context_items += self._context_item_refresh_details()
        context_items += self._context_item_trakt_sync()
        context_items += self._context_item_add_to_library()
        for k, v in context_items:
            self.infoproperties[k] = v

    def set_playcount(self, playcount):
        playcount = try_int(playcount)
        if self.infolabels.get('mediatype') in ['movie', 'episode']:
            if playcount:
                self.infolabels['playcount'] = playcount
                self.infolabels['overlay'] = 5
        elif self.infolabels.get('mediatype') in ['tvshow', 'season']:
            if try_int(self.infolabels.get('episode')):
                self.infoproperties['watchedepisodes'] = playcount
                self.infoproperties['totalepisodes'] = try_int(self.infolabels.get('episode'))
                self.infoproperties['unwatchedepisodes'] = self.infoproperties.get('totalepisodes') - try_int(self.infoproperties.get('watchedepisodes'))
                if playcount and not self.infoproperties.get('unwatchedepisodes'):
                    self.infolabels['playcount'] = playcount
                    self.infolabels['overlay'] = 5

    # @timer_report('set_details')
    def set_details(self, details=None, reverse=False):
        if not details:
            return
        self.stream_details = merge_two_dicts(details.get('stream_details', {}), self.stream_details, reverse=reverse)
        self.infolabels = merge_two_dicts(details.get('infolabels', {}), self.infolabels, reverse=reverse)
        self.infoproperties = merge_two_dicts(details.get('infoproperties', {}), self.infoproperties, reverse=reverse)
        self.art = merge_two_dicts(details.get('art', {}), self.art, reverse=reverse)
        self.unique_ids = merge_two_dicts(details.get('unique_ids', {}), self.unique_ids, reverse=reverse)
        self.cast = self.cast or details.get('cast', [])

    def set_params_reroute(self, ftv_forced_lookup=False, flatten_seasons=False):
        # Do some special stuff for skin shortcuts window like set widget pararm and provide sorting methods
        if xbmc.getCondVisibility("Window.IsVisible(script-skinshortcuts.xml)"):
            self.params['widget'] = 'true'
            if self.infoproperties.get('tmdbhelper.context.sorting'):
                self.params['parent_info'] = self.params['info']
                self.params['info'] = 'trakt_sortby'

        # If parent list had fanarttv param we should carry this with us onto following pages
        if ftv_forced_lookup:
            self.params['fanarttv'] = ftv_forced_lookup

        # Reconfigure various details sections to point to the correct places
        if self.params.get('info') == 'details':
            if self.infoproperties.get('tmdb_type') == 'person':
                self.params['info'] = 'related'
                self.params['tmdb_type'] = 'person'
                self.params['tmdb_id'] = self.unique_ids.get('tmdb')
                self.is_folder = False
            elif (self.parent_params.get('info') == 'library_nextaired'
                    and self.infolabels.get('mediatype') == 'episode'
                    and ADDON.getSettingBool('nextaired_linklibrary')
                    and self.infoproperties.get('tvshow.dbid')):
                self.path = 'videodb://tvshows/titles/{}/'.format(self.infoproperties['tvshow.dbid'])
                self.params = {}
                self.is_folder = True
            elif self.infolabels.get('mediatype') in ['movie', 'episode', 'video']:
                self.params['info'] = 'play'
                self.is_folder = False
                self.infoproperties['isPlayable'] = 'true'
                self.infoproperties['tmdbhelper.context.playusing'] = '{}&ignore_default=true'.format(self.get_url())
            elif self.infolabels.get('mediatype') == 'tvshow':
                self.params['info'] = 'flatseasons' if flatten_seasons else 'seasons'
            elif self.infolabels.get('mediatype') == 'season':
                self.params['info'] = 'episodes'
            elif self.infolabels.get('mediatype') == 'set':
                self.params['info'] = 'collection'

    def set_episode_label(self, format_label=u'{season}x{episode:0>2}. {label}'):
        if not self.infolabels.get('mediatype') == 'episode':
            return
        season = try_int(self.infolabels.get('season', 0))
        episode = try_int(self.infolabels.get('episode', 0))
        if not season or not episode:
            return
        self.label = format_label.format(season=season, episode=episode, label=self.infolabels.get('title', ''))

    def set_uids_to_info(self):
        for k, v in viewitems(self.unique_ids):
            if not v:
                continue
            self.infoproperties['{}_id'.format(k)] = v

    def set_params_to_info(self, widget=None):
        for k, v in viewitems(self.params):
            if not k or not v:
                continue
            self.infoproperties['item.{}'.format(k)] = v
        if self.params.get('tmdb_type'):
            self.infoproperties['item.type'] = self.params['tmdb_type']
        if widget:
            self.infoproperties['widget'] = widget

    def get_url(self):
        return encode_url(self.path, **self.params)

    def get_listitem(self):
        if self.infolabels.get('mediatype') not in ACCEPTED_MEDIATYPES:
            self.infolabels.pop('mediatype', None)
        listitem = xbmcgui.ListItem(label=self.label, label2=self.label2, path=self.get_url())
        listitem.setLabel2(self.label2)
        listitem.setInfo(self.library, self.infolabels)
        listitem.setArt(self.set_art_fallbacks())
        if self.library == 'pictures':
            return listitem
        listitem.setUniqueIDs(self.unique_ids)
        listitem.setProperties(self.infoproperties)
        listitem.setCast(self.cast)
        listitem.addContextMenuItems(self.context_menu)

        if self.stream_details:
            for k, v in viewitems(self.stream_details):
                if not k or not v:
                    continue
                for i in v:
                    if not i:
                        continue
                    listitem.addStreamInfo(k, i)

        return listitem
