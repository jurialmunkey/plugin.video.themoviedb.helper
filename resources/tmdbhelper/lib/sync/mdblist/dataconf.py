from jurialmunkey.ftools import cached_property

"""
Convert MDBLIST sync data from episode based list into nested show list
To mimic Trakt data output for full,extended in sync/watched

EXAMPLE INPUT
{
    "last_watched_at": "2026-09-01T11:33:57.000Z",
    "episode": {
        "season": 1,
        "number": 10,
        "name": "The Verdict",
        "still": "https://image.tmdb.org/t/p/w200/5pnE91mUlCvr9PcAGo4e9IFs1cY.jpg",
        "ids": {
            "tmdb": 1178488,
            "tvdb": 5545827
        },
        "show": {
            "title": "American Crime Story",
            "year": 2016,
            "ids": {
                "tmdb": 64513,
                "trakt": 93939,
                "imdb": "tt2788432",
                "mdblist": "5cco"
            }
        }
    }
}

EXAMPLE OUTPUT
{
    "last_watched_at": "2026-09-01T11:33:57.000Z",
    "show": {
        "type": "show",
        "title": "American Crime Story",
        "year": 2016,
        "ids": {
            "tmdb": 64513,
            "trakt": 93939,
            "imdb": "tt2788432",
            "mdblist": "5cco"
        }
    }
    "seasons": [
        {
            "number": 1,
            "episodes": [
                {
                    "number": 10,
                    "last_watched_at": "2026-09-01T11:33:57.000Z",
                    "plays": 1,
                }
            ]
        }
    ]
}
"""


class ConfigureEpisodeDataItem:
    def __init__(self, item, meta):
        self.item = item
        self.meta = meta
        self.metaepisode  # Initialise the meta

    """
    Item Values
    """

    @cached_property
    def base(self):
        return self.item['episode']

    @cached_property
    def show(self):
        show = self.base['show']
        show['type'] = 'show'
        return show

    @cached_property
    def tmdb(self):
        return self.show['ids'].get('tmdb')

    @cached_property
    def snum(self):
        return self.base['season']

    @cached_property
    def enum(self):
        return self.base['number']

    """
    Meta Values

    """

    @cached_property
    def metashow(self):
        return self.meta.setdefault(self.tmdb, {})

    @cached_property
    def metaseason(self):
        metaseason = self.metashow.setdefault('seasons', {})
        return metaseason.setdefault(self.snum, self.get_season_object(self.snum))

    @cached_property
    def metaepisode(self):
        metaepisode = self.metaseason.setdefault('episodes', {})
        return metaepisode.setdefault(self.enum, self.get_episode_object(self.enum, self.item['last_watched_at']))

    """
    Finalisation
    """

    def get_finalised_season(self, season):
        finalised_season = self.get_season_object(season['number'])
        finalised_season['episodes'] = list(season['episodes'].values())
        return finalised_season

    @cached_property
    def finalised_seasons(self):
        return [self.get_finalised_season(season) for season in self.metashow['seasons'].values()]

    @cached_property
    def finalised_object(self):
        return {
            'last_watched_at': self.item['last_watched_at'],
            'seasons': self.finalised_seasons,
            'show': self.show,
        }

    """
    Objects
    """

    def get_season_object(self, number):
        return {'number': number}

    def get_episode_object(self, number, last_watched_at, plays=1):
        return {'number': number, 'plays': plays, 'last_watched_at': last_watched_at}


def configure_episode_list(episode_list):
    meta = {}
    data = [ConfigureEpisodeDataItem(item, meta) for item in episode_list]
    return tuple((v.finalised_object for v in {i.tmdb: i for i in data}.values()))
