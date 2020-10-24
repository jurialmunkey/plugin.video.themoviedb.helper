import sys
import xbmc
import xbmcplugin
from resources.lib.helpers.constants import NO_LABEL_FORMATTING, RANDOMISED_TRAKT, RANDOMISED_LISTS, TRAKT_LIST_OF_LISTS, TMDB_BASIC_LISTS, TRAKT_BASIC_LISTS, TRAKT_SYNC_LISTS
from resources.lib.helpers.rpc import get_kodi_library, get_movie_details, get_tvshow_details, get_episode_details, get_season_details
from resources.lib.helpers.plugin import convert_type, TYPE_CONTAINER, reconfigure_legacy_params
from resources.lib.script.router import related_lists
from resources.lib.items.listitem import ListItem
from resources.lib.tmdb.api import TMDb
from resources.lib.trakt.api import TraktAPI
from resources.lib.fanarttv.api import FanartTV
from resources.lib.player.players import Players
from resources.lib.helpers.plugin import ADDON, kodi_log, ADDONPATH, viewitems
from resources.lib.items.basedir import BaseDirLists
from resources.lib.tmdb.lists import TMDbLists
from resources.lib.trakt.lists import TraktLists
from resources.lib.tmdb.search import SearchLists
from resources.lib.tmdb.discover import UserDiscoverLists
from resources.lib.helpers.parser import try_decode, parse_paramstring, try_int
from resources.lib.helpers.setutils import split_items, random_from_list, merge_two_dicts


""" Container methods:
pagination_is_allowed   : Checks if pagination is allowed based upon settings and URI params
ftv_is_cache_only       : Checks if additional artwork should be looked-up on fanarttv
add_items               : Converts a list of item dicts into listitems and adds to container
set_params_to_container : Set the URI params to container properties for access via skin
finish_container        : Set plugin category, container content and end directory
item_is_excluded        : Checks if item should be included/excluded based on filter/exclusion key/values
get_tmdb_details        : Gets details about the listitem from TMDb API
                          Non-cached look-ups triggered by self.tmdb_cache_only=False passed to add_items method
get_ftv_artwork         : Gets artwork for the listitem from fanart.tv api
                          Non-cached look-ups triggered by ftv_is_cache_only() dependent on settings
get_playcount_from_trakt: Gets the relevant playcount/unaired/aired etc. values from Trakt API
                          Look-ups are dependent on settings
get_kodi_database       : Gets the kodi db details via JSON-RPC
get_kodi_parent_dbid    : Gets the kodi dbid for the parent item (e.g. tvshow dbid for episodes)
get_kodi_details        : Gets the kodi db details for the listitem
get_kodi_tvchild_details: Gets the details for a tvshow child item (e.g. episode details)
get_container_content   : Converts the TMDb type into a valid Kodi container content type
list_randomised_trakt   : Gets randomised items from a Trakt list
list_randomised         : Gets randomised lists
get_tmdb_id             : Converts a query in the params to a TMDb ID
get_items               : Routing function to get the items for the container based on params
get_directory           : Routing function to get items, add them and finish container based on params
play_external           : Send path to external players for playing
context_related         : Pop-up list of various related list options (replaced detailed item section)
router                  : Entry point router
"""


def filtered_item(item, key, value, exclude=False):
    boolean = False if exclude else True  # Flip values if we want to exclude instead of include
    if key and value and item.get(key) == value:
        boolean = exclude
    return boolean


