from xbmcplugin import addDirectoryItems, setProperty, setPluginCategory, setContent, endOfDirectory, addSortMethod
from tmdbhelper.lib.addon.consts import NO_LABEL_FORMATTING
from tmdbhelper.lib.addon.plugin import get_setting, executebuiltin, get_localized, get_condvisibility
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.thread import ParallelThread
from tmdbhelper.lib.api.tmdb.api import TMDb
from tmdbhelper.lib.api.trakt.api import TraktAPI
from tmdbhelper.lib.api.fanarttv.api import FanartTV
from tmdbhelper.lib.api.omdb.api import OMDb
from tmdbhelper.lib.api.tvdb.api import TVDb
from tmdbhelper.lib.api.mdblist.api import MDbList
from tmdbhelper.lib.items.trakt import TraktMethods
from tmdbhelper.lib.items.builder import ItemBuilder
from tmdbhelper.lib.items.filters import is_excluded
from tmdbhelper.lib.addon.logger import TimerList, log_timer_report
from threading import Thread

""" Lazyimports
from tmdbhelper.lib.items.kodi import KodiDb
"""


class Container():
    def __init__(self, handle, paramstring, **kwargs):
        # Log Settings
        self.log_timers = get_setting('timer_reports')
        self.timer_lists = {}

        # plugin:// params configuration
        self.handle = handle  # plugin:// handle
        self.paramstring = paramstring  # plugin://plugin.video.themoviedb.helper?paramstring
        self.params = kwargs  # paramstring dictionary
        self.parent_params = self.params.copy()  # TODO: CLEANUP
        self.filters = {
            'filter_key': self.params.get('filter_key', None),
            'filter_value': self.params.get('filter_value', None),
            'filter_operator': self.params.get('filter_operator', None),
            'exclude_key': self.params.get('exclude_key', None),
            'exclude_value': self.params.get('exclude_value', None),
            'exclude_operator': self.params.get('exclude_operator', None)}

        self.is_widget = self.params.get('widget', '').lower() == 'true'
        self.is_cacheonly = self.params.get('cacheonly', '').lower() == 'true'
        self.is_fanarttv = self.params.get('fanarttv', '').lower()
        self.is_detailed = self.params.get('detailed', '').lower() == 'true' or self.params.get('info') == 'details'

        self.context_additions = None if self.is_widget else [(get_localized(32496), 'RunScript(plugin.video.themoviedb.helper,make_node)')]

        # endOfDirectory
        self.update_listing = False  # endOfDirectory(updateListing=) set True to replace current path
        self.plugin_category = ''  # Container.PluginCategory / ListItem.Property(widget)
        self.container_content = ''  # Container.Content({})
        self.container_update = ''  # Add path to call Containr.Update({}) at end of directory
        self.container_refresh = False  # True call Container.Refresh at end of directory
        self.library = None  # TODO: FIX -- Currently broken -- SetInfo(library, info)
        self.sort_methods = []  # List of kwargs dictionaries [{'sortMethod': SORT_METHOD_UNSORTED}]
        self.sort_by_dbid = False

        # KodiDB
        self.kodi_db = None

        # API class initialisation
        self.tmdb_api = TMDb(page_length=self.page_length)
        self.omdb_api = OMDb() if get_setting('omdb_apikey', 'str') else None
        self.ftv_api = FanartTV(cache_only=self.ftv_is_cache_only(), )
        self.trakt_api = TraktAPI(page_length=self.page_length)
        self.mdblist_api = MDbList()
        self.tvdb_api = TVDb()
        self.ib = ItemBuilder(
            tmdb_api=self.tmdb_api, ftv_api=self.ftv_api, trakt_api=self.trakt_api,
            log_timers=self.log_timers, timer_lists=self.timer_lists)

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

    @property
    def page_length(self):
        if self.is_widget or not get_condvisibility('Window.IsVisible(MyVideoNav.xml)'):
            return 1
        return get_setting('pagemulti_library', 'int')

    def pagination_is_allowed(self):
        if self.params.get('nextpage', '').lower() == 'false':
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
        with TimerList(self.timer_lists, 'get_kodi', log_threshold=0.05, logging=self.log_timers):
            if not get_setting('local_db'):
                return
            from tmdbhelper.lib.items.kodi import KodiDb
            return KodiDb(tmdb_type)

    def _build_item(self, i):
        if not self.pagination and 'next_page' in i:
            return
        with TimerList(self.timer_lists, 'item_api', log_threshold=0.05, logging=self.log_timers):
            li = self.ib.get_listitem(i, use_iterprops=self.is_detailed)
            if li.infoproperties.get('plot_affix'):
                li.infolabels['plot'] = f"{li.infoproperties['plot_affix']}. {li.infolabels.get('plot')}"
            return li

    def _make_item(self, li):
        if not li:
            return

        with TimerList(self.timer_lists, 'item_abc', log_threshold=0.05, logging=self.log_timers):
            # Reformat ListItem.Label for episodes to match Kodi default 1x01.Title
            # Check if unaired and either apply special formatting or hide item depending on user settings
            li.set_episode_label()
            if self.format_episode_labels and not li.infoproperties.get('specialseason'):
                if li.is_unaired(no_date=self.nodate_is_unaired):
                    return

            # Add details from Kodi library
            try:
                li.set_details(details=self.kodi_db.get_kodi_details(li), reverse=True)
            except AttributeError:
                pass

            # Filter out items that are excluded (done after adding Kodi details so can filter against them)
            if not li.next_page and is_excluded(li, is_listitem=True, **self.filters):
                return

        with TimerList(self.timer_lists, 'item_xyz', log_threshold=0.05, logging=self.log_timers):
            # Add Trakt playcount and watched status
            li.set_playcount(playcount=self.trakt_method.get_playcount(li))
            if self.hide_watched and try_int(li.infolabels.get('playcount')) != 0:
                return

            li.set_context_menu(additions=self.context_additions)  # Set the context menu items
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
            return li

    def precache_parent(self, tmdb_id, season=None):
        self.ib.get_parents(tmdb_type='tv', tmdb_id=tmdb_id, season=season)
        # PREBUILD_PARENTSHOW = ['seasons', 'episodes', 'episode_groups', 'trakt_upnext', 'episode_group_seasons']

    def build_items(self, items):
        # Build items in threads
        self.ib.cache_only = self.tmdb_cache_only
        with TimerList(self.timer_lists, '--build', log_threshold=0.05, logging=self.log_timers):
            self.ib.parent_params = self.parent_params
            with ParallelThread(items, self._build_item) as pt:
                item_queue = pt.queue
            all_listitems = [i for i in item_queue if i]

        # Wait for sync thread
        with TimerList(self.timer_lists, '--sync', log_threshold=0.05, logging=self.log_timers):
            self._pre_sync.join()

        # Finalise listitems in parallel threads
        with TimerList(self.timer_lists, '--make', log_threshold=0.05, logging=self.log_timers):
            self.format_episode_labels = self.parent_params.get('info') not in NO_LABEL_FORMATTING
            with ParallelThread(all_listitems, self._make_item) as pt:
                item_queue = pt.queue

        if self.sort_by_dbid:
            item_queue_dbid = [li for li in item_queue if li and li.infolabels.get('dbid')]
            item_queue_tmdb = [li for li in item_queue if li and not li.infolabels.get('dbid')]
            item_queue = item_queue_dbid + item_queue_tmdb

        return item_queue

    def add_items(self, items):
        addDirectoryItems(self.handle, [(li.get_url(), li.get_listitem(), li.is_folder) for li in items if li])

    def set_mixed_content(self, response):
        self.library = 'video'

        lengths = [
            len(response.get('movies', [])),
            len(response.get('shows', [])),
            len(response.get('persons', []))]

        if lengths.index(max(lengths)) == 0:
            self.container_content = 'movies'
        elif lengths.index(max(lengths)) == 1:
            self.container_content = 'tvshows'
        elif lengths.index(max(lengths)) == 2:
            self.container_content = 'actors'

        if lengths[0] and lengths[1]:
            self.kodi_db = self.get_kodi_database('both')
        elif lengths[0]:
            self.kodi_db = self.get_kodi_database('movie')
        elif lengths[1]:
            self.kodi_db = self.get_kodi_database('tvshow')

    def set_params_to_container(self):
        params = {f'Param.{k}': f'{v}' for k, v in self.params.items() if k and v}
        if self.handle == -1:
            return params
        for k, v in params.items():
            setProperty(self.handle, k, v)  # Set params to container properties
        return params

    def finish_container(self):
        setPluginCategory(self.handle, self.plugin_category)  # Container.PluginCategory
        setContent(self.handle, self.container_content)  # Container.Content
        for i in self.sort_methods:
            addSortMethod(self.handle, **i)
        endOfDirectory(self.handle, updateListing=self.update_listing)

    def get_tmdb_id(self):
        if self.params.get('info') == 'collection':
            self.params['tmdb_type'] = 'collection'
        if not self.params.get('tmdb_id'):
            self.params['tmdb_id'] = self.tmdb_api.get_tmdb_id(**self.params)

    def get_items(self, **kwargs):
        """ Abstract method for getting items
        TODO: abc.abstractmethod to force ???
        """
        return

    def get_directory(self, items_only=False, build_items=True):
        with TimerList(self.timer_lists, 'total', logging=self.log_timers):
            self._pre_sync = Thread(target=self.trakt_method.pre_sync, kwargs=self.params)
            self._pre_sync.start()
            with TimerList(self.timer_lists, 'get_list', logging=self.log_timers):
                items = self.get_items(**self.params)
            if not items:
                return
            if not build_items:
                return items
            self.property_params = self.set_params_to_container()
            self.plugin_category = self.params.get('plugin_category') or self.plugin_category
            with TimerList(self.timer_lists, 'add_items', logging=self.log_timers):
                items = self.build_items(items)
                if items_only:
                    return items
                self.add_items(items)
            self.finish_container()
        if self.log_timers:
            log_timer_report(self.timer_lists, self.paramstring)
        if self.container_update:
            executebuiltin(f'Container.Update({self.container_update})')
        if self.container_refresh:
            executebuiltin('Container.Refresh')
