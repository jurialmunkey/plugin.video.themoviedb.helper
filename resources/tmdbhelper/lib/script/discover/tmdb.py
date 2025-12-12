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
    ItemTuple
)


NODE_FILENAME = 'TMDb Discover.json'


class TMDbDiscoverSave(DiscoverSave):
    pass


class TMDbDiscoverReset(DiscoverReset):
    pass


class TMDbDiscoverType(DiscoverList):
    key = 'tmdb_type'
    label_prefix_localized = 467

    @cached_property
    def routes(self):
        return (
            ItemTuple(get_localized(342), 'movie'),
            ItemTuple(get_localized(20343), 'tv'),
        )

    def menu(self):
        super().menu()
        self.main.build_menu('TMDbDiscoverType')


class TMDbDiscoverRegion(DiscoverList):
    key = 'region'
    label_prefix_localized = 32256
    idx = None

    @property
    def enabled(self):
        return bool(self.main.routes_dict['tmdb_type'].value == 'movie')

    @staticmethod
    def get_configured_routes(routes):
        return tuple((
            ItemTuple(i['name'], i['id'])
            for i in sorted(routes, key=lambda x: x['name'])
        ))

    @cached_property
    def routes(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_REGIONS
        return TMDbDiscoverRegion.get_configured_routes(DISCOVER_REGIONS)


class TMDbDiscoverWithOriginalLanguage(DiscoverMulti):
    key = 'with_original_language'
    label_prefix_localized = 32269
    idx = None
    separator = '|'

    @cached_property
    def routes(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_LANGUAGES
        return TMDbDiscoverRegion.get_configured_routes(DISCOVER_LANGUAGES)


class TMDbDiscoverWithReleaseType(DiscoverMulti):
    key = 'with_release_type'
    label_prefix_localized = 32255
    idx = None
    separator = '|'

    @property
    def enabled(self):
        return bool(self.main.routes_dict['tmdb_type'].value == 'movie')

    @staticmethod
    def get_configured_localized_routes(routes):
        return tuple((
            ItemTuple(get_localized(i['name']), str(i['id']))
            for i in sorted(routes, key=lambda x: x['name'])
        ))

    @cached_property
    def routes(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_RELEASE_TYPES
        return TMDbDiscoverWithReleaseType.get_configured_localized_routes(DISCOVER_RELEASE_TYPES)


class TMDbDiscoverMain(DiscoverMain):

    file = NODE_FILENAME
    winprop = 'TMDbDiscover.Path'
    base_params = ('info=discover', 'with_id=True')

    @cached_property
    def label(self):
        return f'TMDb {get_localized(32174)}'

    @cached_property
    def icon(self):
        return f'{ADDONPATH}/resources/icons/themoviedb/discover.png'

    @cached_property
    def name(self):
        return Dialog().input(get_localized(32241), defaultt=self.defaultt)

    def get_routes_dict(self):
        return {
            'save': TMDbDiscoverSave(self),
            'tmdb_type': TMDbDiscoverType(self),
            'with_original_language': TMDbDiscoverWithOriginalLanguage(self),
            'region': TMDbDiscoverRegion(self),
            'with_release_type': TMDbDiscoverWithReleaseType(self),
            'reset': TMDbDiscoverReset(self),
        }


def TMDbDiscover():
    return TMDbDiscoverMain('DialogSelect.xml', ADDONPATH)