class Container(TMDbLists, BaseDirLists, SearchLists, UserDiscoverLists, TraktLists):
    def __init__(self):
        self.handle = int(sys.argv[1])
        self.paramstring = try_decode(sys.argv[2][1:])
        self.params = parse_paramstring(sys.argv[2][1:])
        self.parent_params = self.params
        self.container_path = '{}{}'.format(sys.argv[0], sys.argv[2])
        self.update_listing = False
        self.plugin_category = ''
        self.container_content = ''
        self.container_update = None
        self.container_refresh = False
        self.item_type = None
        self.kodi_db = None
        self.kodi_db_tv = {}
        self.library = None
        self.tmdb_cache_only = True
        self.tmdb_api = TMDb()
        self.trakt_watchedindicators = ADDON.getSettingBool('trakt_watchedindicators')
        self.trakt_api = TraktAPI()
        self.is_widget = True if self.params.pop('widget', '').lower() == 'true' else False
        self.hide_watched = ADDON.getSettingBool('widgets_hidewatched') if self.is_widget else False
        self.flatten_seasons = ADDON.getSettingBool('flatten_seasons')
        self.ftv_forced_lookup = self.params.pop('fanarttv', '').lower()
        self.ftv_api = FanartTV(cache_only=self.ftv_is_cache_only())
        self.filter_key = self.params.pop('filter_key', None)
        self.filter_value = split_items(self.params.pop('filter_value', None))[0]
        self.exclude_key = self.params.pop('exclude_key', None)
        self.exclude_value = split_items(self.params.pop('exclude_value', None))[0]
        self.pagination = self.pagination_is_allowed()
        self.params = reconfigure_legacy_params(**self.params)

    def pagination_is_allowed(self):
        if self.params.pop('nextpage', '').lower() == 'false':
            return False
        if self.is_widget and not ADDON.getSettingBool('widgets_nextpage'):
            return False
        return True

    def ftv_is_cache_only(self):
        if self.ftv_forced_lookup == 'true':
            return False
        if self.ftv_forced_lookup == 'false':
            return True
        if self.is_widget and ADDON.getSettingBool('widget_fanarttv_lookup'):
            return False
        if not self.is_widget and ADDON.getSettingBool('fanarttv_lookup'):
            return False
        return True

    def add_items(self, items=None, pagination=True, parent_params=None, kodi_db=None, tmdb_cache_only=True):
        if not items:
            return
        check_is_aired = parent_params.get('info') not in NO_LABEL_FORMATTING
        for i in items:
            if not pagination and 'next_page' in i:
                continue
            if self.item_is_excluded(i):
                continue
            li = ListItem(parent_params=parent_params, **i)
            li.set_details(details=self.get_tmdb_details(li, cache_only=tmdb_cache_only))  # Quick because only get cached
            li.set_episode_label()
            if check_is_aired and li.is_unaired():
                continue
            li.set_details(details=self.get_ftv_artwork(li), reverse=True)  # Slow when not cache only
            li.set_details(details=self.get_kodi_details(li), reverse=True)  # Quick because local db
            li.set_playcount(playcount=self.get_playcount_from_trakt(li))  # Quick because of agressive caching of Trakt object and pre-emptive dict comprehension
            if self.hide_watched and try_int(li.infolabels.get('playcount')) != 0:
                continue
            li.set_context_menu()  # Set the context menu items
            li.set_uids_to_info()  # Add unique ids to properties so accessible in skins
            li.set_params_reroute(self.ftv_forced_lookup, self.flatten_seasons)  # Reroute details to proper end point
            li.set_params_to_info(self.plugin_category)  # Set path params to properties for use in skins
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=li.get_url(),
                listitem=li.get_listitem(),
                isFolder=li.is_folder)

    def set_params_to_container(self, **kwargs):
        for k, v in viewitems(kwargs):
            if not k or not v:
                continue
            try:
                xbmcplugin.setProperty(self.handle, u'Param.{}'.format(k), u'{}'.format(v))  # Set params to container properties
            except Exception as exc:
                kodi_log(u'Error: {}\nUnable to set Param.{} to {}'.format(exc, k, v), 1)

    def finish_container(self, update_listing=False, plugin_category='', container_content=''):
        xbmcplugin.setPluginCategory(self.handle, plugin_category)  # Container.PluginCategory
        xbmcplugin.setContent(self.handle, container_content)  # Container.Content
        xbmcplugin.endOfDirectory(self.handle, updateListing=update_listing)

    def item_is_excluded(self, item):
        if self.filter_key and self.filter_value:
            if self.filter_key in item.get('infolabels', {}):
                if filtered_item(item['infolabels'], self.filter_key, self.filter_value):
                    return True
            elif self.filter_key in item.get('infoproperties', {}):
                if filtered_item(item['infoproperties'], self.filter_key, self.filter_value):
                    return True
        if self.exclude_key and self.exclude_value:
            if self.exclude_key in item.get('infolabels', {}):
                if filtered_item(item['infolabels'], self.exclude_key, self.exclude_value, True):
                    return True
            elif self.exclude_key in item.get('infoproperties', {}):
                if filtered_item(item['infoproperties'], self.exclude_key, self.exclude_value, True):
                    return True

    def get_tmdb_details(self, li, cache_only=True):
        if not self.tmdb_api:
            return
        return self.tmdb_api.get_details(
            li.get_tmdb_type(),
            li.unique_ids.get('tvshow.tmdb') if li.infolabels.get('mediatype') == 'episode' else li.unique_ids.get('tmdb'),
            li.infolabels.get('season') if li.infolabels.get('mediatype') in ['season', 'episode'] else None,
            li.infolabels.get('episode') if li.infolabels.get('mediatype') == 'episode' else None,
            cache_only=cache_only)

    def get_ftv_artwork(self, li):
        if not self.ftv_api:
            return
        artwork = self.ftv_api.get_all_artwork(li.get_ftv_id(), li.get_ftv_type())
        if not artwork:
            return
        if li.infolabels.get('mediatype') in ['season', 'episode']:
            artwork = {u'tvshow.{}'.format(k): v for k, v in viewitems(artwork) if v}
        return {'art': artwork}

    def get_playcount_from_trakt(self, li):
        if not self.trakt_watchedindicators:
            return
        if li.infolabels.get('mediatype') == 'movie':
            return self.trakt_api.get_movie_playcount(
                id_type='tmdb',
                unique_id=try_int(li.unique_ids.get('tmdb')))
        if li.infolabels.get('mediatype') == 'episode':
            return self.trakt_api.get_episode_playcount(
                id_type='tmdb',
                unique_id=try_int(li.unique_ids.get('tvshow.tmdb')),
                season=li.infolabels.get('season'),
                episode=li.infolabels.get('episode'))
        if li.infolabels.get('mediatype') == 'tvshow':
            li.infolabels['episode'] = self.trakt_api.get_episodes_airedcount(
                id_type='tmdb',
                unique_id=try_int(li.unique_ids.get('tmdb')))
            return self.trakt_api.get_episodes_watchcount(
                id_type='tmdb',
                unique_id=try_int(li.unique_ids.get('tmdb')))
        if li.infolabels.get('mediatype') == 'season':
            li.infolabels['episode'] = self.trakt_api.get_episodes_airedcount(
                id_type='tmdb',
                unique_id=try_int(li.unique_ids.get('tmdb')),
                season=li.infolabels.get('season'))
            return self.trakt_api.get_episodes_watchcount(
                id_type='tmdb',
                unique_id=try_int(li.unique_ids.get('tmdb')),
                season=li.infolabels.get('season'))

    def get_kodi_database(self, tmdb_type):
        if ADDON.getSettingBool('local_db'):
            return get_kodi_library(tmdb_type)

    def get_kodi_parent_dbid(self, li):
        if not self.kodi_db:
            return
        if li.infolabels.get('mediatype') in ['movie', 'tvshow']:
            return self.kodi_db.get_info(
                info='dbid',
                imdb_id=li.unique_ids.get('imdb'),
                tmdb_id=li.unique_ids.get('tmdb'),
                tvdb_id=li.unique_ids.get('tvdb'),
                originaltitle=li.infolabels.get('originaltitle'),
                title=li.infolabels.get('title'),
                year=li.infolabels.get('year'))
        if li.infolabels.get('mediatype') in ['season', 'episode']:
            return self.kodi_db.get_info(
                info='dbid',
                imdb_id=li.unique_ids.get('tvshow.imdb'),
                tmdb_id=li.unique_ids.get('tvshow.tmdb'),
                tvdb_id=li.unique_ids.get('tvshow.tvdb'),
                title=li.infolabels.get('tvshowtitle'))

    def get_kodi_details(self, li):
        if not self.kodi_db:
            return
        dbid = self.get_kodi_parent_dbid(li)
        if not dbid:
            return
        if li.infolabels.get('mediatype') == 'movie':
            return get_movie_details(dbid)
        if li.infolabels.get('mediatype') == 'tvshow':
            return get_tvshow_details(dbid)
        if li.infolabels.get('mediatype') == 'season':
            return self.get_kodi_tvchild_details(
                tvshowid=dbid,
                season=li.infolabels.get('season'),
                is_season=True)
        if li.infolabels.get('mediatype') == 'episode':
            return self.get_kodi_tvchild_details(
                tvshowid=dbid,
                season=li.infolabels.get('season'),
                episode=li.infolabels.get('episode'))

    def get_kodi_tvchild_details(self, tvshowid, season=None, episode=None, is_season=False):
        if not tvshowid or not season or (not episode and not is_season):
            return
        library = 'season' if is_season else 'episode'
        self.kodi_db_tv[tvshowid] = self.kodi_db_tv.get(tvshowid) or get_kodi_library(library, tvshowid)
        if not self.kodi_db_tv[tvshowid].database:
            return
        dbid = self.kodi_db_tv[tvshowid].get_info('dbid', season=season, episode=episode)
        if not dbid:
            return
        details = get_season_details(dbid) if is_season else get_episode_details(dbid)
        details['infoproperties']['tvshow.dbid'] = tvshowid
        return details

    def get_container_content(self, tmdb_type, season=None, episode=None):
        if tmdb_type == 'tv' and season and episode:
            return convert_type('episode', TYPE_CONTAINER)
        elif tmdb_type == 'tv' and season:
            return convert_type('season', TYPE_CONTAINER)
        return convert_type(tmdb_type, TYPE_CONTAINER)

    def list_randomised_trakt(self, **kwargs):
        kwargs['info'] = RANDOMISED_TRAKT.get(kwargs.get('info'))
        kwargs['randomise'] = True
        self.parent_params = kwargs
        return self.get_items(**kwargs)

    def list_randomised(self, **kwargs):
        params = merge_two_dicts(
            kwargs, RANDOMISED_LISTS.get(kwargs.get('info')))
        item = random_from_list(self.get_items(**params))
        if not item:
            return
        self.plugin_category = item.get('label')
        return self.get_items(**item.get('params', {}))

    def get_tmdb_id(self, info, **kwargs):
        if info == 'collection':
            kwargs['tmdb_type'] = 'collection'
        return self.tmdb_api.get_tmdb_id(**kwargs)

    def get_items(self, **kwargs):
        info = kwargs.get('info')
        if info == 'pass':
            return
        if info == 'dir_search':
            return self.list_searchdir_router(**kwargs)
        if info == 'search':
            return self.list_search(**kwargs)
        if info == 'user_discover':
            return self.list_userdiscover(**kwargs)
        if info == 'dir_discover':
            return self.list_discoverdir_router(**kwargs)
        if info == 'discover':
            return self.list_discover(**kwargs)
        if info == 'all_items':
            return self.list_all_items(**kwargs)
        if info == 'trakt_userlist':
            return self.list_userlist(**kwargs)
        if info in ['trakt_becauseyouwatched', 'trakt_becausemostwatched']:
            return self.list_becauseyouwatched(**kwargs)
        if info == 'trakt_inprogress':
            return self.list_inprogress(**kwargs)
        if info == 'trakt_nextepisodes':
            return self.list_nextepisodes(**kwargs)
        if info == 'trakt_calendar':
            return self.list_trakt_calendar(**kwargs)
        if info == 'library_nextaired':
            return self.list_trakt_calendar(library=True, **kwargs)
        if info in TRAKT_LIST_OF_LISTS:
            return self.list_lists(**kwargs)
        if info in RANDOMISED_LISTS:
            return self.list_randomised(**kwargs)
        if info in RANDOMISED_TRAKT:
            return self.list_randomised_trakt(**kwargs)
        if info == 'trakt_sortby':
            return self.list_trakt_sortby(**kwargs)

        if info and not kwargs.get('tmdb_id'):
            kwargs['tmdb_id'] = self.get_tmdb_id(**kwargs)

        if info == 'details':
            return self.list_details(**kwargs)
        if info == 'seasons':
            return self.list_seasons(**kwargs)
        if info == 'flatseasons':
            return self.list_flatseasons(**kwargs)
        if info == 'episodes':
            return self.list_episodes(**kwargs)
        if info == 'cast':
            return self.list_cast(**kwargs)
        if info == 'crew':
            return self.list_crew(**kwargs)
        if info == 'trakt_upnext':
            return self.list_upnext(**kwargs)
        if info in TMDB_BASIC_LISTS:
            return self.list_tmdb(**kwargs)
        if info in TRAKT_BASIC_LISTS:
            return self.list_trakt(**kwargs)
        if info in TRAKT_SYNC_LISTS:
            return self.list_sync(**kwargs)
        return self.list_basedir(info)

    def get_directory(self):
        items = self.get_items(**self.params)
        if not items:
            return
        self.add_items(
            items,
            pagination=self.pagination,
            parent_params=self.parent_params,
            kodi_db=self.kodi_db,
            tmdb_cache_only=self.tmdb_cache_only)
        self.finish_container(
            update_listing=self.update_listing,
            plugin_category=self.plugin_category,
            container_content=self.container_content)
        self.set_params_to_container(**self.params)
        if self.container_update:
            xbmc.executebuiltin('Container.Update({})'.format(self.container_update))
        if self.container_refresh:
            xbmc.executebuiltin('Container.Refresh')

    def play_external(self, **kwargs):
        """
        Kodi does 5x retries to resolve url if isPlayable property is set
        Since our external players might not return resolvable files we don't use this method
        Instead we pass url to xbmc.Player() or PlayMedia() or ActivateWindow() depending on context
        However, is playable is forced for strm so set a dummy file and stop it immediately
        TMDbHelper sets an islocal flag in its strm files so we can determine what called play
        """
        if kwargs.get('islocal', False):
            xbmcplugin.setResolvedUrl(self.handle, True, ListItem(
                path='{}/resources/dummy.mp4'.format(ADDONPATH)).get_listitem())
            xbmc.executebuiltin('Action(Stop)')

        if not kwargs.get('tmdb_id'):
            kwargs['tmdb_id'] = self.tmdb_api.get_tmdb_id(**kwargs)

        kodi_log(['Attempting to play:\n', kwargs], 1)

        Players(**kwargs).play()

    def context_related(self, **kwargs):
        if not kwargs.get('tmdb_id'):
            kwargs['tmdb_id'] = self.tmdb_api.get_tmdb_id(**kwargs)
        kwargs['container_update'] = True
        related_lists(**kwargs)

    def router(self):
        if self.params.get('info') == 'play':
            return self.play_external(**self.params)
        if self.params.get('info') == 'related':
            return self.context_related(**self.params)
        return self.get_directory()
