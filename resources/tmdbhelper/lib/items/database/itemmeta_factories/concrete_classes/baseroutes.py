from tmdbhelper.lib.addon.plugin import get_mpaa_prefix


class MediaItemInfoLabelItemMethod:

    @staticmethod
    def certification(i):
        certification_prefix = get_mpaa_prefix()
        if not certification_prefix:
            return i['name']
        return f"{certification_prefix}{i['name']}"


class MediaItemInfoLabelItemRoutes:
    # dbmeta_instance, column, infolabel, overwrite existing values
    certification = (('certification', None), MediaItemInfoLabelItemMethod.certification, 'mpaa', True)
    trailer = (('video', None), 'path', 'trailer', True)
    episodecount = (('airedcount', None), 'aired_episodes', 'episode', True)
    playcount = (('playcount', None), 'plays', 'playcount', True)
    imdbnumber = (('imdbnumber', None), 'value', 'imdbnumber', True)
    network = (('network', None), 'name', 'studio', True)
    studio = (('studio', None), 'name', 'studio', True)
    genre = (('genre', None), 'name', 'genre', True)
    country = (('country', None), 'name', 'country', True)
    director = (('director', None), 'name', 'director', True)
    writer = (('writer', None), 'name', 'writer', True)
    series_genre = (('series_genre', None), 'name', 'genre', True)
    series_stats_rating = (('series_stats', None), 'rating', 'rating', True)
    series_stats_votes = (('series_stats', None), 'votes', 'votes', True)
    series_stats_year = (('series_stats', None), 'year_first', 'year', True)
    english_plot = (('english_translation', None), 'plot', 'plot', False)  # Use as fallback so don't overwrite existing plot value


class MediaItemInfoPropertyItemRoutes:
    watchedcount = (('watchedcount', None), 'watched_episodes', 'watchedepisodes')
