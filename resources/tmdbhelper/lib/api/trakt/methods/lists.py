from tmdbhelper.lib.api.trakt.api import is_authorized
from tmdbhelper.lib.files.bcache import use_simple_cache
from tmdbhelper.lib.addon.consts import CACHE_SHORT


@use_simple_cache(cache_days=CACHE_SHORT)
def get_sorted_list(
        self, path, sort_by=None, sort_how=None, extended=None, trakt_type=None, permitted_types=None, cache_refresh=False, cache_only=False,
        genres=None, years=None, query=None, languages=None, countries=None, runtimes=None, studio_ids=None
):
    response = self.get_response(
        path, extended=extended, limit=4095, cache_only=cache_only,
        genres=genres, years=years, query=query, languages=languages, countries=countries, runtimes=runtimes, studio_ids=studio_ids
    )

    if not response:
        return

    def _get_sorted_list_items():
        if extended == 'sync':
            return self.merge_sync_sort(response.json())
        if extended == 'inprogress':
            return self.filter_inprogress(self.merge_sync_sort(response.json()))
        return response.json()

    items = _get_sorted_list_items()

    from tmdbhelper.lib.api.trakt.items import TraktItems
    return TraktItems(items, headers=response.headers).build_items(
        sort_by=sort_by or response.headers.get('x-sort-by'),
        sort_how=sort_how or response.headers.get('x-sort-how'),
        permitted_types=permitted_types)


@is_authorized
def get_custom_list(
        self, list_slug, user_slug=None, page: int = 1, limit: int = None, params=None, authorize=False,
        sort_by=None, sort_how=None, extended=None, owner=False, always_refresh=True, cache_only=False
):

    limit = limit or self.item_limit

    if user_slug == 'official':
        path = f'lists/{list_slug}/items'
    else:
        path = f'users/{user_slug or "me"}/lists/{list_slug}/items'

    # Refresh cache on first page for user list because it might've changed
    from jurialmunkey.parser import try_int
    cache_refresh = True if always_refresh and try_int(page, fallback=1) == 1 else False

    sorted_items = self.get_sorted_list(
        path, sort_by, sort_how, extended,
        permitted_types=['movie', 'show', 'person', 'episode'],
        cache_refresh=cache_refresh, cache_only=cache_only
    ) or {}

    from tmdbhelper.lib.items.pages import PaginatedItems
    paginated_items = PaginatedItems(
        items=sorted_items.get('items', []), page=page, limit=limit)

    return {
        'items': paginated_items.items,
        'movies': sorted_items.get('movies', []),
        'shows': sorted_items.get('shows', []),
        'persons': sorted_items.get('persons', []),
        'next_page': paginated_items.next_page}


def get_list_of_genres(self, trakt_type):
    if trakt_type not in ['movie', 'show']:
        return

    response = self.get_response(f'genres/{trakt_type}s')

    if not response:
        return

    from tmdbhelper.lib.addon.plugin import get_setting, ADDONPATH

    items = []

    for i in response.json():
        item = {}
        item['label'] = i.get('name')
        item['infolabels'] = {}
        item['infoproperties'] = {}
        item['art'] = {
            'icon': f'{ADDONPATH}/resources/icons/trakt/genres.png'
        }
        item['params'] = {
            'info': 'dir_trakt_genre',
            'genre': i.get('slug'),
            'tmdb_type': 'movie' if trakt_type == 'movie' else 'tv'
        }
        item['unique_ids'] = {'slug': i.get('slug')}
        items.append(item)

    def _add_icon(i):
        import xbmcvfs
        slug = i['unique_ids']['slug']
        if not slug:
            return i
        filepath = xbmcvfs.validatePath(xbmcvfs.translatePath(f'{icon_path}/{slug}.png'))
        if not xbmcvfs.exists(filepath):
            return i
        i['art']['icon'] = filepath
        return i

    icon_path = get_setting('trakt_genre_icon_location', 'str')

    if icon_path:
        items = [_add_icon(i) for i in items]

    return items


def merge_sync_sort(self, items):
    """ Get sync dict sorted by slugs then merge slug into list """
    sync = {}
    sync.update(self.get_sync('watched', 'show', 'slug', extended='full'))
    sync.update(self.get_sync('watched', 'movie', 'slug'))
    return [dict(i, **sync.get(i.get(i.get('type'), {}).get('ids', {}).get('slug'), {})) for i in items]


def filter_inprogress(self, items):
    """ Filter list so that it only returns inprogress shows """
    inprogress = self.get_inprogress_shows() or []
    inprogress = [i['show']['ids']['slug'] for i in inprogress if i.get('show', {}).get('ids', {}).get('slug')]
    if not inprogress:
        return
    items = [i for i in items if i.get('show', {}).get('ids', {}).get('slug') in inprogress]
    return items


@use_simple_cache(cache_days=CACHE_SHORT)
def get_imdb_top250(self, id_type=None, trakt_type='movie'):
    paths = {
        'movie': 'users/justin/lists/imdb-top-rated-movies/items',
        'show': 'users/justin/lists/imdb-top-rated-tv-shows/items'}
    try:
        response = self.get_response(paths[trakt_type], limit=4095)
        from tmdbhelper.lib.api.trakt.items import TraktItems
        sorted_items = TraktItems(response.json() if response else []).sort_items('rank', 'asc') or []
        return [i[trakt_type]['ids'][id_type] for i in sorted_items]
    except KeyError:
        return []
