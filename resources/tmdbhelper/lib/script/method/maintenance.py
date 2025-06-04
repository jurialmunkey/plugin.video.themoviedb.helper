# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

def vacuum_databases():
    from tmdbhelper.lib.addon.logger import TimerFunc
    from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
    from tmdbhelper.lib.api.tmdb.database import TMDbDatabase
    with TimerFunc('Vacuuming databases:', inline=True):
        ItemDetailsDatabase().execute_sql("VACUUM")
        TMDbDatabase().execute_sql("VACUUM")


def clean_old_databases():
    """ Once-off routine to delete old unused database versions to avoid wasting disk space """
    from tmdbhelper.lib.files.futils import delete_folder
    from tmdbhelper.lib.addon.plugin import get_setting
    # databases = ['database', 'database_v2', 'database_v3', 'database_v4', 'database_v5', 'database_v6']
    databases = ['database', 'database_v2', 'database_v3', 'database_v4', 'database_v5']
    for f in databases:
        delete_folder(f, force=True, check_exists=True)
    save_path = get_setting('image_location', 'str')
    for f in ['blur', 'crop', 'desaturate', 'colors']:
        delete_folder(f, force=True, check_exists=True)
        if not save_path:
            continue
        delete_folder(f'{save_path}{f}/', force=True, check_exists=True, join_addon_data=False)


def recache_kodidb(notification=True, confirmation=False):
    from tmdbhelper.lib.addon.plugin import ADDONPATH
    from tmdbhelper.lib.api.kodi.rpc import KodiLibrary
    from tmdbhelper.lib.addon.logger import TimerFunc
    from xbmcgui import Dialog

    with TimerFunc('KodiLibrary sync took', inline=True):
        KodiLibrary('movie', cache_refresh=True)
        KodiLibrary('tvshow', cache_refresh=True)

    if notification:
        head = 'TMDbHelper'
        data = 'Kodi Library cached to memory'
        icon = f'{ADDONPATH}/icon.png'
        Dialog().notification(head, data, icon=icon)

    if confirmation:
        head = 'TMDbHelper'
        data = 'Kodi Library cached to memory'
        Dialog().ok(head, data)
