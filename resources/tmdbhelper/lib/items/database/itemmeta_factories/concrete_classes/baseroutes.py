from tmdbhelper.lib.addon.plugin import get_mpaa_prefix


class MediaItemInfoLabelItemMethod:

    @staticmethod
    def certification(i):
        certification_prefix = get_mpaa_prefix()
        if not certification_prefix:
            return i['name']
        return f"{certification_prefix}{i['name']}"


class MediaItemInfoLabelItemRoutes:
    certification = (('certification', None), MediaItemInfoLabelItemMethod.certification, 'mpaa')
    trailer = (('video', None), 'path', 'trailer')
    playcount = (('playcount', None), 'plays', 'playcount')
    imdbnumber = (('imdbnumber', None), 'value', 'imdbnumber')
    series_stats_rating = (('series_stats', None), 'rating', 'rating')
    series_stats_votes = (('series_stats', None), 'votes', 'votes')
    series_stats_year = (('series_stats', None), 'year_first', 'year')
    series_genre = (('series_genre', None), 'name', 'genre')
    network = (('network', None), 'name', 'studio')
    studio = (('studio', None), 'name', 'studio')
    genre = (('genre', None), 'name', 'genre')
    country = (('country', None), 'name', 'country')
    director = (('director', None), 'name', 'director')
    writer = (('writer', None), 'name', 'writer')
    english_plot = (('english_translation', None), 'plot', 'plot')


class MediaItemInfoPropertyItemRoutes:
    watchedcount = (('watchedcount', None), 'watched_episodes', 'watchedepisodes')
    episodecount = (('airedcount', None), 'aired_episodes', 'airedepisodes')
