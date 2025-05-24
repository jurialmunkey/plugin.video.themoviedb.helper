# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.script.method.decorators import is_in_kwargs, get_tmdb_id
from tmdbhelper.lib.addon.plugin import get_localized


TMDB_USER_API_ROUTES = {
    # 'add_favorite': {'func': 'add_favorite', 'name': get_localized(32490)},
    # 'add_watchlist': {'func': 'add_watchlist', 'name': get_localized(32291)},
    # 'del_favorite': {'func': 'del_favorite', 'name': get_localized(32491)},
    # 'del_watchlist': {'func': 'del_watchlist', 'name': get_localized(32292)},
    'modify_watchlist': {'func': 'modify_watchlist', 'name': get_localized(32526)},
    'modify_favorite': {'func': 'modify_favorite', 'name': get_localized(32525)},
    'modify_list': {'func': 'modify_list', 'name': get_localized(32523)},
}


def select_sync_type():
    choices = [k for k in TMDB_USER_API_ROUTES.keys()]
    d_items = [TMDB_USER_API_ROUTES[k]['name'] for k in choices]
    from xbmcgui import Dialog
    x = Dialog().select(get_localized(32522), d_items)
    if x == -1:
        return
    return choices[x]


@is_in_kwargs({'tmdb_type': ['movie', 'tv']})
@get_tmdb_id
def sync_tmdb(tmdb_type=None, tmdb_id=None, season=None, episode=None, sync_type=None, **kwargs):
    sync_type = sync_type or select_sync_type()
    if sync_type not in TMDB_USER_API_ROUTES:
        return
    return sync_tmdb_item(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode, sync_type=sync_type, **kwargs)


def sync_tmdb_item(tmdb_type=None, tmdb_id=None, season=None, episode=None, sync_type=None, **kwargs):
    from tmdbhelper.lib.api.tmdb.users import TMDbUser
    tmdb_user_api = TMDbUser()
    func = getattr(tmdb_user_api, TMDB_USER_API_ROUTES[sync_type]['func'])
    func(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode)


def refresh_item(tmdb_type, tmdb_id, season=None, episode=None, **kwargs):
    import xbmcgui
    from tmdbhelper.lib.addon.dialog import BusyDialog
    from tmdbhelper.lib.script.method.kodi_utils import container_refresh
    from tmdbhelper.lib.addon.plugin import get_localized, convert_type
    from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory

    def refresh_item_factory(season=None, episode=None):
        mediatype = convert_type(tmdb_type, 'dbtype', season, episode)
        sync = BaseItemFactory(mediatype)
        sync.tmdb_id = tmdb_id
        sync.season = season
        sync.episode = episode
        sync.cache_refresh = 'force'
        sync.data

    with BusyDialog():
        refresh_item_factory(season, episode)

        if episode is not None:
            refresh_item_factory(season)

        if season is not None:
            refresh_item_factory()

    xbmcgui.Dialog().ok(get_localized(32233), f'{tmdb_type} {tmdb_id} {season if season else ""} {episode if episode else ""}')
    container_refresh()


def delete_itemtype(mediatype=None, confirmation=True, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.dialog import BusyDialog
    from tmdbhelper.lib.addon.logger import TimerFunc
    from tmdbhelper.lib.items.database.database import ItemDetailsDatabase

    routes = {
        'movie': {
            'baseitems': ('movie', 'collection', ),
            'tables': (),
        },
        'tvshow': {
            'baseitems': ('tvshow', 'season', 'episode', ),
            'tables': (),
        },
        'all': {
            'baseitems': ('person', 'tvshow', 'season', 'episode', 'movie', 'collection', ),
            'tables': (),
        },
    }

    if not mediatype:
        choices = [i for i in routes.keys()]
        x = Dialog().select('Choose mediatype', choices)
        if x == -1:
            return
        mediatype = choices[x]

    if mediatype not in routes:
        raise Exception(f'The mediatype {mediatype} is not valid!')

    if not Dialog().yesno(
        (
            f'{get_localized(32387).format(mediatype.capitalize())}: '
            f'{get_localized(19194)}'
        ),
        (
            f'[B][COLOR=red][UPPERCASE]{get_localized(14117)}[/UPPERCASE][/COLOR][/B] - '
            f'{get_localized(32053)}'
        )
    ):
        return

    with BusyDialog():
        database = ItemDetailsDatabase()
        with TimerFunc(f'Deleting mediatype {mediatype}:', inline=True):
            for i in routes[mediatype]['baseitems']:
                database.execute_sql(f'DELETE FROM baseitem WHERE mediatype="{i}"')
            for i in routes[mediatype]['tables']:
                database.execute_sql(f'DELETE FROM {i}')
            database.execute_sql('VACUUM')

    if confirmation:
        head = get_localized(32387).format(mediatype.capitalize())
        data = get_localized(32051).format(mediatype)
        Dialog().ok(head, data)
