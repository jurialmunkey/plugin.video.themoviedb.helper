from tmdbhelper.lib.items.directories.lists_default import UncachedItemsPage
from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties
from tmdbhelper.lib.items.directories.mapper_standard import FactoryItemMapper
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class UncachedTraktItemsPage(UncachedItemsPage):
    @cached_property
    def response_results(self):
        try:
            return self.response.json()
        except (TypeError, KeyError, AttributeError):
            return

    @cached_property
    def response_total_pages(self):
        return try_int(self.response.headers.get('x-pagination-page-count', 0))

    @cached_property
    def response_total_items(self):
        return try_int(self.response.headers.get('x-pagination-item-count', 0))


class ListTraktStandardProperties(ListStandardProperties):

    class_pages = UncachedTraktItemsPage
    trakt_filters = {}
    trakt_authorization = False

    sub_type = False
    sub_type_map = {
        'movie': 'movie',
        'tv': 'show',
    }

    @property
    def next_page(self):
        return self.page + 1

    @cached_property
    def limit(self):
        return self.pmax * 20

    @cached_property
    def cache_name_tuple(self):
        cache_name_tuple = self.get_cache_name_list_filter()
        cache_name_tuple = self.get_cache_name_list_prefix() + cache_name_tuple
        cache_name_tuple = cache_name_tuple + [self.page, self.limit]
        return tuple(cache_name_tuple)

    def get_cache_name_list_filter(self):
        cache_name_list = [f'{k}={v}' for k, v in self.trakt_filters.items()]
        cache_name_list = sorted(cache_name_list)
        return cache_name_list

    def get_cache_name_list_prefix(self):
        return [self.class_name, self.tmdb_type]

    @cached_property
    def trakt_type(self):
        return self.sub_type_map.get(self.tmdb_type)

    @cached_property
    def url(self):
        return self.request_url.format(trakt_type=self.trakt_type)

    def get_uncached_items(self):
        return {
            'items': self.class_pages(self, self.page).items,
            'pages': self.total_pages,
            'count': self.total_items,
        }

    def get_api_response(self, page=1):
        if self.trakt_authorization and not self.trakt_api.is_authorized:
            return
        return self.trakt_api.get_response(self.url, page=page, limit=self.limit, **self.trakt_filters)

    def get_mapped_item(self, item, add_infoproperties=None):
        return FactoryItemMapper(item, add_infoproperties, trakt_type=self.trakt_type, sub_type=self.sub_type).item


class ListTraktStandard(ListStandard):

    list_properties_class = ListTraktStandardProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.page_length = get_setting('pagemulti_trakt', 'int') or 1
        return list_properties


class ListTraktFilteredProperties(ListTraktStandardProperties):
    @cached_property
    def plugin_category(self):
        plugin_category = self.plugin_name.format(localized=self.localized, plural=self.plural)
        plugin_category = f'{plugin_category} ({" ".join([f"{v}".capitalize() for v in self.trakt_filters.values()])})' if self.trakt_filters else plugin_category
        return plugin_category


class ListTraktFiltered(ListTraktStandard):

    list_properties_class = ListTraktFilteredProperties

    def get_items(
        self, *args,
        genres=None,
        subgenres=None,
        query=None,
        years=None,
        languages=None,
        countries=None,
        runtimes=None,
        studio_ids=None,
        certifications=None,
        watchnow=None,
        network_ids=None,
        status=None,
        ratings=None,
        votes=None,
        tmdb_ratings=None,
        tmdb_votes=None,
        imdb_ratings=None,
        imdb_votes=None,
        rt_meters=None,
        rt_user_meters=None,
        metascores=None,
        **kwargs
    ):

        self.list_properties.trakt_filters = {
            k: v for k, v in (
                ('genres', genres),
                ('subgenres', subgenres),
                ('query', query),
                ('years', years),
                ('languages', languages),
                ('countries', countries),
                ('runtimes', runtimes),
                ('studio_ids', studio_ids),
                ('certifications', certifications),
                ('watchnow', watchnow),
                ('network_ids', network_ids),
                ('status', status),
                ('ratings', ratings),
                ('votes', votes),
                ('tmdb_ratings', tmdb_ratings),
                ('tmdb_votes', tmdb_votes),
                ('imdb_ratings', imdb_ratings),
                ('imdb_votes', imdb_votes),
                ('rt_meters', rt_meters),
                ('rt_user_meters', rt_user_meters),
                ('metascores', metascores),
            ) if k and v
        }

        return super().get_items(*args, **kwargs)
