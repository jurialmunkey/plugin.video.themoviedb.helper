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
