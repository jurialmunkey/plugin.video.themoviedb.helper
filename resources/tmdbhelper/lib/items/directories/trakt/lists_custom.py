from jurialmunkey.parser import boolean
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.trakt.lists_standard import (
    ListTraktStandard,
    ListTraktStandardProperties,
)


class ListTraktCustomProperties(ListTraktStandardProperties):
    @cached_property
    def plugin_category(self):
        return self.plugin_name.format(list_name=self.list_name)

    list_type = 'movie,show,season,episode'
    list_sort_map = {
        'rank': 'asc',
        'added': 'desc',
        'title': 'asc',
        'released': 'desc',
        'runtime': 'desc',
        'popularity': 'desc',
        'random': 'desc',
        'percentage': 'desc',
        'my_rating': 'desc',
        'watched': 'desc',
        'collected': 'desc',
    }

    @cached_property
    def unconfigured_item_data(self):
        if not self.owner or get_setting('trakt_cacheownlists'):
            return self.get_cached_items() or {}
        return self.get_uncached_items() or {}

    def get_cache_name_list_prefix(self):
        return [self.class_name, self.tmdb_type, self.user_slug, self.list_slug, self.list_type, self.list_sort]

    @cached_property
    def list_sort(self):
        if self.sort_by not in self.list_sort_map:
            return ''
        if self.sort_how not in ('asc', 'desc'):
            self.sort_how = self.list_sort_map[self.sort_by]
        return f'{self.sort_by}/{self.sort_how}'

    @property
    def url(self):
        url = (
            'lists/{list_slug}/items/{list_type}/{list_sort}'
            if self.user_slug == 'official' else
            'users/{user_slug}/lists/{list_slug}/items/{list_type}/{list_sort}'
        )
        return url.format(list_slug=self.list_slug, user_slug=self.user_slug, list_sort=self.list_sort, list_type=self.list_type)


class ListTraktCustom(ListTraktStandard):

    list_properties_class = ListTraktCustomProperties

    def get_items(
        self, *args,
        list_slug=None,
        user_slug=None,
        list_name=None,
        sort_by=None,
        sort_how=None,
        tmdb_type=None,
        owner=False,
        **kwargs
    ):
        self.list_properties.list_slug = list_slug
        self.list_properties.user_slug = user_slug or 'me'
        self.list_properties.list_name = list_name or list_slug or ''
        self.list_properties.sort_by = sort_by
        self.list_properties.sort_how = sort_how
        self.list_properties.owner = boolean(owner)
        self.list_properties.trakt_authorization = bool(self.list_properties.owner or self.list_properties.user_slug == 'me')
        return super().get_items(*args, tmdb_type=tmdb_type, **kwargs)

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{list_name}'
        list_properties.sub_type = True
        return list_properties
