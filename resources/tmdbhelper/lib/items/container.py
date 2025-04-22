from tmdbhelper.lib.files.ftools import cached_property
from jurialmunkey.parser import try_int, boolean
from tmdbhelper.lib.addon.consts import NO_UNAIRED_LABEL, NO_UNAIRED_CHECK, REMOVE_EPISODE_COUNT
from tmdbhelper.lib.addon.plugin import get_setting, executebuiltin, get_localized, get_condvisibility
from tmdbhelper.lib.api.contains import CommonContainerAPIs
from tmdbhelper.lib.addon.logger import TimerList


""" Lazyimports
from tmdbhelper.lib.items.kodi import KodiDb
"""


class ContainerDirectoryCommon(CommonContainerAPIs):
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
            'exclude_operator': self.params.get('exclude_operator', None)
        }

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
        self.thumb_override = 0

    @cached_property
    def is_fanarttv(self):
        return self.params.get('fanarttv', '').lower()

    @cached_property
    def is_widget(self):
        return boolean(self.params.get('widget', False))

    @cached_property
    def is_cacheonly(self):
        return boolean(self.params.get('cacheonly', False))

    @cached_property
    def is_detailed(self):
        return boolean(self.params.get('detailed', False)) or self.params.get('info') == 'details'

    @cached_property
    def context_additions(self):
        if self.context_additions_make_node:
            return [(get_localized(32496), 'RunScript(plugin.video.themoviedb.helper,make_node)')]
        return []

    @cached_property
    def context_additions_make_node(self):
        return get_setting('contextmenu_make_node') if not self.is_widget else False

    @cached_property
    def hide_watched(self):
        return get_setting('widgets_hidewatched') if self.is_widget else False

    @cached_property
    def nodate_is_unaired(self):
        return get_setting('nodate_is_unaired')

    @cached_property
    def tmdb_cache_only(self):
        if self.is_cacheonly:  # cacheonly=true param overrides all other settings
            return True
        if not self.ftv_is_cache_only:  # fanarttv lookups require TMDb lookups for tvshow ID -- TODO: only force on tvshows
            return False
        if get_setting('tmdb_details'):  # user setting
            return False
        return True

    @cached_property
    def is_excluded(self):
        from tmdbhelper.lib.items.filters import is_excluded
        return is_excluded

    @cached_property
    def trakt_playdata(self):
        from tmdbhelper.lib.items.trakt import TraktPlayData
        return TraktPlayData(
            watchedindicators=get_setting('trakt_watchedindicators'),
            pauseplayprogress=get_setting('trakt_playprogress'),
            traktepisodetypes=get_setting('trakt_episodetypes'))

    @cached_property
    def ib(self):
        from tmdbhelper.lib.items.builder import ItemBuilder
        return ItemBuilder(
            tmdb_api=self.tmdb_api, ftv_api=self.ftv_api, trakt_api=self.trakt_api,
            log_timers=self.log_timers, timer_lists=self.timer_lists)

    @property
    def page_length(self):
        if self.is_widget or not get_condvisibility('Window.IsVisible(MyVideoNav.xml)'):
            return 1
        return get_setting('pagemulti_library', 'int')

    @cached_property
    def pagination(self):
        if not boolean(self.params.get('nextpage', True)):
            return False
        if self.is_widget and not get_setting('widgets_nextpage'):
            return False
        return True

    @property
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

    def get_kodi_database(self, tmdb_type):
        if not get_setting('local_db'):
            return
        with TimerList(self.timer_lists, 'get_kodi', log_threshold=0.05, logging=self.log_timers):
            from tmdbhelper.lib.items.kodi import KodiDb
            return KodiDb(tmdb_type)

    @cached_property
    def remove_unaired_object(self):
        return self.parent_params.get('info') not in NO_UNAIRED_CHECK

    @cached_property
    def format_unaired_labels(self):
        return self.parent_params.get('info') not in NO_UNAIRED_LABEL

    @cached_property
    def remove_episode_counts(self):
        return self.parent_params.get('info') in REMOVE_EPISODE_COUNT

    def make_item(self, li):
        if not li:
            return

        with TimerList(self.timer_lists, 'item_abc', log_threshold=0.05, logging=self.log_timers):

            # Remove episode counts for some types of lists (eg stars_in_tvshows) where API uses episode_count for appearances instead of totalepisodes
            if self.remove_episode_counts:
                li.infolabels.pop('episode', None)

            # Reformat ListItem.Label for episodes to match Kodi default 1x01.Title
            li.set_episode_label()

            # Check if unaired and either apply special formatting or hide item depending on user settings
            if self.format_unaired_labels and not li.infoproperties.get('specialseason'):
                is_unaired = li.is_unaired(no_date=self.nodate_is_unaired)
                if self.remove_unaired_object and is_unaired:
                    return

            # Add details from Kodi library
            try:
                li.set_details(details=self.kodi_db.get_kodi_details(li), reverse=True)
            except AttributeError:
                pass

            # Filter out items that are excluded (done after adding Kodi details so can filter against them)
            if not li.next_page and self.is_excluded(li, is_listitem=True, **self.filters):
                return

        with TimerList(self.timer_lists, 'item_xyz', log_threshold=0.05, logging=self.log_timers):
            # Add Trakt playcount and watched status
            li.set_playcount(playcount=self.trakt_playdata.get_playcount(li))
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
            self.trakt_playdata.set_episode_type(li)
            self.trakt_playdata.set_playprogress(li)
            return li

    def make_items(self, items):
        from tmdbhelper.lib.addon.thread import ParallelThread
        with ParallelThread(items, self.make_item) as pt:
            item_queue = pt.queue
        return self.sort_items_by_dbid(item_queue)

    def sort_items_by_dbid(self, items):
        if not self.sort_by_dbid:
            return items
        items_dbid = [li for li in items if li and li.infolabels.get('dbid')]
        items_tmdb = [li for li in items if li and not li.infolabels.get('dbid')]
        return items_dbid + items_tmdb

    @staticmethod
    def precache_parent(tmdb_id, season=None):
        return

    @staticmethod
    def build_detailed_items(items):
        return items

    def build_items(self, items):
        """ Build items in threads """

        items = self.build_detailed_items(items)

        # Wait for sync thread
        with TimerList(self.timer_lists, '--sync', log_threshold=0.05, logging=self.log_timers):
            self.trakt_playdata.pre_sync_join()

        # Finalise listitems in parallel threads
        with TimerList(self.timer_lists, '--make', log_threshold=0.05, logging=self.log_timers):
            items = self.make_items(items)

        return items

    def add_items(self, items):
        from xbmcplugin import addDirectoryItems
        addDirectoryItems(self.handle, [(li.get_url(), li.get_listitem(), li.is_folder) for li in items if li])

    def set_mixed_content(self, response):
        self.library = 'video'

        lengths = [
            len(response.get('movies', [])),
            len(response.get('shows', [])),
            len(response.get('persons', [])),
            len(response.get('seasons', [])),
            len(response.get('episodes', []))
        ]

        if lengths.index(max(lengths)) == 0:
            self.container_content = 'movies'
        elif lengths.index(max(lengths)) == 1:
            self.container_content = 'tvshows'
        elif lengths.index(max(lengths)) == 2:
            self.container_content = 'actors'
        elif lengths.index(max(lengths)) == 3:
            self.container_content = 'seasons'
        elif lengths.index(max(lengths)) == 4:
            self.container_content = 'episodes'

        if lengths[0] and (lengths[1] or lengths[3] or lengths[4]):
            self.kodi_db = self.get_kodi_database('both')
        elif lengths[0]:
            self.kodi_db = self.get_kodi_database('movie')
        elif (lengths[1] or lengths[3] or lengths[4]):
            self.kodi_db = self.get_kodi_database('tv')

    def set_params_to_container(self):
        params = {f'Param.{k}': f'{v}' for k, v in self.params.items() if k and v}
        if self.handle == -1:
            return params
        from xbmcplugin import setProperty
        for k, v in params.items():
            setProperty(self.handle, k, v)  # Set params to container properties
        return params

    def finish_container(self):
        from xbmcplugin import setPluginCategory, setContent, endOfDirectory, addSortMethod
        setPluginCategory(self.handle, self.plugin_category)  # Container.PluginCategory
        setContent(self.handle, self.container_content)  # Container.Content
        for i in self.sort_methods:
            addSortMethod(self.handle, **i)
        endOfDirectory(self.handle, updateListing=self.update_listing)

    def get_tmdb_id(self):

        if self.params.get('info') == 'collection' and self.params.get('tmdb_type') == 'movie':
            movie_tmdb_id = self.params.get('tmdb_id') or self.tmdb_api.get_tmdb_id(**self.params)
            self.params['tmdb_id'] = self.tmdb_api.get_collection_tmdb_id(movie_tmdb_id)
            self.params['tmdb_type'] = 'collection'
            return

        if self.params.get('tmdb_id'):
            return

        self.params['tmdb_id'] = self.tmdb_api.get_tmdb_id(**self.params)

    def get_items(self, **kwargs):
        """ Abstract method for getting items
        TODO: abc.abstractmethod to force ???
        """
        return

    def get_directory(self, items_only=False, build_items=True):
        with TimerList(self.timer_lists, 'total', logging=self.log_timers):
            self.trakt_playdata.pre_sync_start(**self.params)
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
            from tmdbhelper.lib.addon.logger import log_timer_report
            log_timer_report(self.timer_lists, self.paramstring)
        if self.container_update:
            executebuiltin(f'Container.Update({self.container_update})')
        if self.container_refresh:
            executebuiltin('Container.Refresh')


