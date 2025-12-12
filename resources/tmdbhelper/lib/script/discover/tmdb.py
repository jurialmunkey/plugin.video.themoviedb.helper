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
    DiscoverItem
)


NODE_FILENAME = 'TMDb Discover.json'


class DiscoverProviderItem(DiscoverItem):
    @cached_property
    def icon(self):
        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
        return TMDbImagePath().get_imagepath_origin(self.image)

    @cached_property
    def label2(self):
        return f"ID #{self.value}"


class TMDbDiscoverMethods:
    @staticmethod
    def get_configured_routes(routes, item_class=DiscoverItem):
        return tuple((
            item_class(label=i['name'], value=i['id'], image=i.get('icon'))
            for i in sorted(routes, key=lambda x: x['name'])
        ))

    @staticmethod
    def get_configured_localized_routes(routes, item_class=DiscoverItem):
        return tuple((
            item_class(label=get_localized(i['name']), value=i['id'], image=i.get('icon'))
            for i in sorted(routes, key=lambda x: x['name'])
        ))

    @staticmethod
    def get_load_value_split(value, separator):
        import re
        return re.split(separator, value, flags=re.IGNORECASE)

    @staticmethod
    def get_load_value_generator(value, separator, id_func, item_class=DiscoverItem):
        return (
            item_class(id_func(tmdb_id), tmdb_id)
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
    rebuild = True
    idx = 0
    default_idx = 0

    def get_routes(self):
        return (
            DiscoverItem(get_localized(342), 'movie'),
            DiscoverItem(get_localized(20343), 'tv'),
        )


class TMDbDiscoverSortBy(DiscoverList):
    key = 'sort_by'
    label_prefix_localized = 32240

    @property
    def datalist(self):
        if self.main.tmdb_type == 'movie':
            from tmdbhelper.lib.addon.consts import DISCOVER_SORTBY_MOVIES
            return DISCOVER_SORTBY_MOVIES

        if self.main.tmdb_type == 'tv':
            from tmdbhelper.lib.addon.consts import DISCOVER_SORTBY_TV
            return DISCOVER_SORTBY_TV

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverRegion(DiscoverList):
    key = 'region'
    label_prefix_localized = 32256
    rebuild = True

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie')

    @property
    def preselect(self):
        return self.idx or next((x for x, i in enumerate(self.routes) if i.value == self.main.iso_country), -1)

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_REGIONS
        return DISCOVER_REGIONS

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverCertificationCountry(TMDbDiscoverRegion):
    key = 'certification_country'
    label_prefix_localized = 32219
    rebuild = True

    @property
    def preselect(self):
        return self.idx or next((x for x, i in enumerate(self.routes) if i.value == self.main.iso_country), -1)

    @cached_property
    def region_names(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_REGIONS
        return {i['id']: i['name'] for i in DISCOVER_REGIONS}

    @property
    def datalist(self):
        with BusyDialog():
            from tmdbhelper.lib.query.database.database import FindQueriesDatabase
            datalist = FindQueriesDatabase().get_certification('movie')
            datalist = [
                {'id': j, 'name': self.region_names.get(j, j)}
                for j in {i['iso_country'] for i in datalist}
            ]
            return datalist


class TMDbDiscoverCertification(TMDbDiscoverRegion):
    key = 'certification'
    label_prefix_localized = 32486

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie' and self.main.certification_country)

    @property
    def datalist(self):
        with BusyDialog():
            from tmdbhelper.lib.query.database.database import FindQueriesDatabase
            datalist = FindQueriesDatabase().get_certification('movie')
            datalist = [
                {'id': i['certification'], 'name': i['certification']}
                for i in datalist if i['iso_country'] == self.main.certification_country
            ]
            return datalist


class TMDbDiscoverCertificationGTE(TMDbDiscoverCertification):
    key = 'certification.gte'
    label_prefix_localized = 32488


class TMDbDiscoverCertificationLTE(TMDbDiscoverCertification):
    key = 'certification.lte'
    label_prefix_localized = 32487


class TMDbDiscoverWatchRegion(DiscoverList):
    key = 'watch_region'
    label_prefix_localized = 32217
    rebuild = True

    @property
    def preselect(self):
        return self.idx or next((x for x, i in enumerate(self.routes) if i.value == self.main.iso_country), -1)

    @property
    def datalist(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        datalist = FindQueriesDatabase().provider_regions
        datalist = [{'name': f'{v} ({k})', 'id': k} for k, v in datalist.items()]
        return datalist

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverWithCompanies(DiscoverMulti):
    key = 'with_companies'
    label_prefix_localized = 32265
    query_tmdb_type = 'company'
    query_use_details = True
    separator = '%7C'
    preselect = None

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
        self.route = [i for i in self.get_load_value_generator(value) if i.label and i.value]

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

        self.route.append(DiscoverItem(value.getLabel(), value.getUniqueID('tmdb')))
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

    @property
    def has_multiples(self):
        return bool(len(self.route) > 1)

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
        self.set_separator(self.get_separator())
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

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)

    def menu(self):
        super().menu()
        self.set_separator(self.get_separator())
        self.listitem.setLabel(self.listitem_label)


class TMDbDiscoverWithoutGenres(TMDbDiscoverWithGenres):
    key = 'without_genres'
    label_prefix_localized = 32264


class TMDbDiscoverWithWatchProviders(TMDbDiscoverWithGenres):
    key = 'with_watch_providers'
    label_prefix_localized = 32412
    use_details = True

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist, item_class=DiscoverProviderItem)

    @property
    def enabled(self):
        return bool(self.main.watch_region)

    @property
    def datalist(self):
        with BusyDialog():
            from tmdbhelper.lib.query.database.database import FindQueriesDatabase
            data_list = FindQueriesDatabase().get_watch_providers(self.main.tmdb_type, self.main.watch_region)
            data_list = [{'name': i['provider_name'], 'id': i['provider_id'], 'icon': i.get('logo_path')} for i in data_list]
            return data_list


class TMDbDiscoverWithWatchMonetizationTypes(DiscoverMulti):
    key = 'with_watch_monetization_types'
    label_prefix_localized = 32218
    separator = '%7C'

    @property
    def enabled(self):
        return bool(self.main.watch_region)

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_WATCH_MONETIZATION_TYPES
        return DISCOVER_WATCH_MONETIZATION_TYPES

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverWithOriginalLanguage(DiscoverMulti):
    key = 'with_original_language'
    label_prefix_localized = 32269
    separator = '%7C'

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_LANGUAGES
        return DISCOVER_LANGUAGES

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverWithReleaseType(DiscoverMulti):
    key = 'with_release_type'
    label_prefix_localized = 32255
    separator = '%7C'

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie' and self.main.region)

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_RELEASE_TYPES
        return DISCOVER_RELEASE_TYPES

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_localized_routes(self.datalist)


class TMDbDiscoverMain(DiscoverMain):

    file = NODE_FILENAME
    winprop = 'TMDbDiscover.Path'
    base_params = ('info=discover', 'with_id=True')

    def load_values(self, tmdb_type='movie', **kwargs):
        self.routes_dict['tmdb_type'].load_value(tmdb_type)  # Set TMDb Type first as other values depend on it
        super().load_values(**kwargs)

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

    @property
    def watch_region(self):
        return self.routes_dict['watch_region'].value

    @property
    def region(self):
        return self.routes_dict['region'].value

    @property
    def certification_country(self):
        return self.routes_dict['certification_country'].value

    @cached_property
    def iso_country(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb().iso_country

    def get_routes_dict(self):
        return {
            'save': TMDbDiscoverSave(self),
            'tmdb_type': TMDbDiscoverType(self),
            'sort_by': TMDbDiscoverSortBy(self),
            'with_genres': TMDbDiscoverWithGenres(self),
            'without_genres': TMDbDiscoverWithoutGenres(self),
            'watch_region': TMDbDiscoverWatchRegion(self),
            'with_watch_providers': TMDbDiscoverWithWatchProviders(self),
            'with_watch_monetization_types': TMDbDiscoverWithWatchMonetizationTypes(self),
            'with_cast': TMDbDiscoverWithCast(self),
            'with_crew': TMDbDiscoverWithCrew(self),
            'with_people': TMDbDiscoverWithPeople(self),
            'with_companies': TMDbDiscoverWithCompanies(self),
            'with_keywords': TMDbDiscoverWithKeywords(self),
            'without_keywords': TMDbDiscoverWithoutKeywords(self),
            'with_original_language': TMDbDiscoverWithOriginalLanguage(self),
            'region': TMDbDiscoverRegion(self),
            'certification_country': TMDbDiscoverCertificationCountry(self),
            'certification': TMDbDiscoverCertification(self),
            'certification_gte': TMDbDiscoverCertificationGTE(self),
            'certification_lte': TMDbDiscoverCertificationLTE(self),
            'with_release_type': TMDbDiscoverWithReleaseType(self),
            'reset': TMDbDiscoverReset(self),
        }


def TMDbDiscover():
    return TMDbDiscoverMain('DialogSelect.xml', ADDONPATH)
