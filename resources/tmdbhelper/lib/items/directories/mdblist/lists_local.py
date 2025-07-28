from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties, UncachedItemsPage
from tmdbhelper.lib.items.directories.mdblist.mapper_standard import FactoryMDbListItemMapper
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class UncachedMDbListLocalData:
    def __init__(self, response, page=1, limit=20):
        self.response = response
        self.limit = limit
        self.page = page

    @cached_property
    def item_count(self):
        return len(self.response)

    @cached_property
    def page_count(self):
        return (self.item_count + self.limit - 1) // self.limit  # Ceiling division

    @cached_property
    def item_a(self):
        return max(((self.page - 1) * self.limit), 0)

    @cached_property
    def item_z(self):
        return min((self.page * self.limit), self.item_count)

    @cached_property
    def json(self):
        return self.response[self.item_a:self.item_z]

    @cached_property
    def data(self):
        return {
            'json': self.json,
            'headers': {
                'x-pagination-page-count': self.page_count,
                'x-pagination-item-count': self.item_count,
            }
        } if self.response else {}


class UncachedMDbListItemsPage(UncachedItemsPage):
    def __init__(self, outer_class, page):
        self.outer_class = outer_class
        self.page = page

    @cached_property
    def response_json(self):
        return self.get_response_json()

    def get_response_json(self):
        try:
            return self.response['json']
        except (TypeError, KeyError):
            return []

    def get_results(self):
        try:
            self.outer_class.total_pages = try_int(self.response['headers'].get('x-pagination-page-count', 0))
            self.outer_class.total_items = try_int(self.response['headers'].get('x-pagination-item-count', 0))
        except (TypeError, KeyError):
            self.outer_class.total_pages = 0
            self.outer_class.total_items = 0
        return self.response_json


class ListMDbListLocalProperties(ListStandardProperties):

    class_pages = UncachedMDbListItemsPage

    def get_mediatype_items(self, mediatype):
        return [i for i in self.items if i['infolabels']['mediatype'] == mediatype]

    @cached_property
    def movies(self):
        return self.get_mediatype_items('movie')

    @cached_property
    def tvshows(self):
        return self.get_mediatype_items('tvshow')

    @cached_property
    def seasons(self):
        return self.get_mediatype_items('season')

    @cached_property
    def episodes(self):
        return self.get_mediatype_items('episode')

    @cached_property
    def container_content(self):
        container_content = [
            ('movies', len(self.movies)),
            ('tvshows', len(self.tvshows)),
            ('seasons', len(self.seasons)),
            ('episodes', len(self.episodes)),
        ]
        container_content = sorted(container_content, key=lambda x: x[1])
        return container_content[0][0]

    @property
    def next_page(self):
        return self.page + 1

    @cached_property
    def limit(self):
        return self.pmax * 20

    @cached_property
    def next_page_item(self):
        return {'next_page': self.next_page}

    def get_uncached_items(self):
        return {
            'items': self.class_pages(self, self.page).items,
            'pages': self.total_pages,
            'count': self.total_items,
        }

    def get_api_response(self, page=1):
        import json
        import xbmcvfs
        import contextlib

        response = None

        if self.filepath.startswith('http'):
            import requests
            response = requests.get(self.filepath, timeout=10.000)
            response = response.json() if response else None

        else:
            with contextlib.suppress(IOError, json.JSONDecodeError):
                with xbmcvfs.File(self.filepath, 'r') as file:
                    response = json.load(file)

        return UncachedMDbListLocalData(response, self.page, self.limit).data

    def get_mapped_item(self, item, add_infoproperties=None):
        return FactoryMDbListItemMapper(item, add_infoproperties).item


class ListMDbListLocalNoCacheProperties(ListMDbListLocalProperties):
    def get_cached_items(self, *args, **kwargs):  # Override caching
        return self.get_uncached_items(*args, **kwargs)


class ListMDbListLocal(ListStandard):

    list_properties_class = ListMDbListLocalNoCacheProperties  # Don't cache filepath items

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'TMDbHelper'
        list_properties.page_length = get_setting('pagemulti_trakt', 'int') or 1
        return list_properties

    def get_items(self, *args, paths, tmdb_type=None, **kwargs):
        if not paths or not isinstance(paths, list):
            return
        self.list_properties.filepath = paths[0]
        return super().get_items(*args, tmdb_type=tmdb_type, **kwargs)
