from jurialmunkey.parser import boolean
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.consts import NO_UNAIRED_LABEL
from tmdbhelper.lib.addon.plugin import get_setting, executebuiltin, get_localized
from tmdbhelper.lib.api.contains import CommonContainerAPIs
from tmdbhelper.lib.addon.logger import TimerList


""" Lazyimports
from tmdbhelper.lib.items.kodi import KodiDb
"""


class ItemCache:
    def __init__(self, filename, cache_days=0.25):  # 6 hours default cache
        from tmdbhelper.lib.files.bcache import BasicCache
        self.cache = BasicCache(filename=filename)
        self.cache_days = cache_days

    def __call__(self, function):
        def wrapper(instance, *args, **kwargs):
            kwargs['cache_days'] = self.cache_days
            kwargs['cache_name'] = f'{instance.__class__.__name__}.{function.__name__}'
            kwargs['cache_combine_name'] = True
            return self.cache.use_cache(function, instance, *args, **kwargs)
        return wrapper


use_item_cache = ItemCache


class ContainerDirectoryCommon(CommonContainerAPIs):
    default_cacheonly = False
    update_listing = False  # endOfDirectory(updateListing=) set True to replace current path
    plugin_category = ''  # Container.PluginCategory / ListItem.Property(widget)
    container_content = ''  # Container.Content({})
    container_update = ''  # Add path to call Containr.Update({}) at end of directory
    container_refresh = False  # True call Container.Refresh at end of directory
    sort_by_dbid = False
    kodi_db = None
    thumb_override = 0

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

        self.sort_methods = []  # List of kwargs dictionaries [{'sortMethod': SORT_METHOD_UNSORTED}]
        self.property_params = {}

    @cached_property
    def is_widget(self):
        return boolean(self.params.get('widget', False))

    @cached_property
    def is_cacheonly(self):
        return boolean(self.params.get('cacheonly', self.default_cacheonly))

    @cached_property
    def is_detailed(self):
        if self.params.get('info') == 'details':
            return True
        return boolean(self.params.get('detailed', False))

    @cached_property
    def context_additions(self):
        if self.context_additions_make_node:
            return [(get_localized(32496), 'RunScript(plugin.video.themoviedb.helper,make_node)')]
        return []

    @cached_property
    def context_additions_make_node(self):
        return get_setting('contextmenu_make_node') if not self.is_widget else False

    @cached_property
    def is_excluded(self):
        from tmdbhelper.lib.items.filters import is_excluded
        return is_excluded

    @cached_property
    def trakt_playdata(self):
        from tmdbhelper.lib.items.trakt import TraktPlayData
        return TraktPlayData(
            watchedindicators=get_setting('trakt_watchedindicators'),
            pauseplayprogress=get_setting('trakt_watchedindicators'))

    @cached_property
    def pagination(self):
        if not boolean(self.params.get('nextpage', True)):
            return False
        if self.is_widget and not get_setting('widgets_nextpage'):
            return False
        return True

    @cached_property
    def kodi_db_preferred(self):
        if get_setting('use_kodi_local_db', 'int') == 2:
            return True  # Overwrite TMDb data with Kodi DB data
        return False  # Compliment missing TMDb data with Kodi Db data

    def get_kodi_database(self, tmdb_type):
        if get_setting('use_kodi_local_db', 'int') == 0:
            return
        with TimerList(self.timer_lists, 'get_kodi', log_threshold=0.001, logging=self.log_timers):
            from tmdbhelper.lib.items.kodi import KodiDb
            return KodiDb(tmdb_type)

    @cached_property
    def format_unaired_labels(self):
        return self.parent_params.get('info') not in NO_UNAIRED_LABEL

    @cached_property
    def hide_unaired(self):
        return boolean(self.parent_params.get('hide_unaired'))

    @cached_property
    def only_unaired(self):
        return boolean(self.parent_params.get('only_unaired'))

    def make_item(self, li):
        if not li:
            return

        def finalise_next_page():
            li.params['cacheonly'] = self.is_cacheonly
            li.params['plugin_category'] = self.plugin_category  # Carry the plugin category to next page in plugin:// path
            return li.finalise()

        def finalise_mediaitem():
            # Check if unaired and either apply special formatting or hide item depending on user settings
            li.format_unaired_labels = bool(self.format_unaired_labels and not li.infoproperties.get('specialseason'))
            if li.format_unaired_labels and self.hide_unaired and li.is_unaired:
                return
            if li.format_unaired_labels and self.only_unaired and not li.is_unaired:
                return

            # Add details from Kodi library
            try:
                li.set_details(details=self.kodi_db.get_kodi_details(li), reverse=self.kodi_db_preferred)
            except AttributeError:
                pass

            # Filter out items that are excluded (done after adding Kodi details so can filter against them)
            if self.is_excluded(li, is_listitem=True, **self.filters):
                return

            li.context_additions = self.context_additions
            li.thumb_override = self.thumb_override
            li.infoproperties_additions['widget'] = self.plugin_category
            li.infoproperties_additions.update(self.property_params)

            return li.finalise()

        return finalise_next_page() if li.next_page else finalise_mediaitem()

    def make_items(self, items):
        make_items = [self.make_item(i) for i in items if i]
        make_items = self.sort_items_by_dbid(make_items) if self.sort_by_dbid else make_items
        return make_items

    def sort_items_by_dbid(self, items):
        items_dbid = [li for li in items if li and li.infolabels.get('dbid')]
        items_tmdb = [li for li in items if li and not li.infolabels.get('dbid')]
        return items_dbid + items_tmdb

    @staticmethod
    def build_detailed_items(items):
        return items

    def build_items(self, items):
        """ Build items in threads """

        items = self.build_detailed_items(items)

        # Finalise listitems in parallel threads
        with TimerList(self.timer_lists, '--make', log_threshold=0.001, logging=self.log_timers):
            items = self.make_items(items)

        return items

    def add_items(self, items):
        with TimerList(self.timer_lists, '--list', log_threshold=0.001, logging=self.log_timers):
            items = [(li.url, li.get_listitem(), li.is_folder) for li in items if li]
        with TimerList(self.timer_lists, '--dirs', log_threshold=0.001, logging=self.log_timers):
            from xbmcplugin import addDirectoryItems
            addDirectoryItems(self.handle, items)

    def set_mixed_content(self, response):
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
        params = {f'param.{k}': f'{v}' for k, v in self.params.items() if k and v}
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

    def get_collection_tmdb_id(self, tmdb_id=None, **kwargs):
        try:
            from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
            sync = BaseItemFactory('movie')
            sync.tmdb_id = tmdb_id or self.query_database.get_tmdb_id(**kwargs)
            return sync.data['infoproperties']['set.tmdb_id']
        except (KeyError, TypeError, AttributeError):
            pass

    def get_tmdb_id(self):
        if self.params.get('info') == 'collection' and self.params.get('tmdb_type') == 'movie':
            self.params['tmdb_type'] = 'collection'
            self.params['tmdb_id'] = self.get_collection_tmdb_id(**self.params)
            return

        if self.params.get('tmdb_id'):
            return

        self.params['tmdb_id'] = self.query_database.get_tmdb_id(**self.params)

    def get_items(self, **kwargs):
        """ Abstract method for getting items
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

            self.property_params.update(self.set_params_to_container())
            self.plugin_category = self.params.get('plugin_category') or self.plugin_category

            with TimerList(self.timer_lists, '--sync', log_threshold=0.001, logging=self.log_timers):
                self.trakt_playdata.pre_sync_join()

            with TimerList(self.timer_lists, 'add_items', logging=self.log_timers):
                items = self.build_items(items)
                if items_only:
                    return items
                self.add_items(items)
            self.finish_container()

        if self.log_timers:
            from tmdbhelper.lib.files.futils import write_to_file
            from tmdbhelper.lib.addon.logger import log_timer_report
            from tmdbhelper.lib.addon.tmdate import get_todays_date
            report_data = log_timer_report(self.timer_lists, self.paramstring, logging=False)
            write_to_file(''.join(report_data), 'timer_report', f'{get_todays_date()}.txt', join_addon_data=True, append_to_file=True)

        if self.container_update:
            executebuiltin(f'Container.Update({self.container_update})')

        if self.container_refresh:
            executebuiltin('Container.Refresh')


class ContainerDirectory(ContainerDirectoryCommon):

    @cached_property
    def lidc_cache_refresh(self):
        if self.is_cacheonly:
            return 'never'
        if self.is_detailed:
            return None
        return 'basic'

    @cached_property
    def lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        lidc = ListItemDetails(self)
        lidc.parent_params = self.parent_params
        lidc.pagination = self.pagination
        lidc.cache_refresh = self.lidc_cache_refresh
        lidc.extendedinfo = self.is_detailed
        lidc.timer_lists = self.timer_lists
        lidc.log_timers = self.log_timers
        return lidc

    def build_detailed_item(self, li):
        if li.infoproperties.get('label_override'):
            li.label = f"{li.infoproperties['label_override']}"
        if li.infoproperties.get('label_affix'):
            li.label = f"{li.infoproperties['label_affix']}. {li.label}"
        if li.infoproperties.get('plot_affix'):
            li.infolabels['plot'] = f"{li.infoproperties['plot_affix']}. {li.infolabels.get('plot')}"
        return li

    def build_detailed_items(self, items):
        with TimerList(self.timer_lists, '--build', log_threshold=0.001, logging=self.log_timers):
            items = self.lidc.configure_listitems_threaded(items)
            return [i for i in (self.build_detailed_item(li) for li in items if li) if i]


class ContainerDefaultCacheDirectory(ContainerDirectory):
    default_cacheonly = False


class ContainerCacheOnlyDirectory(ContainerDirectory):
    default_cacheonly = True
