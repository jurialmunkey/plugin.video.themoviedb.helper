from xbmcplugin import addDirectoryItem, setProperty, setPluginCategory, setContent, endOfDirectory
from resources.lib.addon.consts import NO_LABEL_FORMATTING, RANDOMISED_TRAKT, RANDOMISED_LISTS, TRAKT_LIST_OF_LISTS, TMDB_BASIC_LISTS, TRAKT_BASIC_LISTS, TRAKT_SYNC_LISTS, ROUTE_NO_ID, ROUTE_TMDB_ID
from resources.lib.addon.plugin import convert_type, get_setting, executebuiltin
from resources.lib.addon.parser import try_int, split_items, merge_two_dicts, is_excluded
from resources.lib.addon.thread import ParallelThread
from resources.lib.api.tmdb.api import TMDb
from resources.lib.api.tmdb.lists import TMDbLists
from resources.lib.api.tmdb.search import SearchLists
from resources.lib.api.tmdb.discover import UserDiscoverLists
from resources.lib.api.trakt.api import TraktAPI
from resources.lib.api.trakt.lists import TraktLists
from resources.lib.api.fanarttv.api import FanartTV
from resources.lib.api.omdb.api import OMDb
from resources.lib.items.trakt import TraktMethods
from resources.lib.items.builder import ItemBuilder
from resources.lib.items.basedir import BaseDirLists
from resources.lib.addon.logger import kodi_log, TimerList, log_timer_report
from threading import Thread

""" Lazyimports """
from resources.lib.addon.modimp import lazyimport_module, lazyimport
random = None
KodiDb = None  # from resources.lib.items.kodi import KodiDb


PREBUILD_PARENTSHOW = ['seasons', 'episodes', 'episode_groups', 'trakt_upnext', 'episode_group_seasons']