class ContainerDirectoryItemBuilder(ContainerDirectoryCommon):
    @cached_property
    def ib(self):
        from tmdbhelper.lib.items.builder import ItemBuilder
        return ItemBuilder(
            tmdb_api=self.tmdb_api, ftv_api=self.ftv_api, trakt_api=self.trakt_api,
            log_timers=self.log_timers, timer_lists=self.timer_lists)

    def precache_parent(self, tmdb_id, season=None):
        self.ib.get_parents(tmdb_type='tv', tmdb_id=tmdb_id, season=season)

    def build_detailed_item(self, i):
        if not self.pagination and 'next_page' in i:
            return
        with TimerList(self.timer_lists, 'item_api', log_threshold=0.05, logging=self.log_timers):
            li = self.ib.get_listitem(i, use_iterprops=self.is_detailed)
        if li.infoproperties.get('plot_affix'):
            li.infolabels['plot'] = f"{li.infoproperties['plot_affix']}. {li.infolabels.get('plot')}"
        return li

    def build_detailed_items(self, items):
        from tmdbhelper.lib.addon.thread import ParallelThread
        self.ib.cache_only = self.tmdb_cache_only
        self.ib.parent_params = self.parent_params
        with TimerList(self.timer_lists, '--build', log_threshold=0.05, logging=self.log_timers):
            with ParallelThread(items, self.build_detailed_item) as pt:
                item_queue = pt.queue
        return [i for i in item_queue if i]


class ContainerDirectoryItemDetails(ContainerDirectoryCommon):
    @cached_property
    def lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetailsConfigurator
        lidc = ListItemDetailsConfigurator(tmdb_api=self.tmdb_api, trakt_api=self.trakt_api)
        lidc.pagination = self.pagination
        return lidc

    def build_detailed_item(self, li):
        if li.infoproperties.get('plot_affix'):
            li.infolabels['plot'] = f"{li.infoproperties['plot_affix']}. {li.infolabels.get('plot')}"
        return li

    def build_detailed_items(self, items):
        with TimerList(self.timer_lists, '--build', log_threshold=0.05, logging=self.log_timers):
            items = self.lidc.configure_listitems_threaded(items)
            return [i for i in (self.build_detailed_item(li) for li in items if li) if i]


ContainerDirectory = ContainerDirectoryItemBuilder
# ContainerDirectory = ContainerDirectoryItemDetails
