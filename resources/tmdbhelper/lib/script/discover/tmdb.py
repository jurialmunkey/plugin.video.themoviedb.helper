from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH
from tmdbhelper.lib.addon.dialog import BusyDialog
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

    @staticmethod
    def get_load_value_split(value, separator):
        import re
        return re.split(separator, value, flags=re.IGNORECASE)

    @staticmethod
    def get_load_value_generator(value, separator, id_func):
        return (
            ItemTuple(id_func(tmdb_id), tmdb_id)
            for tmdb_id in TMDbDiscoverMethods.get_load_value_split(value, separator)
        )

    @staticmethod
    def get_load_value_separator(value):
        return '%2C' if '%2C' in value or '%2c' in value else '%7C'


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


class TMDbDiscoverWithCompanies(DiscoverMulti):
    key = 'with_companies'
    label_prefix_localized = 32265
    query_tmdb_type = 'company'
    query_use_details = True
    separator = '%7C'
    preselect = None
    idx = None

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    def get_name_from_id(self, tmdb_id):
        try:
            return self.tmdb_api.get_response_json(self.query_tmdb_type, tmdb_id)['name']
        except (KeyError, TypeError):
            return

    def get_load_value_generator(self, value):
        return TMDbDiscoverMethods.get_load_value_generator(value, self.separator, self.get_name_from_id)

    def load_value(self, value):
        self.separator = TMDbDiscoverMethods.get_load_value_separator(value)
        self.route = [i for i in self.get_load_value_generator(value) if i[0] and i[1]]

    @property
    def query_header(self):
        return f'{get_localized(32276)} {self.query_tmdb_type}'

    @property
    def query_result(self):
        query = Dialog().input(self.query_header)
        if not query:
            return

        value = self.get_query(query)
        if not value or not value.getUniqueID('tmdb'):
            Dialog().ok(query, get_localized(32310).format(query))
            return self.query_result

        self.route.append(ItemTuple(value.getLabel(), value.getUniqueID('tmdb')))
        return self.route[-1]

    def get_query(self, query):
        with BusyDialog():
            from tmdbhelper.lib.query.database.database import FindQueriesDatabase
            return FindQueriesDatabase().get_tmdb_id_from_query(
                tmdb_type=self.query_tmdb_type,
                query=query,
                header=self.listitem_label,
                use_details=self.query_use_details,
                get_listitem=True
            )

    @cached_property
    def route(self):
        return []

    def select_separator(self):
        if len(self.route) < 2:
            return
        super().select_separator()

    def clear_route(self):
        if len(self.route) < 1:
            return False
        if Dialog().yesno(
            get_localized(32101),
            get_localized(32100),
            nolabel=get_localized(32101),
            yeslabel=get_localized(32102)
        ):
            return False
        self.route = []
        return True

    def menu(self):
        if self.clear_route():
            return
        while self.query_result and Dialog().yesno(self.listitem_label, get_localized(32165)):
            pass
        self.select_separator()
        self.listitem.setLabel(self.listitem_label)


class TMDbDiscoverWithKeywords(TMDbDiscoverWithCompanies):
    key = 'with_keywords'
    label_prefix_localized = 32268
    query_tmdb_type = 'keyword'
    query_use_details = False


class TMDbDiscoverWithoutKeywords(TMDbDiscoverWithKeywords):
    key = 'without_keywords'
    label_prefix_localized = 32267


class TMDbDiscoverWithCast(TMDbDiscoverWithCompanies):
    key = 'with_cast'
    label_prefix_localized = 32247
    query_tmdb_type = 'person'
    query_use_details = True

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie')


class TMDbDiscoverWithCrew(TMDbDiscoverWithCast):
    key = 'with_crew'
    label_prefix_localized = 32248


class TMDbDiscoverWithPeople(TMDbDiscoverWithCast):
    key = 'with_people'
    label_prefix_localized = 32249


class TMDbDiscoverWithGenres(DiscoverMulti):
    key = 'with_genres'
    label_prefix_localized = 32263
    idx = None
    separator = '%7C'

    def get_load_value_index(self, tmdb_id):
        return next((x for x, i in enumerate(self.routes) if str(i.value) == str(tmdb_id)), None)

    def get_load_value_split(self, value):
        return TMDbDiscoverMethods.get_load_value_split(value, self.separator)

    def load_value(self, value):
        self.separator = TMDbDiscoverMethods.get_load_value_separator(value)
        self.idx = [self.get_load_value_index(i) for i in self.get_load_value_split(value) if i]

    @property
    def datalist(self):
        with BusyDialog():
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

    def load_values(self, tmdb_type='movie', **kwargs):
        from tmdbhelper.lib.addon.logger import kodi_log
        kodi_log(f'{kwargs}', 1)
        self.routes_dict['tmdb_type'].load_value(tmdb_type)  # Set TMDb Type first as other values depend on it
        for k, v in kwargs.items():
            try:
                value = v.replace(',', '%2C').replace('|', '%7C')  # Convert back to percent encoding for consistency
            except AttributeError:
                continue
            try:
                self.routes_dict[k].load_value(value)
            except KeyError:
                continue

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
            'with_cast': TMDbDiscoverWithCast(self),
            'with_crew': TMDbDiscoverWithCrew(self),
            'with_people': TMDbDiscoverWithPeople(self),
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
