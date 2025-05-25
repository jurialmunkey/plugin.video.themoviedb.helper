from tmdbhelper.lib.items.directories.lists_default import ListDefault
from tmdbhelper.lib.addon.plugin import get_setting


ITEMS_LENGTH = 20
PAGES_LENGTH = get_setting('pagemulti_tmdb', 'int') or 1


class ListStandard(ListDefault):
    pass


class ListPopular(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/popular'
        list_properties.localize = 32175
        return list_properties


class ListTopRated(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/top_rated'
        list_properties.localize = 32176
        return list_properties


class ListUpcoming(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/upcoming'
        list_properties.localize = 32177
        return list_properties


class ListTrendingDay(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'trending/{tmdb_type}/day'
        list_properties.plugin_name = '{plural} {localized}'
        list_properties.localize = 32178
        return list_properties


class ListTrendingWeek(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'trending/{tmdb_type}/week'
        list_properties.plugin_name = '{plural} {localized}'
        list_properties.localize = 32179
        return list_properties


class ListInTheatres(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/now_playing'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32180
        return list_properties


class ListAiringToday(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/airing_today'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32181
        return list_properties


class ListCurrentlyAiring(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/on_the_air'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32182
        return list_properties


class ListRevenue(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'discover/{tmdb_type}?sort_by=revenue.desc'
        list_properties.localize = 32184
        return list_properties


class ListMostVoted(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'discover/{tmdb_type}?sort_by=vote_count.desc'
        list_properties.localize = 32185
        return list_properties