class Container(TMDbLists, BaseDirLists, SearchLists, UserDiscoverLists, TraktLists):
    def __init__(self, handle, paramstring, **kwargs):
        # plugin:// params configuration
        self.handle = handle  # plugin:// handle
        self.paramstring = paramstring  # plugin://plugin.video.themoviedb.helper?paramstring
        self.params = kwargs  # paramstring dictionary
        self.parent_params = self.params.copy()  # TODO: CLEANUP
        self.is_widget = self.params.pop('widget', '').lower() == 'true'
        self.is_cacheonly = self.params.pop('cacheonly', '').lower() == 'true'
        self.is_fanarttv = self.params.pop('fanarttv', '').lower()
        self.is_nextpage = self.params.pop('nextpage', '').lower() != 'false'
        self.filters = {
            'filter_key': self.params.get('filter_key', None),
            'filter_value': split_items(self.params.get('filter_value', None))[0],
            'exclude_key': self.params.get('exclude_key', None),
            'exclude_value': split_items(self.params.get('exclude_value', None))[0]
        }

        # endOfDirectory
        self.update_listing = False  # endOfDirectory(updateListing=) set True to replace current path
        self.plugin_category = ''  # Container.PluginCategory / ListItem.Property(widget)
        self.container_content = ''  # Container.Content({})
        self.container_update = ''  # Add path to call Containr.Update({}) at end of directory
        self.container_refresh = False  # True call Container.Refresh at end of directory
        self.library = None  # TODO: FIX -- Currently broken -- SetInfo(library, info)

        # KodiDB
        self.kodi_db = None

        # API class initialisation
        self.ib = None
        self.tmdb_api = TMDb(delay_write=True)
        self.trakt_api = TraktAPI(delay_write=True)
        self.omdb_api = OMDb(delay_write=True) if get_setting('omdb_apikey', 'str') else None
        self.ftv_api = FanartTV(cache_only=self.ftv_is_cache_only(), delay_write=True)

        # Log Settings
        self.log_timers = get_setting('timer_reports')
        self.timer_lists = {}

        # Trakt Watched Progress Settings
        self.hide_watched = get_setting('widgets_hidewatched') if self.is_widget else False
        self.trakt_method = TraktMethods(
            trakt=self.trakt_api,
            watchedindicators=get_setting('trakt_watchedindicators'),
            pauseplayprogress=get_setting('trakt_playprogress'),
            unwatchedepisodes=get_setting('trakt_watchedinprogress'))

        # Miscellaneous
        self.nodate_is_unaired = get_setting('nodate_is_unaired')  # Consider items with no date to be
        self.tmdb_cache_only = self.tmdb_is_cache_only()
        self.pagination = self.pagination_is_allowed()
        self.thumb_override = 0

    def pagination_is_allowed(self):
        if not self.is_nextpage:  # nextpage=false param overrides all other settings
            return False
        if self.is_widget and not get_setting('widgets_nextpage'):
            return False
        return True

    def ftv_is_cache_only(self):
        if self.is_cacheonly:  # cacheonly=true param overrides all other settings
            return True
        if self.is_fanarttv == 'true':
            return False
        if self.is_fanarttv == 'false':
            return True
        if self.is_widget and get_setting('widget_fanarttv_lookup'):  # user settings
            return False
        if not self.is_widget and get_setting('fanarttv_lookup'):  # user setting
            return False
        return True

    def tmdb_is_cache_only(self):
        if self.is_cacheonly:  # cacheonly=true param overrides all other settings
            return True
        if not self.ftv_is_cache_only():  # fanarttv lookups require TMDb lookups for tvshow ID -- TODO: only force on tvshows
            return False
        if get_setting('tmdb_details'):  # user setting
            return False
        return True

    def get_kodi_database(self, tmdb_type):
        if not get_setting('local_db'):
            return
        lazyimport(globals(), 'resources.lib.items.kodi', import_attr='KodiDb')
        return KodiDb(tmdb_type)

    def _add_item(self, i, pagination=True):
        if not pagination and 'next_page' in i:
            return
        with TimerList(self.timer_lists, 'item_api', log_threshold=0.05, logging=self.log_timers):
            return self.ib.get_listitem(i)

    def _make_item(self, li):
        if not li:
            return
        if not li.next_page and is_excluded(li, is_listitem=True, **self.filters):
            return

        # Reformat ListItem.Label for episodes to match Kodi default 1x01.Title
        # Check if unaired and either apply special formatting or hide item depending on user settings
        li.set_episode_label()
        if self.format_episode_labels and not li.infoproperties.get('specialseason'):
            if li.is_unaired(no_date=self.nodate_is_unaired):
                return

        try:  # Add details from Kodi library
            li.set_details(details=self.kodi_db.get_kodi_details(li), reverse=True)
        except AttributeError:
            pass

        # Add Trakt playcount and watched status
        li.set_playcount(playcount=self.trakt_method.get_playcount(li))
        if self.hide_watched and try_int(li.infolabels.get('playcount')) != 0:
            return

        li.set_context_menu()  # Set the context menu items
        li.set_uids_to_info()  # Add unique ids to properties so accessible in skins
        li.set_thumb_to_art(self.thumb_override == 2) if self.thumb_override else None  # Special override for calendars to prevent thumb spoilers
        li.set_params_reroute(self.is_fanarttv, self.params.get('extended'), self.is_cacheonly)  # Reroute details to proper end point
        li.set_params_to_info(self.plugin_category)  # Set path params to properties for use in skins
        li.infoproperties.update(self.property_params or {})
        if self.thumb_override:
            li.infolabels.pop('dbid', None)  # Need to pop the DBID if overriding thumb to prevent Kodi overwriting
        if li.next_page:
            li.params['plugin_category'] = self.plugin_category  # Carry the plugin category to next page in plugin:// path
        self.trakt_method.set_playprogress(li)
        return {'url': li.get_url(), 'listitem': li.get_listitem(), 'isFolder': li.is_folder}

    def add_items(self, items=None, pagination=True, property_params=None, kodi_db=None):
        if not items:
            return

        # Setup ItemBuilder
        self.ib = ItemBuilder(
            tmdb_api=self.tmdb_api, ftv_api=self.ftv_api, trakt_api=self.trakt_api,
            delay_write=True, cache_only=self.tmdb_cache_only)
        self.ib.timer_lists = self.ib._cache._timers = self.timer_lists
        self.ib.log_timers = self.log_timers

        # Prebuild parent show details
        if self.parent_params.get('info') in PREBUILD_PARENTSHOW:
            self.ib.get_parents(
                tmdb_type='tv', tmdb_id=self.parent_params.get('tmdb_id'),
                season=self.parent_params.get('season', None) if self.parent_params['info'] == 'episodes' else None)

        # Build items in threadss
        with TimerList(self.timer_lists, '--build', log_threshold=0.05, logging=self.log_timers):
            self.ib.parent_params = self.parent_params
            with ParallelThread(items, self._add_item, pagination) as pt:
                item_queue = pt.queue
            all_listitems = [i for i in item_queue if i]

        # Finalise listitems in parallel threads
        self._pre_sync.join()
        with TimerList(self.timer_lists, '--make', log_threshold=0.05, logging=self.log_timers):
            self.property_params = property_params
            self.format_episode_labels = self.parent_params.get('info') not in NO_LABEL_FORMATTING
            with ParallelThread(all_listitems, self._make_item) as pt:
                item_queue = pt.queue
            all_itemtuples = [i for i in item_queue if i]
            # Add items to directory
            for i in all_itemtuples:
                addDirectoryItem(handle=self.handle, **i)

    def set_params_to_container(self, **kwargs):
        params = {}
        for k, v in kwargs.items():
            if not k or not v:
                continue
            try:
                k = f'Param.{k}'
                v = f'{v}'
                params[k] = v
                setProperty(self.handle, k, v)  # Set params to container properties
            except Exception as exc:
                kodi_log(f'Error: {exc}\nUnable to set param {k} to {v}', 1)
        return params

    def finish_container(self, update_listing=False, plugin_category='', container_content=''):
        setPluginCategory(self.handle, plugin_category)  # Container.PluginCategory
        setContent(self.handle, container_content)  # Container.Content
        endOfDirectory(self.handle, updateListing=update_listing)

    def get_container_content(self, tmdb_type, season=None, episode=None):
        if tmdb_type == 'tv' and season and episode:
            return convert_type('episode', 'container')
        elif tmdb_type == 'tv' and season:
            return convert_type('season', 'container')
        return convert_type(tmdb_type, 'container')

    def list_randomised_trakt(self, **kwargs):
        kwargs['info'] = RANDOMISED_TRAKT.get(kwargs.get('info'), {}).get('info')
        kwargs['randomise'] = True
        self.parent_params = kwargs
        return self.get_items(**kwargs)

    @lazyimport_module(globals(), 'random')
    def list_randomised(self, **kwargs):
        def random_from_list(i, remove_next_page=True):
            if not i or not isinstance(i, list) or len(i) < 2:
                return
            item = random.choice(i)
            if remove_next_page and isinstance(item, dict) and 'next_page' in item:
                return random_from_list(i, remove_next_page=True)
            return item
        params = merge_two_dicts(kwargs, RANDOMISED_LISTS.get(kwargs.get('info'), {}).get('params'))
        item = random_from_list(self.get_items(**params))
        if not item:
            return
        self.plugin_category = f'{item.get("label")}'
        self.parent_params = item.get('params', {})
        return self.get_items(**item.get('params', {}))

    def get_tmdb_id(self, info, **kwargs):
        if info == 'collection':
            kwargs['tmdb_type'] = 'collection'
        return self.tmdb_api.get_tmdb_id(**kwargs)

    def _noop(self):
        return None

    def _get_items(self, func, **kwargs):
        return func['lambda'](getattr(self, func['getattr']), **kwargs)

    def get_items(self, **kwargs):
        info = kwargs.get('info')

        # Check routes that don't require ID lookups first
        route = ROUTE_NO_ID
        route.update(TRAKT_LIST_OF_LISTS)
        route.update(RANDOMISED_LISTS)
        route.update(RANDOMISED_TRAKT)

        # Early exit if we have a route
        if info in route:
            return self._get_items(route[info]['route'], **kwargs)

        # Check routes that require ID lookups second
        route = ROUTE_TMDB_ID
        route.update(TMDB_BASIC_LISTS)
        route.update(TRAKT_BASIC_LISTS)
        route.update(TRAKT_SYNC_LISTS)

        # Early exit to basedir if no route found
        if info not in route:
            return self.list_basedir(info)

        # Lookup up our TMDb ID
        if not kwargs.get('tmdb_id'):
            self.parent_params['tmdb_id'] = self.params['tmdb_id'] = kwargs['tmdb_id'] = self.get_tmdb_id(**kwargs)

        return self._get_items(route[info]['route'], **kwargs)

    def get_directory(self):
        with TimerList(self.timer_lists, 'total', logging=self.log_timers):
            self._pre_sync = Thread(target=self.trakt_method.pre_sync, kwargs=self.params)
            self._pre_sync.start()
            with TimerList(self.timer_lists, 'get_list', logging=self.log_timers):
                items = self.get_items(**self.params)
            if not items:
                return
            self.plugin_category = self.params.get('plugin_category') or self.plugin_category
            with TimerList(self.timer_lists, 'add_items', logging=self.log_timers):
                self.add_items(
                    items,
                    pagination=self.pagination,
                    property_params=self.set_params_to_container(**self.params),
                    kodi_db=self.kodi_db)
            self.finish_container(
                update_listing=self.update_listing,
                plugin_category=self.plugin_category,
                container_content=self.container_content)
        if self.log_timers:
            log_timer_report(self.timer_lists, self.paramstring)
        if self.container_update:
            executebuiltin(f'Container.Update({self.container_update})')
        if self.container_refresh:
            executebuiltin('Container.Refresh')
