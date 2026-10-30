from tmdbhelper.lib.items.directories.sync.mapper_currentlywatching import CurrentlyWatchingMovieItemMapper
from tmdbhelper.lib.items.directories.sync.mapper_nextmovies import NextMovieItemMapper


def FactoryCurrentlyWatchingMoviesItemMapper(meta, add_infoproperties=None):
    mapper_class = NextMovieItemMapper if 'collection_id' in meta else CurrentlyWatchingMovieItemMapper
    return mapper_class(meta, add_infoproperties)
