from jurialmunkey.parser import try_int
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.directories.trakt.lists_standard import (
    ListTraktStandard,
    ListTraktStandardProperties,
    PAGES_LENGTH
)


class ListTraktRelatedProperties(ListTraktStandardProperties):
    @property
    def url(self):
        return self.request_url.format(
            trakt_type=self.trakt_type,
            trakt_slug=self.trakt_slug
        )

    def get_cache_name_list_prefix(self):
        return [self.class_name, self.tmdb_type, self.tmdb_id]

    @cached_property
    def trakt_slug(self):
        return self.trakt_api.get_id(self.tmdb_id, 'tmdb', trakt_type=self.trakt_type, output_type='slug')


class ListTraktRelated(ListTraktStandard):
    list_properties_class = ListTraktRelatedProperties

    def get_items(self, *args, tmdb_id=None, length=None, **kwargs):
        self.list_properties.tmdb_id = tmdb_id
        return super().get_items(*args, length=try_int(length) or PAGES_LENGTH, **kwargs)

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/{trakt_slug}/related'
        list_properties.localize = 32064
        list_properties.sub_type = False
        return list_properties
