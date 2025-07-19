from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.trakt.lists_standard import (
    ListTraktStandardProperties,
    ListTraktStandard,
)


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
        query=None,
        years=None,
        languages=None,
        countries=None,
        runtimes=None,
        studio_ids=None,
        certifications=None,
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
                ('query', query),
                ('years', years),
                ('languages', languages),
                ('countries', countries),
                ('runtimes', runtimes),
                ('studio_ids', studio_ids),
                ('certifications', certifications),
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


class ListTraktTrending(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/trending'
        list_properties.localize = 32204
        list_properties.sub_type = True
        return list_properties


class ListTraktPopular(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/popular'
        list_properties.localize = 32175
        list_properties.sub_type = False
        return list_properties


class ListTraktMostPlayed(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/played/weekly'
        list_properties.localize = 32205
        list_properties.sub_type = True
        return list_properties


class ListTraktMostWatched(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/watched/weekly'
        list_properties.localize = 32414
        list_properties.sub_type = True
        return list_properties


class ListTraktAnticipated(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/anticipated'
        list_properties.localize = 32206
        list_properties.sub_type = True
        return list_properties
