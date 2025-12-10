from tmdbhelper.lib.script.discover.base import DiscoverList, DiscoverQuery, DiscoverYears, DiscoverRatings, DiscoverRuntimes, DiscoverSave, DiscoverReset, DiscoverMain, ItemTuple
from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH
from jurialmunkey.ftools import cached_property
from xbmcgui import Dialog, INPUT_NUMERIC


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

    @cached_property
    def routes(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_REGIONS
        return tuple((
            ItemTuple(i['name'], i['id'])
            for i in sorted(DISCOVER_REGIONS, key=lambda x: x['name'])
        ))


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
            'region': TMDbDiscoverRegion(self),
            'reset': TMDbDiscoverReset(self),
        }


def TMDbDiscover():
    return TMDbDiscoverMain('DialogSelect.xml', ADDONPATH)
