# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.script.method.decorators import is_in_kwargs, get_tmdb_id


@is_in_kwargs({'tmdb_type': ['movie', 'tv']})
@get_tmdb_id
def sync_trakt(tmdb_type=None, tmdb_id=None, season=None, episode=None, sync_type=None, **kwargs):
    """ Open sync trakt menu for item """
    from tmdbhelper.lib.script.sync.trakt.menu import sync_item
    sync_item(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode, sync_type=sync_type)


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
    from tmdbhelper.lib.items.directories.trakt.lists_sorting import get_sort_methods
    sort_methods = get_sort_methods(kwargs['info'])
    return select_sort_list(sort_methods, **kwargs)


def sort_mdblist(**kwargs):
    from tmdbhelper.lib.items.directories.mdblist.lists_sorting import get_sort_methods
    sort_methods = get_sort_methods(kwargs['info'])
    return select_sort_list(sort_methods, **kwargs)


def select_sort_list(sort_methods, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.plugin import executebuiltin, format_folderpath, encode_url
    x = Dialog().contextmenu([i['name'] for i in sort_methods])
    if x == -1:
        return
    for k, v in sort_methods[x]['params'].items():
        kwargs[k] = v
    executebuiltin(format_folderpath(encode_url(**kwargs)))


def invalidate_trakt_sync(invalidate_trakt_sync, notification=True, **kwargs):
    import itertools
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.dialog import ProgressDialog
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

    def invalidate_sync(progress_dialog=None):
        # init database
        progress_dialog.update('Initialise database') if progress_dialog else None
        database = ItemDetailsDatabase()

        # delete column data for datatypes
        database_keys = tuple((_build_keys(i) for i in route['data']))
        database_keys = tuple(itertools.chain.from_iterable(database_keys))
        progress_dialog.update(f'Deleting simplecache keys: {database_keys}') if progress_dialog else None
        database.del_column_values(table='simplecache', keys=database_keys)

        # clean up corresponding last activity values
        database_lactivities_ids = tuple((_build_lactivities_ids(i) for i in route['data']))
        database_lactivities_ids = tuple(itertools.chain.from_iterable(database_lactivities_ids))
        progress_dialog.update(f'Deleting last activities keys: {database_lactivities_ids}') if progress_dialog else None
        for x, item_id in enumerate(database_lactivities_ids, 1):
            database.del_item(table='lactivities', item_id=item_id)

    # show dialog or not
    if not notification:
        invalidate_sync()
        return

    with ProgressDialog(
        title=get_localized(32022),
        total=4,
    ) as progress_dialog:
        invalidate_sync(progress_dialog)
    Dialog().ok(
        get_localized(32026),
        get_localized(32027).format(route['name'].lower())
    )


def authenticate_trakt(**kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI(force=True)
    invalidate_trakt_sync('all', notification=False)


def revoke_trakt(**kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI().logout()
    invalidate_trakt_sync('all', notification=False)


def get_stats(**kwargs):
    from tmdbhelper.lib.query.database.database import FindQueriesDatabase
    from jurialmunkey.window import get_property

    stats = FindQueriesDatabase().get_trakt_stats()
    if not stats:
        return

    combined_stats = {}

    def set_proptime(prop_name, v):
        days, minutes = divmod(int(v), 60 * 24)
        hour, minutes = divmod(int(minutes), 60)
        get_property(f'{prop_name}_d', set_property=f'{days}')
        get_property(f'{prop_name}_h', set_property=f'{hour}')
        get_property(f'{prop_name}_mm', set_property=f'{minutes}')

    def set_property(base_name, stat_name, stat_type, v):
        prop_name = f'{base_name}.{stat_type}.{stat_name}'
        get_property(prop_name, set_property=f'{v}')
        set_proptime(prop_name, v) if stat_name == 'minutes' else None

    def set_combined(stat_name, v):
        stat_name = f'{stat_name}_total'
        combined_stats.setdefault(stat_name, 0)
        combined_stats[stat_name] += v

    def set_allstats(d, base_name, update_combined=True):
        for k, v in d.items():
            stat_name, stat_type = k.split('_')
            set_property(base_name, stat_name, stat_type, v)
            set_combined(stat_name, v) if update_combined else None

    set_allstats(stats, 'TraktStats')
    set_allstats(combined_stats, 'TraktStats', update_combined=False)
