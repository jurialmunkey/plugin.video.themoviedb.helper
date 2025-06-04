# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.script.method.decorators import is_in_kwargs, get_tmdb_id


@is_in_kwargs({'tmdb_type': ['movie', 'tv']})
@get_tmdb_id
def sync_trakt(tmdb_type=None, tmdb_id=None, season=None, episode=None, sync_type=None, **kwargs):
    """ Open sync trakt menu for item """
    from tmdbhelper.lib.script.sync.menu import sync_trakt_item
    sync_trakt_item(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode, sync_type=sync_type)


@is_in_kwargs({'like_list': True})
def like_list(like_list=None, user_slug=None, delete=False, **kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    user_slug = user_slug or 'me'
    TraktAPI().trakt_syncdata.like_userlist(user_slug=user_slug, list_slug=like_list, confirmation=True, delete=delete)
    if not delete:
        return
    from tmdbhelper.lib.script.method.kodi_utils import container_refresh
    container_refresh()


@is_in_kwargs({'delete_list': True})
def delete_list(delete_list=None, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.addon.plugin import get_localized
    if not Dialog().yesno(get_localized(32358), get_localized(32357).format(delete_list)):
        return
    TraktAPI().delete_response('users/me/lists', delete_list)
    from tmdbhelper.lib.script.method.kodi_utils import container_refresh
    container_refresh()


@is_in_kwargs({'rename_list': True})
def rename_list(rename_list=None, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.addon.plugin import get_localized
    name = Dialog().input(get_localized(32359))
    if not name:
        return
    TraktAPI().post_response('users/me/lists', rename_list, postdata={'name': name}, response_method='put')
    from tmdbhelper.lib.script.method.kodi_utils import container_refresh
    container_refresh()


def sort_list(**kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.plugin import executebuiltin, format_folderpath, encode_url
    from tmdbhelper.lib.api.trakt.sorting import get_sort_methods
    sort_methods = get_sort_methods(kwargs['info'])
    x = Dialog().contextmenu([i['name'] for i in sort_methods])
    if x == -1:
        return
    for k, v in sort_methods[x]['params'].items():
        kwargs[k] = v
    executebuiltin(format_folderpath(encode_url(**kwargs)))


def invalidate_trakt_sync(invalidate_trakt_sync, notification=True, **kwargs):
    import itertools
    from xbmcgui import Dialog
    from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
    from tmdbhelper.lib.addon.plugin import get_localized
    from tmdbhelper.lib.api.trakt.sync.datatype import (
        SyncWatched, SyncPlayback, SyncNextEpisodes, SyncAllNextEpisodes,
        SyncCollection, SyncWatchlist, SyncFavorites, SyncRatings,
        SyncHiddenProgressWatched, SyncHiddenProgressCollected,
        SyncHiddenCalendar, SyncHiddenDropped,
    )

    def _build_keys(datatype):
        return tuple((
            f'{datatype.key_prefix}_{k}' if datatype.key_prefix else k
            for k in datatype.keys
        ))

    def _build_lactivities_ids(datatype, item_types=('movie', 'show', 'episode')):
        return tuple((f'{item_type}.{datatype.method}' for item_type in item_types))

    routes = {
        'watchedprogress': {
            'name': get_localized(32035),
            'data': (SyncWatched, SyncPlayback, SyncNextEpisodes, SyncAllNextEpisodes),
        },
        'collection': {
            'name': get_localized(32192),
            'data': (SyncCollection, ),
        },
        'watchlist': {
            'name': get_localized(32193),
            'data': (SyncWatchlist, ),
        },
        'favorites': {
            'name': get_localized(1036),
            'data': (SyncFavorites, ),
        },
        'ratings': {
            'name': get_localized(32028),
            'data': (SyncRatings, ),
        },
        'hidden': {
            'name': get_localized(32036),
            'data': (
                SyncHiddenProgressWatched, SyncHiddenProgressCollected,
                SyncHiddenCalendar, SyncHiddenDropped,
            ),
        },
        'all': {
            'name': get_localized(593),
            'data': (
                SyncWatched, SyncPlayback, SyncNextEpisodes, SyncAllNextEpisodes,
                SyncCollection, SyncWatchlist, SyncFavorites, SyncRatings,
                SyncHiddenProgressWatched, SyncHiddenProgressCollected,
                SyncHiddenCalendar, SyncHiddenDropped,
            ),
        },
    }

    # ask user to choose route if not specified
    try:
        route = routes[invalidate_trakt_sync]
    except KeyError:
        route_keys = [k for k in routes.keys()]
        route_list = [v['name'] for k, v in routes.items()]
        x = Dialog().select('Sync', route_list)
        if x == -1:
            return
        route = routes[route_keys[x]]

    # init database
    database = ItemDetailsDatabase()

    # delete column data for datatypes
    database_keys = tuple((_build_keys(i) for i in route['data']))
    database_keys = tuple(itertools.chain.from_iterable(database_keys))
    database.del_column_values(table='simplecache', keys=database_keys)

    # clean up corresponding last activity values
    database_lactivities_ids = tuple((_build_lactivities_ids(i) for i in route['data']))
    database_lactivities_ids = tuple(itertools.chain.from_iterable(database_lactivities_ids))
    for x, item_id in enumerate(database_lactivities_ids, 1):
        database.del_item(table='lactivities', item_id=item_id)

    # notify of success
    if not notification:
        return
    Dialog().ok(get_localized(32026), get_localized(32027).format(route['name'].lower()))


def authenticate_trakt(**kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI(force=True)
    invalidate_trakt_sync('all', notification=False)


def revoke_trakt(**kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI().logout()
    invalidate_trakt_sync('all', notification=False)


def get_stats(**kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from jurialmunkey.window import get_property

    response = TraktAPI().get_request('users/me/stats', cache_days=0.015)
    if not response:
        return

    combined_stats = {}

    def _set_property(name, value, key):
        get_property(name, set_property=f'{value}')
        if not isinstance(value, int):
            return
        combined_stats.setdefault(key, 0)
        combined_stats[key] += value

    def _set_stats(d, prop):
        for k, v in d.items():
            name = f'{prop}.{k}'
            if isinstance(v, dict):
                _set_stats(v, name)
                continue
            _set_property(name, v, key=k)
            if k == 'minutes':
                days, minutes = divmod(int(v), 60 * 24)
                hours, minutes = divmod(int(minutes), 60)
                _set_property(f'{name}_d', days, key=k)
                _set_property(f'{name}_h', hours, key=k)
                _set_property(f'{name}_mm', minutes, key=k)

    _set_stats(response, 'TraktStats')
    _set_stats(combined_stats, 'TraktStats.Total')

    for i in ('movie', 'episode', ''):
        path = f'users/me/history/{i}s' if i else 'users/me/history'
        response = TraktAPI().get_request(path, cache_days=0.015, limit=1)
        if not response:
            continue
        for x, j in enumerate(response):
            _set_stats(j, f'TraktStats.Recent{i}.{x}')
