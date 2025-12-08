from tmdbhelper.lib.items.directories.lists_default import UncachedItemsPage
from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties
from tmdbhelper.lib.items.directories.mdblist.mapper_standard import FactoryMDbListItemMapper
from tmdbhelper.lib.items.directories.lists_local import UncachedListLocalData
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class UncachedMDbListItemsPage(UncachedItemsPage):
    @cached_property
    def response_results(self):
        try:
            return self.response['json']
        except (TypeError, KeyError):
            return

    @cached_property
    def response_total_pages(self):
        return try_int(self.response['headers'].get('x-pagination-page-count', 0))

    @cached_property
    def response_total_items(self):
        return try_int(self.response['headers'].get('x-pagination-item-count', 0))


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

        return UncachedListLocalData(response, self.page, self.limit).data

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
