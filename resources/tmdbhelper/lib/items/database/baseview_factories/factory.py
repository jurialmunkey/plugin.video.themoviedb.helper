# from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type
from jurialmunkey.modimp import importmodule
from jurialmunkey.parser import try_int
# from tmdbhelper.lib.addon.logger import kodi_log

"""
BASEVIEW FACTORY

Viewlists to retrieve data from database as a directory of listitems (e.g. cast members list for movie)

"""


def BaseViewFactory(import_attr, tmdb_type, tmdb_id, season=None, episode=None, filters=None, limit=None, sort_by=None, sort_how=None, offset=None):
    mediatype = convert_type(tmdb_type, 'dbtype', season=season, episode=episode)
    clsimport = importmodule(
        module_name=f'tmdbhelper.lib.items.database.baseview_factories.concrete_classes.{import_attr}',
        import_attr=f'{mediatype.capitalize()}' if mediatype != 'set' else 'Series'
    )
    obj = clsimport()
    obj.mediatype = mediatype
    obj.tmdb_type = tmdb_type
    obj.tmdb_id = try_int(tmdb_id)
    obj.season = try_int(season, fallback=None)
    obj.episode = try_int(episode, fallback=None)
    obj.filters = filters
    obj.sort_by = sort_by
    obj.sort_how = sort_how
    obj.limit = limit
    obj.offset = offset
    return obj
