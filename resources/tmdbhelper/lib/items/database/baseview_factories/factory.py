# from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type
from jurialmunkey.modimp import importmodule
# from tmdbhelper.lib.addon.logger import kodi_log

"""
BASEVIEW FACTORY

Viewlists to retrieve data from database as a directory of listitems (e.g. cast members list for movie)

"""


def BaseViewFactory(import_attr, tmdb_type, tmdb_id, season=None, episode=None, filters=None, limit=None):
    mediatype = convert_type(tmdb_type, 'dbtype', season=season, episode=episode)
    clsimport = importmodule(
        module_name=f'tmdbhelper.lib.items.database.baseview_factories.concrete_classes.{import_attr}',
        import_attr=f'{mediatype.capitalize()}'
    )
    obj = clsimport()
    obj.mediatype = mediatype
    obj.tmdb_type = tmdb_type
    obj.tmdb_id = tmdb_id
    obj.season = season
    obj.episode = episode
    obj.filters = filters
    obj.limit = limit
    return obj
