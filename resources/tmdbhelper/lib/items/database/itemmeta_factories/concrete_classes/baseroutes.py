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
    episodecount = (('airedcount', None), 'aired_episodes', 'episode')
    playcount = (('playcount', None), 'plays', 'playcount')


class MediaItemInfoPropertyItemRoutes:
    watchedcount = (('watchedcount', None), 'watched_episodes', 'watchedepisodes')
