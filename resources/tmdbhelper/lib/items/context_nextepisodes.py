from urllib.parse import parse_qsl, urlencode
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import boolean
from tmdbhelper.lib.addon.consts import ROUTE_NOID
from tmdbhelper.lib.addon.plugin import PLUGINPATH


class BrowseNextEpisodesContextMenu:
    """Open a show-list directory with next-episode replacement enabled."""

    show_routes = (
        'all_tvshows',
        'stars_in_tvshows',
        'stars_in_both',
        'crew_in_tvshows',
        'crew_in_both',
        'credits_in_both',
    )
    mixed_routes = (
        'tmdb_list',
        'tmdb_v4_watchlist',
        'trakt_userlist',
        'mdblist_locallist',
        'mdblist_userlist',
        'tvdb_award_category',
        'gemini_recommendations',
    )
    typed_routes = (
        'popular',
        'top_rated',
        'trending_day',
        'trending_week',
        'airing_today',
        'on_the_air',
        'most_voted',
        'search',
        'discover',
        'recommendations',
        'similar',
        'random_genres',
        'random_providers',
        'random_networks',
        'sync_collection',
        'sync_watchlist',
        'sync_watchlist_released',
        'sync_watchlist_anticipated',
        'sync_history',
        'sync_watchedon',
        'sync_mostwatched',
        'sync_dropped',
        'sync_inprogress',
        'sync_towatch',
        'sync_becauseyouwatched',
        'sync_becausemostwatched',
        'tmdb_recommendations',
        'tmdb_favorites',
        'tmdb_rated',
        'trakt_favorites',
        'trakt_trending',
        'trakt_popular',
        'trakt_mostplayed',
        'trakt_mostviewers',
        'trakt_anticipated',
        'trakt_recommendations',
        'trakt_related',
        'trakt_random_trendinglists',
        'trakt_random_popularlists',
        'trakt_random_likedlists',
        'trakt_random_mylists',
        'trakt_random_trending',
        'trakt_random_popular',
        'trakt_random_mostplayed',
        'trakt_random_mostviewers',
        'trakt_random_anticipated',
        'mdblist_officiallist',
        'mdblist_streamingchart',
        'tvdb_genre',
    )

    def __init__(self, listitem):
        self.listitem = listitem

    @cached_property
    def path(self):
        return self.listitem.url

    @cached_property
    def query_parts(self):
        return self.path.partition('?')[2].split('&&')

    @cached_property
    def params(self):
        return dict(parse_qsl(self.query_parts[0], keep_blank_values=True))

    @cached_property
    def route(self):
        return self.get_route()

    def get_route(self):
        route = self.params.get('parent_info') or self.params.get('info', '')
        definition = ROUTE_NOID.get(route, {})
        if 'redirect' in definition:
            return definition['redirect']
        sync_route = route.replace('trakt_', 'sync_', 1)
        if route.startswith('trakt_') and definition and definition == ROUTE_NOID.get(sync_route):
            return sync_route
        return route

    @cached_property
    def is_supported(self):
        return self.get_is_supported()

    def get_is_supported(self):
        if not self.listitem.is_folder or self.listitem.next_page:
            return False
        if self.path.partition('?')[0].rstrip('/') != PLUGINPATH.rstrip('/'):
            return False
        if boolean(self.params.get('nextepisodes', False)) or boolean(self.params.get('episodes', False)):
            return False
        if self.params.get('method') or self.params.get('clear_cache'):
            return False
        if self.route in self.show_routes:
            return True
        item_type = self.params.get('tmdb_type')
        if self.route in self.mixed_routes:
            return item_type in (None, '', 'both', 'tv')
        return self.route in self.typed_routes and item_type in ('tv', 'both')

    @cached_property
    def url(self):
        return self.get_url()

    def get_url(self):
        params = dict(self.params, nextepisodes='true')
        query = '&&'.join([urlencode(params), *self.query_parts[1:]])
        return f'{PLUGINPATH}?{query}'

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        if not self.is_supported:
            return []
        return [
            (
                '$ADDON[plugin.video.themoviedb.helper 32770]',
                f'Container.Update("{self.url}")',
            ),
        ]
