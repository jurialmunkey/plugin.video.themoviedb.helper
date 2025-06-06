import random
from jurialmunkey.parser import try_int
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting, get_localized, convert_type
from tmdbhelper.lib.items.directories.tmdb.lists_related import ListRecommendations
from tmdbhelper.lib.items.directories.trakt.lists_sync import ListMostWatched, ListHistory
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
    PAGES_LENGTH
)


class ListTraktRandomisedProperties(ListTraktStandardProperties):

    @cached_property
    def limit(self):
        return self.length * 40  # Use double normal limit to get a decent sample size

    @cached_property
    def sample_limit(self):
        return min((self.length * 20), len(self.filtered_items))  # Make sure we dont try to sample more items than we have

    @cached_property
    def sorted_items(self):
        import random
        return random.sample(self.filtered_items, self.sample_limit)


class ListTraktRandomised(ListTraktStandard):

    list_properties_class = ListTraktRandomisedProperties
    pagination = False

    def get_items(self, *args, length=None, tmdb_type=None, **kwargs):
        length = try_int(length) or PAGES_LENGTH

        if tmdb_type == 'both':
            import random
            items = []
            items += super().get_items(*args, length=length, tmdb_type='movie', **kwargs) or []
            self.list_properties = self.configure_list_properties(self.list_properties_class())
            items += super().get_items(*args, length=length, tmdb_type='tv', **kwargs) or []
            items = random.sample(items, min((length * 20), len(items)))
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


class ListRandomBecauseYouWatched(ListRecommendations):
    def get_items(self, info, tmdb_type, **kwargs):

        func = ListMostWatched if info == 'trakt_becausemostwatched' else ListHistory

        watched_items = func(-1, self.paramstring)
        watched_items.list_properties.next_page = False
        watched_items = watched_items.get_items(tmdb_type=tmdb_type)

        if not watched_items:
            return

        limit = get_setting('trakt_becausewatchedseed', 'int') or 5
        watched_items = watched_items[:limit]

        item = watched_items[random.randint(0, len(watched_items) - 1)]

        try:
            label = item['label']
            tmdb_type = item['params']['tmdb_type']
            tmdb_id = item['params']['tmdb_id']
        except (AttributeError, KeyError):
            return

        localized = get_localized(32288)

        params = {
            'info': 'recommendations',
            'tmdb_type': tmdb_type,
            'tmdb_id': tmdb_id,
        }

        items = super().get_items(**params)

        self.plugin_category = f'{localized} {label}'
        self.property_params.update(
            {
                'widget.label': label,
                'widget.tmdb_type': tmdb_type,
                'widget.tmdb_id': tmdb_id,
                'widget.category': localized,
            }
        )

        return items
