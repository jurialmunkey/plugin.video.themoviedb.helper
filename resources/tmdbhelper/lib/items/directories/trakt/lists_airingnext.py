from tmdbhelper.lib.items.directories.lists_default import ItemCache, ListSliceProperties, ListDefault
from tmdbhelper.lib.items.directories.trakt.mapper_airingnext import AiringNextItemGetter
from tmdbhelper.lib.addon.plugin import get_setting, get_localized
from tmdbhelper.lib.addon.dialog import progress_bg
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class ListAiringNextProperties(ListSliceProperties):
    dialog_now = 0
    cache_days = 0.02

    @cached_property
    def dialog_max(self):
        return len(self.seed_items)

    def dialog_update(self, value, message):
        if not self.dialog_progress_bg:
            return
        self.dialog_progress_bg.update(value, message)

    def dialog_update_percentage(self, message):
        self.dialog_update(self.dialog_percentage, message)
        self.dialog_now += 1

    @property
    def dialog_percentage(self):
        return int((self.dialog_now / self.dialog_max) * 100)

    @cached_property
    def seed_items(self):
        self.dialog_update(0, message=f'{get_localized(32375)}...')
        return self.get_seed_items()

    def get_seed_items(self):
        sd = self.trakt_api.trakt_syncdata
        sd = sd.get_all_unhidden_shows_started_getter()
        try:
            return [{'tmdb_id': i[sd.keys.index('tmdb_id')]} for i in sd.items if i]
        except Exception:
            return []

    def get_threaded_item(self, item):
        item_mapper = AiringNextItemGetter(item)
        self.dialog_update_percentage(f'{get_localized(32375)}: {item_mapper.tmdb_id}')
        return item_mapper.item or None

    @progress_bg
    def get_uncached_items(self):
        from tmdbhelper.lib.addon.thread import ParallelThread
        ParallelThreadLimited = ParallelThread
        ParallelThreadLimited.thread_max = min((40, ParallelThreadLimited.thread_max or 40))
        with ParallelThreadLimited(self.seed_items, self.get_threaded_item) as pt:
            item_queue = pt.queue
        return [i for i in item_queue if i]

    @cached_property
    def sorted_items(self):
        sorted_items = sorted(self.filtered_items, key=lambda i: i['infolabels']['premiered'], reverse=False)
        return sorted_items[self.item_a:self.item_z]


class ListLibraryAiringNextProperties(ListAiringNextProperties):
    def get_seed_items(self):
        if not self.kodi_db or not self.kodi_db.database:
            return []
        return self.kodi_db.database


class ListTraktAiringNext(ListDefault):
    list_properties_class = ListAiringNextProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32459
        list_properties.item_type = 'episode'
        list_properties.container_content = 'episodes'
        list_properties.page_length = get_setting('pagemulti_trakt', 'int') or 1
        return list_properties

    def get_items(self, page=1, length=None, **kwargs):
        self.list_properties.tmdb_type = 'tv'
        self.list_properties.length = try_int(length)
        self.list_properties.page = try_int(page) or 1
        return self.get_items_finalised()


class ListLibraryAiringNext(ListTraktAiringNext):
    list_properties_class = ListLibraryAiringNextProperties

    @cached_property
    def kodi_db(self):  # Override internal settings for adding in library details as we always need them here
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        return get_kodi_library('tv')

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32458
        list_properties.kodi_db = self.kodi_db
        return list_properties
