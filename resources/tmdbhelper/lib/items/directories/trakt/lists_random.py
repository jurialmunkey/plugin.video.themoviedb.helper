import random
from jurialmunkey.parser import try_int
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type
from tmdbhelper.lib.items.directories.trakt.lists_filtered import (
    ListTraktTrending,
    ListTraktPopular,
    ListTraktMostPlayed,
    ListTraktMostWatched,
    ListTraktAnticipated,
)
from tmdbhelper.lib.items.directories.trakt.lists_standard import (
    ListTraktStandard,
    ListTraktStandardProperties,
)
from tmdbhelper.lib.items.directories.trakt.lists_custom import ListTraktCustom
from tmdbhelper.lib.items.directories.trakt.lists_static import (
    ListTraktStaticTrending,
    ListTraktStaticPopular,
    ListTraktStaticLiked,
    ListTraktStaticOwned,
)


class ListTraktRandomisedProperties(ListTraktStandardProperties):

    @cached_property
    def limit(self):
        return self.pmax * 40  # Use double normal limit to get a decent sample size

    @cached_property
    def sample_limit(self):
        return min((self.pmax * 20), len(self.filtered_items))  # Make sure we dont try to sample more items than we have

    @cached_property
    def sorted_items(self):
        import random
        return random.sample(self.filtered_items, self.sample_limit)


class ListTraktRandomised(ListTraktStandard):

    list_properties_class = ListTraktRandomisedProperties
    pagination = False

    def get_items(self, *args, length=None, tmdb_type=None, **kwargs):
        length = try_int(length)

        if tmdb_type == 'both':
            import random
            items = []
            items += super().get_items(*args, length=length, tmdb_type='movie', **kwargs) or []
            self.list_properties = self.configure_list_properties(self.list_properties_class())
            items += super().get_items(*args, length=length, tmdb_type='tv', **kwargs) or []
            items = random.sample(items, self.list_properties.sample_limit)
            self.plugin_category = self.list_properties.plugin_name.format(localized=self.list_properties.localized, plural=convert_type('both', 'plural'))
            self.container_content = convert_type('both', 'container', items=items)
            return items

        return super().get_items(*args, length=length, tmdb_type=tmdb_type, **kwargs)


class ListTraktTrendingRandomised(ListTraktRandomised, ListTraktTrending):
    pass


class ListTraktPopularRandomised(ListTraktRandomised, ListTraktPopular):
    pass


class ListTraktMostPlayedRandomised(ListTraktRandomised, ListTraktMostPlayed):
    pass


class ListTraktMostWatchedRandomised(ListTraktRandomised, ListTraktMostWatched):
    pass


class ListTraktAnticipatedRandomised(ListTraktRandomised, ListTraktAnticipated):
    pass


class ListTraktStaticTrendingRandomised(ListTraktCustom):
    sample_class = ListTraktStaticTrending

    def get_items(self, *args, tmdb_type=None, **kwargs):
        item = random.choice(self.sample_class(-1, 'nextpage=false').get_items(tmdb_type='both'))
        return super().get_items(**item['params'])


class ListTraktStaticPopularRandomised(ListTraktStaticTrendingRandomised):
    sample_class = ListTraktStaticPopular


class ListTraktStaticLikedRandomised(ListTraktStaticTrendingRandomised):
    sample_class = ListTraktStaticLiked


class ListTraktStaticOwnedRandomised(ListTraktStaticTrendingRandomised):
    sample_class = ListTraktStaticOwned
