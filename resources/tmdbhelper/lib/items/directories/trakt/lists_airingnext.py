from tmdbhelper.lib.items.directories.lists_default import ItemCache, ListProperties, ListDefault
from tmdbhelper.lib.addon.plugin import KeyGetter, get_setting
from tmdbhelper.lib.addon.dialog import progress_bg
from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class AiringNextItemMapper(ItemMapper):

    prefix = 'next_aired'

    @cached_property
    def tmdb_id(self):
        return self.meta.get('tmdb_id')

    @cached_property
    def premiered(self):
        return self.meta.get(f'{self.prefix}.original')

    @cached_property
    def is_future(self):
        if not self.premiered:
            return
        from tmdbhelper.lib.addon.tmdate import is_future_timestamp
        return is_future_timestamp(self.premiered, time_fmt="%Y-%m-%d", time_lim=10, days=-1)

    def get_metadata(self, key):
        name = f'{self.prefix}.{key}'
        data = f'{self.meta.get(name)}'
        return data

    @cached_property
    def title(self):
        return self.get_metadata('name')

    @cached_property
    def episode(self):
        return self.get_metadata('episode')

    @cached_property
    def season(self):
        return self.get_metadata('season')

    @cached_property
    def label(self):
        label = f'{self.title} ({self.premiered})'
        return label

    def get_infolabels(self):
        return {
            'mediatype': 'episode',
            'title': self.title,
            'episode': self.episode,
            'season': self.season,
            'plot': self.get_metadata('plot'),
            'year': self.get_metadata('year'),
            'premiered': self.premiered
        }

    def get_params(self):
        return {
            'info': 'details',
            'tmdb_type': 'tv',
            'tmdb_id': self.tmdb_id,
            'episode': self.episode,
            'season': self.season,
        }

    def get_unique_ids(self):
        return {
            'tmdb': self.tmdb_id,
            'tvshow.tmdb': self.tmdb_id,
        }

    def get_item(self):
        if not self.is_future:
            return
        return super().get_item()


class AiringNextItemGetter:

    def __init__(self, data):
        self.data = KeyGetter(data)

    @cached_property
    def tmdb_id(self):
        tmdb_id = self.data.get_key('tmdb_id')
        tmdb_id = tmdb_id or self.query_database.get_tmdb_id(
            tmdb_type='tv',
            imdb_id=self.data.get_key('imdb_id'),
            tvdb_id=self.data.get_key('tvdb_id'),
            query=self.data.get_key('showtitle') or self.data.get_key('title'),
            year=self.data.get_key('year')
        )
        return tmdb_id

    @cached_property
    def lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        lidc = ListItemDetails()
        lidc.extendedinfo = False
        return lidc

    @cached_property
    def query_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    @cached_property
    def meta(self):
        if not self.tmdb_id:
            return {}
        meta = self.lidc.get_item('tv', self.tmdb_id)
        meta = meta.get('infoproperties')
        if not meta:
            return {}
        meta['tmdb_id'] = self.tmdb_id
        return meta

    @cached_property
    def item(self):
        if not self.meta:
            return
        return AiringNextItemMapper(self.meta, add_infoproperties=None).item


class ListAiringNextProperties(ListProperties):
    dialog_now = 0
    cache_days = 0.02
    unconfigured_item_data = None

    @cached_property
    def cache_name_tuple(self):
        return (self.class_name, )

    @property
    def next_page(self):
        return self.page + 1

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
        self.dialog_update(0, message=f'Getting seed items...')
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
        self.dialog_update_percentage(f'{item_mapper.tmdb_id} - Checking TMDb ID')
        return item_mapper.item or None

    @ItemCache('ItemContainer.db')
    def get_cached_items(self, *args, **kwargs):
        return self.get_uncached_items(*args, **kwargs)

    @progress_bg
    def get_uncached_items(self):
        from tmdbhelper.lib.addon.thread import ParallelThread
        ParallelThreadLimited = ParallelThread
        ParallelThreadLimited.thread_max = min((40, ParallelThreadLimited.thread_max or 40))
        with ParallelThreadLimited(self.seed_items, self.get_threaded_item) as pt:
            item_queue = pt.queue
        return [i for i in item_queue if i]

    @cached_property
    def items(self):
        return self.get_cached_items() or []

    @cached_property
    def pages(self):
        return (self.count + self.limit - 1) // self.limit  # Ceiling division

    @cached_property
    def count(self):
        return len(self.filtered_items)

    @cached_property
    def limit(self):
        return self.pmax * 20

    @cached_property
    def item_a(self):
        return max(((self.page - 1) * self.limit), 0)

    @cached_property
    def item_z(self):
        return min((self.page * self.limit), self.count)

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
