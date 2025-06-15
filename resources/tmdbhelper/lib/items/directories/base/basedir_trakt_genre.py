class TraktGenre:
    def __init__(self, clobj, genre):
        self.clobj = clobj
        self.genre = genre

    @property
    def instance(self):
        instance = self.clobj
        instance.label = f'{instance.label} ({self.genre.capitalize()})'
        instance.params['genres'] = self.genre
        return instance


def get_all_trakt_genre_class_instances(genre):
    from tmdbhelper.lib.items.directories.base.basedir_trakt import get_all_trakt_class_instances
    return [
        TraktGenre(i, genre).instance
        for i in get_all_trakt_class_instances()
        if i.filters
    ]
