from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH
from jurialmunkey.ftools import cached_property
from xbmcgui import Dialog, INPUT_NUMERIC
from tmdbhelper.lib.script.discover.base import (
    DiscoverList,
    DiscoverMulti,
    DiscoverQuery,
    DiscoverYears,
    DiscoverRatings,
    DiscoverRuntimes,
    DiscoverSave,
    DiscoverReset,
    DiscoverMain,
    DiscoverItem
)


NODE_FILENAME = 'Trakt Discover.json'


class TraktDiscoverList(DiscoverList):
    idx = 0
    default_idx = 0

    def get_routes(self):
        return (
            DiscoverItem(get_localized(32204), 'trakt_trending'),
            DiscoverItem(get_localized(32175), 'trakt_popular'),
            DiscoverItem(get_localized(32205), 'trakt_mostplayed'),
            DiscoverItem(get_localized(32414), 'trakt_mostviewers'),
            DiscoverItem(get_localized(32206), 'trakt_anticipated'),
        )


class TraktDiscoverType(DiscoverList):
    key = 'tmdb_type'
    label_prefix_localized = 467
    idx = 0
    default_idx = 0

    def get_routes(self):
        return (
            DiscoverItem(get_localized(342), 'movie'),
            DiscoverItem(get_localized(20343), 'tv'),
        )


class TraktDiscoverGenres(DiscoverMulti):
    idx = None
    key = 'genres'
    label_prefix_localized = 135

    @property
    def routes_items(self):
        if self.main.routes_dict['tmdb_type'].value == 'movie':
            return self.routes_items_movies
        return self.routes_items_shows

    @cached_property
    def routes_items_movies(self):
        return self.main.trakt_api.get_response_json('genres/movies')

    @cached_property
    def routes_items_shows(self):
        return self.main.trakt_api.get_response_json('genres/shows')

    def get_routes(self):
        return tuple((DiscoverItem(i['name'], i['slug']) for i in self.routes_items if i))


class TraktDiscoverCertifications(TraktDiscoverGenres):
    idx = None
    key = 'certifications'
    label_prefix_localized = 32486

    @cached_property
    def routes_items_movies(self):
        try:
            return self.main.trakt_api.get_response_json('certifications/movies')['us']
        except (KeyError, TypeError):
            return []

    @cached_property
    def routes_items_shows(self):
        try:
            return self.main.trakt_api.get_response_json('certifications/shows')['us']
        except (KeyError, TypeError):
            return []


class TraktDiscoverQuery(DiscoverQuery):
    pass


class TraktDiscoverYears(DiscoverYears):
    pass


class TraktDiscoverRuntimes(DiscoverRuntimes):
    pass


class TraktDiscoverRatings(DiscoverRatings):
    pass


class TraktDiscoverVotes(DiscoverRuntimes):
    key = 'votes'
    label_prefix_localized = 205

    @property
    def input_label(self):
        return get_localized(205)

    def menu(self):
        self.value_a = Dialog().input(f'{self.input_label}', type=INPUT_NUMERIC, defaultt=f'{self.value_a}' if self.value_a else '')
        self.listitem.setLabel(self.listitem_label)


class TraktDiscoverTMDbRatings(TraktDiscoverRatings):
    key = 'tmdb_ratings'
    label_affix = 'TMDb'

    def menu(self):
        super().menu()
        if self.value_a:
            self.value_a = f'{int(self.value_a) / 10:.1f}'
        if self.value_z:
            self.value_z = f'{int(self.value_z) / 10:.1f}'


class TraktDiscoverTMDbVotes(TraktDiscoverVotes):
    key = 'tmdb_votes'
    label_affix = 'TMDb'


class TraktDiscoverIMDbRatings(TraktDiscoverTMDbRatings):
    key = 'imdb_ratings'
    label_affix = 'IMDb'


class TraktDiscoverIMDbVotes(TraktDiscoverVotes):
    key = 'imdb_votes'
    label_affix = 'IMDb'


class TraktDiscoverRTRatings(TraktDiscoverRatings):
    key = 'rt_meters'
    label_affix = 'Rotten Tomatoes'


class TraktDiscoverRTUserRatings(TraktDiscoverRatings):
    key = 'rt_user_meters'
    label_affix = 'Rotten Tomatoes Users'


class TraktDiscoverMetaRatings(TraktDiscoverTMDbRatings):
    key = 'metascores'
    label_affix = 'Metacritic'


class TraktDiscoverSave(DiscoverSave):
    pass


class TraktDiscoverReset(DiscoverReset):
    pass


class TraktDiscoverMain(DiscoverMain):

    file = NODE_FILENAME
    winprop = 'TraktDiscover.Path'

    def load_values(self, tmdb_type='movie', **kwargs):
        self.routes_dict['tmdb_type'].load_value(tmdb_type)  # Set TMDb Type first as other values depend on it
        super().load_values(**kwargs)

    @cached_property
    def label(self):
        return f'Trakt {get_localized(32174)}'

    @cached_property
    def icon(self):
        return f'{ADDONPATH}/resources/trakt.png'

    @cached_property
    def name(self):
        return Dialog().input(get_localized(32241), defaultt=self.defaultt)

    def get_routes_dict(self):
        return {
            'save': TraktDiscoverSave(self),
            'list': TraktDiscoverList(self),
            'tmdb_type': TraktDiscoverType(self),
            'query': TraktDiscoverQuery(self),
            'years': TraktDiscoverYears(self),
            'genres': TraktDiscoverGenres(self),
            'certifications': TraktDiscoverCertifications(self),
            'runtimes': TraktDiscoverRuntimes(self),
            'ratings': TraktDiscoverRatings(self),
            'votes': TraktDiscoverVotes(self),
            'tmdb_ratings': TraktDiscoverTMDbRatings(self),
            'tmdb_votes': TraktDiscoverTMDbVotes(self),
            'imdb_ratings': TraktDiscoverIMDbRatings(self),
            'imdb_votes': TraktDiscoverIMDbVotes(self),
            'rt_meters': TraktDiscoverRTRatings(self),
            'rt_user_meters': TraktDiscoverRTUserRatings(self),
            'metascores': TraktDiscoverMetaRatings(self),
            'reset': TraktDiscoverReset(self),
        }

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()


def TraktDiscover():
    return TraktDiscoverMain('DialogSelect.xml', ADDONPATH)
