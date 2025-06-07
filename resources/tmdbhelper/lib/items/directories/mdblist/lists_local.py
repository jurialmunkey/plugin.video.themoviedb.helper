from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties, UncachedItemsPage
from tmdbhelper.lib.items.directories.mdblist.mapper_standard import FactoryMDbListItemMapper
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.ftools import cached_property
from jurialmunkey.parser import try_int


PAGES_LENGTH = get_setting('pagemulti_trakt', 'int') or 1


class UncachedMDbListItemsPage(UncachedItemsPage):
    def __init__(self, outer_class, page):
        self.outer_class = outer_class
        self.page = page

    @cached_property
    def response_json(self):
        try:
            return self.response['json']
        except (TypeError, KeyError):
            return []

    @cached_property
    def results(self):
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
        return self.length * 20

    @cached_property
    def next_page_item(self):
        return {'next_page': self.next_page}

    def get_cached_items(self, *args, **kwargs):  # Override caching
        return self.get_uncached_items(*args, **kwargs)

    def get_uncached_items(self):
        return {
            'items': self.class_pages(self, self.page).items,
            'pages': self.total_pages,
            'count': self.total_items,
        }

    def get_uncached_response(self, page=1):
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

        if not response:
            return {}

        # Calculate total values
        item_count = len(response)
        page_count = (item_count + self.limit - 1) // self.limit  # Ceiling division

        # Get start and end offsets for slicing results
        item_a = max(((page - 1) * self.limit), 0)
        item_z = min((page * self.limit), item_count)

        return {
            'json': response[item_a:item_z],
            'headers': {
                'x-pagination-page-count': page_count,
                'x-pagination-item-count': item_count,
            }
        }

    def get_mapped_item(self, item, add_infoproperties=None):
        return FactoryMDbListItemMapper(item, add_infoproperties).item


class ListMDbListLocal(ListStandard):

    list_properties_class = ListMDbListLocalProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'TMDbHelper'
        return list_properties

    def get_items(self, *args, paths, length=None, tmdb_type=None, **kwargs):
        if not paths or not isinstance(paths, list):
            return
        self.list_properties.filepath = paths[0]
        length = try_int(length) or PAGES_LENGTH
        return super().get_items(*args, length=length, tmdb_type=tmdb_type, **kwargs)
