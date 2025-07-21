from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.trakt.mapper_comments import CommentsItemMapper
from tmdbhelper.lib.items.directories.trakt.mapper_watchers import WatchersItemMapper
from tmdbhelper.lib.items.directories.trakt.lists_standard import (
    ListTraktStandard,
    ListTraktStandardProperties,
)


class ListTraktRelatedProperties(ListTraktStandardProperties):

    trakt_sort = None

    @property
    def url(self):
        return self.request_url.format(
            trakt_type=self.trakt_type,
            trakt_slug=self.trakt_slug,
            trakt_sort=self.trakt_sort,
        )

    def get_cache_name_list_prefix(self):
        return [self.class_name, self.tmdb_type, self.tmdb_id, self.trakt_sort]

    @cached_property
    def trakt_slug(self):
        return self.query_database.get_trakt_id(self.tmdb_id, 'tmdb', item_type=self.trakt_type, output_type='slug')


class ListTraktRelatedCommentsProperties(ListTraktRelatedProperties):
    container_content = ''

    def get_mapped_item(self, item, add_infoproperties=None):
        return CommentsItemMapper(item, add_infoproperties).item


class ListTraktRelatedWatchersProperties(ListTraktRelatedProperties):
    container_content = ''

    @cached_property
    def unconfigured_item_data(self):
        return self.get_uncached_items() or {}

    def get_mapped_item(self, item, add_infoproperties=None):
        return WatchersItemMapper(item, add_infoproperties).item


class ListTraktRelatedID(ListTraktStandard):
    list_properties_class = ListTraktRelatedProperties

    def get_items(self, *args, tmdb_id=None, **kwargs):
        self.list_properties.tmdb_id = tmdb_id
        return super().get_items(*args, **kwargs)


class ListTraktRelated(ListTraktRelatedID):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/{trakt_slug}/related'
        list_properties.localize = 32064
        list_properties.sub_type = False
        return list_properties


class ListTraktComments(ListTraktRelatedID):
    list_properties_class = ListTraktRelatedCommentsProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/{trakt_slug}/comments/{trakt_sort}'
        list_properties.localize = 32305
        list_properties.sub_type = False
        list_properties.page_length = 10
        return list_properties

    def get_items(self, *args, sort_by=None, **kwargs):
        self.list_properties.trakt_sort = sort_by or 'newest'
        return super().get_items(*args, **kwargs)


class ListTraktWatchers(ListTraktRelatedID):
    list_properties_class = ListTraktRelatedWatchersProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/{trakt_slug}/watching'
        list_properties.localize = 32065
        list_properties.sub_type = False
        list_properties.page_length = 10
        return list_properties
