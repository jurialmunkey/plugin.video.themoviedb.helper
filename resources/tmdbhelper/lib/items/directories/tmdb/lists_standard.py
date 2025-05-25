from tmdbhelper.lib.items.directories.lists_default import ListDefault
from tmdbhelper.lib.addon.plugin import get_setting


ITEMS_LENGTH = 20
PAGES_LENGTH = get_setting('pagemulti_tmdb', 'int') or 1


class ListStandard(ListDefault):
    pass


class ListPopular(ListStandard):
    item_list_request_url = '{tmdb_type}/popular'
    item_list_localize = 32175


class ListTopRated(ListStandard):
    item_list_request_url = '{tmdb_type}/top_rated'
    item_list_localize = 32176


class ListUpcoming(ListStandard):
    item_list_request_url = '{tmdb_type}/upcoming'
    item_list_localize = 32177


class ListTrendingDay(ListStandard):
    item_list_request_url = 'trending/{tmdb_type}/day'
    item_list_plugin_name = '{plural} {localized}'
    item_list_localize = 32178


class ListTrendingWeek(ListStandard):
    item_list_request_url = 'trending/{tmdb_type}/week'
    item_list_plugin_name = '{plural} {localized}'
    item_list_localize = 32179


class ListInTheatres(ListStandard):
    item_list_request_url = '{tmdb_type}/now_playing'
    item_list_plugin_name = '{localized}'
    item_list_localize = 32180


class ListAiringToday(ListStandard):
    item_list_request_url = '{tmdb_type}/airing_today'
    item_list_plugin_name = '{localized}'
    item_list_localize = 32181


class ListCurrentlyAiring(ListStandard):
    item_list_request_url = '{tmdb_type}/on_the_air'
    item_list_plugin_name = '{localized}'
    item_list_localize = 32182


class ListRevenue(ListStandard):
    item_list_request_url = 'discover/{tmdb_type}?sort_by=revenue.desc'
    item_list_localize = 32184


class ListMostVoted(ListStandard):
    item_list_request_url = 'discover/{tmdb_type}?sort_by=vote_count.desc'
    item_list_localize = 32185
