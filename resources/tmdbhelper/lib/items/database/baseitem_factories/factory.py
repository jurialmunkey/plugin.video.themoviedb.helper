"""
BASEITEM FACTORY

Used to sync detailed data about item mediatype with tmdb_id to cache and then return configured data about item

"""


# FIXME IMAGES
"""
def finalise_image():
    item['infolabels']['title'] = f'{item["infoproperties"].get("width")}x{item["infoproperties"].get("height")}'
    item['params'] = -1
    item['path'] = item['art'].get('thumb') or item['art'].get('poster') or item['art'].get('fanart')
    item['is_folder'] = False
    item['library'] = 'pictures'
"""


def import_movie():
    from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.movie import Movie
    return Movie


def import_tvshow():
    from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.tvshow import Tvshow
    return Tvshow


def import_season():
    from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.season import Season
    return Season


def import_episode():
    from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.episode import Episode
    return Episode


def import_person():
    from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.person import Person
    return Person


def import_set():
    from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.series import Series
    return Series


FACTORY_ROUTES = {
    'movie': import_movie,
    'tvshow': import_tvshow,
    'season': import_season,
    'episode': import_episode,
    'person': import_person,
    'set': import_set,
}


def BaseItemFactory(mediatype, *args, **kwargs):

    try:
        dbc = FACTORY_ROUTES[mediatype]()(*args, **kwargs)
    except KeyError:
        return

    dbc.mediatype = mediatype
    return dbc
