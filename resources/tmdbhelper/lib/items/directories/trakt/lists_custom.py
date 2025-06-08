from jurialmunkey.parser import try_int
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.directories.trakt.lists_standard import (
    ListTraktStandard,
    ListTraktStandardProperties,
    PAGES_LENGTH
)


class ListTraktCustomProperties(ListTraktStandardProperties):

    list_sort_default = 'rank'
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

    def get_cache_name_list_prefix(self):
        return [self.class_name, self.tmdb_type, self.list_slug, self.user_slug, self.list_sort]

    @cached_property
    def list_sort(self):
        if self.sort_by not in self.list_sort_map:
            self.sort_by = self.list_sort_default
        if self.sort_how not in ('asc', 'desc'):
            self.sort_how = self.list_sort_map[self.sort_by]
        return f'{self.sort_by}/{self.sort_how}'

    @property
    def url(self):
        url = (
            'lists/{list_slug}/items/{list_sort}'
            if self.user_slug == 'official' else
            'users/{user_slug}/lists/{list_slug}/items/{list_sort}'
        )
        return url.format(list_slug=self.list_slug, user_slug=self.user_slug, list_sort=self.list_sort)


class ListTraktCustom(ListTraktStandard):

    list_properties_class = ListTraktCustomProperties

    def get_items(self, *args, length=None, list_slug=None, user_slug=None, sort_by=None, sort_how=None, **kwargs):
        self.list_properties.list_slug = list_slug
        self.list_properties.user_slug = user_slug or 'me'
        self.list_properties.sort_by = sort_by or 'rank'
        self.list_properties.sort_how = sort_how
        return super().get_items(*args, length=try_int(length) or PAGES_LENGTH, **kwargs)

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32204
        list_properties.sub_type = True
        return list_properties
