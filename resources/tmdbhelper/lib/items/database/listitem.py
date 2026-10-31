from tmdbhelper.lib.api.contains import CommonContainerAPIs
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.addon.logger import TimerList, kodi_log
from tmdbhelper.lib.items.database.details.client import DetailsClient
from tmdbhelper.lib.items.database.details.request import DetailsRequest


class ListItemConfig:
    listitem_cacher_permitted_types = ('movie', 'tvshow', 'season', 'episode', 'person', 'set')

    def __init__(self, parent, item):
        if parent.__class__.__name__ != 'ListItemDetails':
            raise Exception(f'Requires ListItemDetails parent but {parent.__class__.__name__} given')
        self.item = item
        self.next_page = bool('next_page' in item)
        self.parent = parent
        self.item['parent_params'] = self.parent.parent_params

    @cached_property
    def is_cacheable(self):
        if self.next_page:
            return False
        if self.mediatype not in self.listitem_cacher_permitted_types:
            return False
        if not self.tmdb_id:
            return False
        if not self.tmdb_type:
            return False
        if not self.request:
            return False
        return True

    @cached_property
    def request(self):
        return self.get_request()

    def get_request(self):
        # One malformed item must not prevent details for the rest of the list.
        try:
            return self.parent.get_request(self.tmdb_type, self.tmdb_id, self.season, self.episode)
        except ValueError as exc:
            kodi_log(f'Item details skipped for {self.mediatype} {self.tmdb_id}: {exc}', 1)

    @cached_property
    def listitem(self):
        return ListItem(**self.item)

    def get_configured_listitem(self, data):
        if self.next_page and not self.parent.pagination:
            return
        self.listitem.set_details(data, override=True, reverse_artwork=True) if data else None
        return self.listitem

    @cached_property
    def mediatype(self):
        if self.listitem.infoproperties.get('tmdb_type') == 'person':
            return 'person'
        return self.listitem.infolabels.get('mediatype')

    @cached_property
    def tmdb_id(self):
        if self.mediatype == 'movie':
            return self.listitem.unique_ids.get('tmdb')
        if self.mediatype == 'tvshow':
            return self.listitem.unique_ids.get('tmdb') or self.listitem.unique_ids.get('tvshow.tmdb')
        if self.mediatype == 'season':
            return self.listitem.unique_ids.get('tvshow.tmdb')
        if self.mediatype == 'episode':
            return self.listitem.unique_ids.get('tvshow.tmdb')
        if self.mediatype == 'person':
            return self.listitem.unique_ids.get('tmdb') or self.listitem.infoproperties.get('tmdb_id')
        if self.mediatype == 'set':
            return self.listitem.unique_ids.get('tmdb')
        return

    @cached_property
    def tmdb_type(self):
        if self.mediatype == 'movie':
            return 'movie'
        if self.mediatype == 'tvshow':
            return 'tv'
        if self.mediatype == 'season':
            return 'tv'
        if self.mediatype == 'episode':
            return 'tv'
        if self.mediatype == 'person':
            return 'person'
        if self.mediatype == 'set':
            return 'collection'
        return

    @cached_property
    def season(self):
        if self.mediatype not in ('episode', 'season'):
            return
        return self.listitem.infolabels.get('season', 0)

    @cached_property
    def episode(self):
        if self.mediatype != 'episode':
            return
        return self.listitem.infolabels.get('episode', 0)


class ListItemBatch:
    def __init__(self, parent, items):
        self.parent = parent
        self.items = [ListItemConfig(parent, item) for item in items]

    @cached_property
    def requested_items(self):
        return self.get_requested_items()

    def get_requested_items(self):
        return [item for item in self.items if item.is_cacheable]

    def get_configured_items(self):
        with TimerList(
                self.parent.timer_lists, ' - service',
                log_threshold=0.001, logging=self.parent.log_timers):
            data = self.parent.client.get_items([item.request for item in self.requested_items])
        details = dict(zip(self.requested_items, data))
        return [item.get_configured_listitem(details.get(item)) for item in self.items]


class ListItemDetails:
    pagination = False
    cache_refresh = None
    cache_translations = False
    extendedinfo = False
    parent_params = {}
    timer_lists = {}
    log_timers = False

    def __init__(self, common_apis=None):
        self.common_apis = common_apis or CommonContainerAPIs()
        self.client = DetailsClient()

    def get_request(self, tmdb_type, tmdb_id, season=None, episode=None):
        return DetailsRequest.from_type(
            tmdb_type, tmdb_id, season, episode,
            cache_refresh=self.cache_refresh, cache_translations=self.cache_translations,
            extendedinfo=self.extendedinfo, language=self.common_apis.tmdb_api.language)

    def get_item(self, tmdb_type, tmdb_id, season=None, episode=None):
        if not tmdb_id:
            return
        return self.client.get_item(self.get_request(tmdb_type, tmdb_id, season, episode))

    def configure_listitems_threaded(self, items):
        return ListItemBatch(self, items).get_configured_items()
