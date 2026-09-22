from jurialmunkey.ftools import cached_property


class RatingsTraktMapperTrakt:
    name = 'trakt'

    def __init__(self, data):
        self.data = data

    def configure_rating(self, data):
        return int(float(data) * 10)

    @cached_property
    def rating(self):
        try:
            data = self.data['rating']
            return self.configure_rating(data)
        except (KeyError, TypeError, ValueError):
            return

    def configure_votes(self, data):
        return int(data)

    @cached_property
    def votes(self):
        try:
            data = self.data['votes']
            return self.configure_votes(data)
        except (KeyError, TypeError, ValueError):
            return

    @cached_property
    def outputs(self):
        return {
            f'{self.name}_{k}': v
            for k, v in (
                ('rating', self.rating),
                ('votes', self.votes),
            ) if v
        }


class RatingsTraktMapperTMDb(RatingsTraktMapperTrakt):
    name = 'tmdb'


class RatingsTraktMapperIMDb(RatingsTraktMapperTrakt):
    name = 'imdb'


class RatingsTraktMapperMetacritic(RatingsTraktMapperTrakt):
    name = 'metacritic'

    def configure_rating(self, data):
        return int(data)  # Already a score out of 100


def RatingsTraktMapper(name, data):
    routes = {
        'trakt': RatingsTraktMapperTrakt,
        'tmdb': RatingsTraktMapperTMDb,
        'imdb': RatingsTraktMapperIMDb,
        'metascore': RatingsTraktMapperMetacritic,
    }
    try:
        return routes[name](data)
    except KeyError:
        return


def map_trakt_ratings(meta):
    mappers = (i for i in (RatingsTraktMapper(name, data) for name, data in meta.items()) if i)
    return {k: v for i in mappers for k, v in i.outputs.items()}
