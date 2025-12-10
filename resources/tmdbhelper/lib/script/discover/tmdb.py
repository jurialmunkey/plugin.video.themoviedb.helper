from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH
from jurialmunkey.ftools import cached_property
from xbmcgui import Dialog, INPUT_NUMERIC
from tmdbhelper.lib.script.discover.base import (
    DiscoverMenu,
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


class TMDbDiscoverMethods:
    @staticmethod
    def get_configured_routes(routes):
        return tuple((
            ItemTuple(i['name'], i['id'])
            for i in sorted(routes, key=lambda x: x['name'])
        ))

    @staticmethod
    def get_configured_localized_routes(routes):
        return tuple((
            ItemTuple(get_localized(i['name']), i['id'])
            for i in sorted(routes, key=lambda x: x['name'])
        ))


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
        return bool(self.main.tmdb_type == 'movie')

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_REGIONS
        return DISCOVER_REGIONS

    @cached_property
    def routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverWithCompanies(DiscoverMenu):
    key = 'with_companies'
    label_prefix_localized = 32265
    query_tmdb_type = 'company'
    query_use_details = True

    @property
    def query_header(self):
        return f'{get_localized(32276)} {self.query_tmdb_type}'

    @property
    def query_result(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        item = FindQueriesDatabase().get_tmdb_id_from_query(
            tmdb_type=self.query_tmdb_type,
            query=Dialog().input(self.query_header),
            header=self.listitem_label,
            use_details=self.query_use_details,
            get_listitem=True
        )
        if not item or not item.getUniqueID('tmdb'):
            return ItemTuple('', '')
        return ItemTuple(item.getLabel(), item.getUniqueID('tmdb'))

    def menu(self):
        self.label, self.value = self.query_result
        self.listitem.setLabel(self.listitem_label)


class TMDbDiscoverWithKeywords(TMDbDiscoverWithCompanies):
    key = 'with_keywords'
    label_prefix_localized = 32268
    query_tmdb_type = 'keyword'
    query_use_details = False


class TMDbDiscoverWithoutKeywords(TMDbDiscoverWithKeywords):
    key = 'without_keywords'
    label_prefix_localized = 32267


class TMDbDiscoverWithGenres(DiscoverMulti):
    key = 'with_genres'
    label_prefix_localized = 32263
    idx = None
    separator = '%7C'

    @property
    def datalist(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        data_list = FindQueriesDatabase().get_genres(self.main.tmdb_type) or {}
        data_list = [{'name': k, 'id': v} for k, v in data_list.items()]
        return data_list

    @cached_property
    def routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)

    def menu(self):
        super().menu()
        self.select_separator()
        self.listitem.setLabel(self.listitem_label)


class TMDbDiscoverWithoutGenres(TMDbDiscoverWithGenres):
    key = 'without_genres'
    label_prefix_localized = 32264


class TMDbDiscoverWithOriginalLanguage(DiscoverMulti):
    key = 'with_original_language'
    label_prefix_localized = 32269
    idx = None
    separator = '%7C'

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_LANGUAGES
        return DISCOVER_LANGUAGES

    @cached_property
    def routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverWithReleaseType(DiscoverMulti):
    key = 'with_release_type'
    label_prefix_localized = 32255
    idx = None
    separator = '%7C'

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie')

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_RELEASE_TYPES
        return DISCOVER_RELEASE_TYPES

    @cached_property
    def routes(self):
        return TMDbDiscoverMethods.get_configured_localized_routes(self.datalist)


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

    @property
    def tmdb_type(self):
        return self.routes_dict['tmdb_type'].value

    def get_routes_dict(self):
        return {
            'save': TMDbDiscoverSave(self),
            'tmdb_type': TMDbDiscoverType(self),
            'with_genres': TMDbDiscoverWithGenres(self),
            'without_genres': TMDbDiscoverWithoutGenres(self),
            'with_companies': TMDbDiscoverWithCompanies(self),
            'with_keywords': TMDbDiscoverWithKeywords(self),
            'without_keywords': TMDbDiscoverWithoutKeywords(self),
            'with_original_language': TMDbDiscoverWithOriginalLanguage(self),
            'region': TMDbDiscoverRegion(self),
            'with_release_type': TMDbDiscoverWithReleaseType(self),
            'reset': TMDbDiscoverReset(self),
        }


def TMDbDiscover():
    return TMDbDiscoverMain('DialogSelect.xml', ADDONPATH)
