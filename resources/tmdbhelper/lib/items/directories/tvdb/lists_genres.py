from tmdbhelper.lib.items.directories.tvdb.lists_awards import ListAwards
from tmdbhelper.lib.items.directories.tvdb.lists_tvdb import ListTVDbProperties, ListTVDbMediaProperties
from tmdbhelper.lib.items.directories.tvdb.mapper_static import TVDbStaticGenresItemMapper
from tmdbhelper.lib.items.directories.tvdb.mapper_items import TVDbGenreItemMapper
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property


class ListTVDbGenresProperties(ListTVDbProperties):
    item_mapper_class = TVDbStaticGenresItemMapper


class ListGenres(ListAwards):

    list_properties_class = ListTVDbGenresProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 135
        list_properties.request_url = 'genres'
        list_properties.sorting_key = lambda x: x.get('label') or 0
        return list_properties


class ListTVDbMixedMediaProperties(ListTVDbMediaProperties):
    item_mapper_class = staticmethod(TVDbGenreItemMapper)

    @cached_property
    def request(self):
        request = []
        if self.tmdb_type in ('movie', 'both'):
            request += self.tvdb_api.get_request_lc(self.url.format(tvdb_type='movies'), **self.request_url_kwargs)
        if self.tmdb_type in ('tv', 'both'):
            request += self.tvdb_api.get_request_lc(self.url.format(tvdb_type='series'), **self.request_url_kwargs)
        return request


class ListGenre(ListAwards):

    list_properties_class = ListTVDbMixedMediaProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 135
        list_properties.request_url = '{{tvdb_type}}/filter'
        list_properties.page_length = get_setting('pagemulti_trakt', 'int') or 1
        return list_properties

    def get_items(self, tvdb_id, **kwargs):
        self.list_properties.request_url_kwargs = {'genre': tvdb_id, 'sort': 'score', 'sortType': 'desc'}
        return super().get_items(**kwargs)
