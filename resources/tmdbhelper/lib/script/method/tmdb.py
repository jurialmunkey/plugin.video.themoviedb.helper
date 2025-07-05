# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.script.method.decorators import is_in_kwargs, get_tmdb_id
from tmdbhelper.lib.addon.plugin import get_localized


@is_in_kwargs({'tmdb_type': ['movie', 'tv']})
@get_tmdb_id
def sync_tmdb(tmdb_type=None, tmdb_id=None, season=None, episode=None, sync_type=None, **kwargs):
    """ Open sync trakt menu for item """
    from tmdbhelper.lib.script.sync.tmdb.menu import sync_item
    sync_item(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode, sync_type=sync_type)


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
    from tmdbhelper.lib.addon.dialog import ProgressDialog
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

    with ProgressDialog(
        title=f'{get_localized(32387).format(mediatype.capitalize())}',
        total=(len(routes[mediatype]['baseitems']) + len(routes[mediatype]['tables']) + 1),
        background=False,
    ) as progress_dialog:
        database = ItemDetailsDatabase()
        with TimerFunc(f'Deleting mediatype {mediatype}:', inline=True):
            for i in routes[mediatype]['baseitems']:
                statement = f'DELETE FROM baseitem WHERE mediatype="{i}"'
                progress_dialog.update(statement)
                database.execute_sql(statement)
            for i in routes[mediatype]['tables']:
                statement = f'DELETE FROM {i}'
                progress_dialog.update(statement)
                database.execute_sql(statement)
            progress_dialog.update('Vacuuming database...')
            database.execute_sql('VACUUM')

    if confirmation:
        head = get_localized(32387).format(mediatype.capitalize())
        data = get_localized(32051).format(mediatype)
        Dialog().ok(head, data)
