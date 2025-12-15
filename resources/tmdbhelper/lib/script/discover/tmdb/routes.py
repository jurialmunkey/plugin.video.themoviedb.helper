from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.addon.dialog import BusyDialog
from jurialmunkey.ftools import cached_property
from xbmcgui import Dialog
from tmdbhelper.lib.script.discover.tmdb.methods import TMDbDiscoverMethods
from tmdbhelper.lib.script.discover.tmdb.items import DiscoverProviderItem
from tmdbhelper.lib.script.discover.base import (
    DiscoverList,
    DiscoverMulti,
    DiscoverYear,
    DiscoverQuery,
    DiscoverNumeric,
    DiscoverRatings,
    DiscoverSave,
    DiscoverReset,
    DiscoverItem
)


class TMDbDiscoverTmdbType(DiscoverList):
    priority = 20
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
    priority = 30
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


class TMDbDiscoverWithCompanies(DiscoverMulti):
    priority = 40
    key = 'with_companies'
    label_prefix_localized = 32265
    query_tmdb_type = 'company'
    query_use_details = True
    separator = '%7C'
    preselect = None
    rebuild = True

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
        if not value or not self.get_query_result_value(value):
            Dialog().ok(query, get_localized(32310).format(query))
            return self.query_result

        self.route.append(DiscoverItem(self.get_query_result_label(value), self.get_query_result_value(value)))
        return self.route[-1]

    def get_query_result_label(self, query_item):
        return query_item.getLabel()

    def get_query_result_value(self, query_item):
        return query_item.getUniqueID('tmdb')

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
            self.listitem.setLabel(self.listitem_label)
            return
        while self.query_result and Dialog().yesno(self.listitem_label, get_localized(32165)):
            pass
        self.set_separator(self.get_separator())
        self.listitem.setLabel(self.listitem_label)


class TMDbDiscoverWithNetworks(TMDbDiscoverWithCompanies):
    priority = 35
    key = 'with_networks'
    label_prefix_localized = 32257
    query_tmdb_type = 'network'
    query_use_details = False
    rebuild = True

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'tv')

    def get_query_result_label(self, query_item):
        return query_item['name']

    def get_query_result_value(self, query_item):
        return query_item['id']

    def get_query(self, query):
        with BusyDialog():
            from tmdbhelper.lib.query.database.database import FindQueriesDatabase
            networks = FindQueriesDatabase().get_network(query)
            if not networks:
                return
            x = Dialog().select(self.listitem_label, [f"{i['name']} - ID #{i['id']}" for i in networks]) if len(networks) > 1 else 0
            if x == -1:
                return
            return {'id': networks[x]['id'], 'name': networks[x]['name']}


class TMDbDiscoverWithKeywords(TMDbDiscoverWithCompanies):
    priority = 50
    key = 'with_keywords'
    label_prefix_localized = 32268
    query_tmdb_type = 'keyword'
    query_use_details = False


class TMDbDiscoverWithoutKeywords(TMDbDiscoverWithKeywords):
    priority = 60
    key = 'without_keywords'
    label_prefix_localized = 32267


class TMDbDiscoverWithCast(TMDbDiscoverWithCompanies):
    priority = 70
    key = 'with_cast'
    label_prefix_localized = 32247
    query_tmdb_type = 'person'
    query_use_details = True

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie')


class TMDbDiscoverWithCrew(TMDbDiscoverWithCast):
    priority = 80
    key = 'with_crew'
    label_prefix_localized = 32248


class TMDbDiscoverWithPeople(TMDbDiscoverWithCast):
    priority = 90
    key = 'with_people'
    label_prefix_localized = 32249


class TMDbDiscoverWithGenres(DiscoverMulti):
    priority = 100
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
    priority = 110
    key = 'without_genres'
    label_prefix_localized = 32264


class TMDbDiscoverWatchRegion(DiscoverList):
    priority = 120
    key = 'watch_region'
    label_prefix_localized = 32217
    rebuild = True

    @property
    def preselect(self):
        return self.idx if self.idx is not None else next((x for x, i in enumerate(self.routes) if i.value == self.main.iso_country), -1)

    @property
    def datalist(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        datalist = FindQueriesDatabase().provider_regions
        datalist = [{'name': f'{v} ({k})', 'id': k} for k, v in datalist.items()]
        return datalist

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverWithWatchProviders(TMDbDiscoverWithGenres):
    priority = 130
    key = 'with_watch_providers'
    label_prefix_localized = 32412
    use_details = True
    routes_to_subselect = ('watch_region', )
    routes_to_reset = ()

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist, item_class=DiscoverProviderItem)

    @property
    def datalist(self):
        with BusyDialog():
            from tmdbhelper.lib.query.database.database import FindQueriesDatabase
            data_list = FindQueriesDatabase().get_watch_providers(self.main.tmdb_type, self.main.routes_dict['watch_region'].value)
            data_list = [{'name': i['provider_name'], 'id': i['provider_id'], 'icon': i.get('logo_path')} for i in data_list or ()]
            return data_list

    def menu(self):
        if not TMDbDiscoverMethods.menu_with_subselection(self):
            return
        super().menu()


class TMDbDiscoverWithWatchMonetizationTypes(DiscoverMulti):
    priority = 140
    key = 'with_watch_monetization_types'
    label_prefix_localized = 32218
    separator = '%7C'
    routes_to_subselect = ('watch_region', )
    routes_to_reset = ()

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_WATCH_MONETIZATION_TYPES
        return DISCOVER_WATCH_MONETIZATION_TYPES

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)

    def menu(self):
        if not TMDbDiscoverMethods.menu_with_subselection(self):
            return
        super().menu()


class TMDbDiscoverRegion(DiscoverList):
    priority = 150
    key = 'region'
    label_prefix_localized = 32256
    rebuild = True

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie')

    @property
    def preselect(self):
        return self.idx if self.idx is not None else next((x for x, i in enumerate(self.routes) if i.value == self.main.iso_country), -1)

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_REGIONS
        return DISCOVER_REGIONS

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverWithType(DiscoverMulti):
    priority = 160
    key = 'with_type'
    label_prefix_localized = 32255
    separator = '%7C'

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'tv')

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_TV_TYPES
        return DISCOVER_TV_TYPES

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_localized_routes(self.datalist, sorting=False)


class TMDbDiscoverWithReleaseType(DiscoverMulti):
    priority = 160
    key = 'with_release_type'
    label_prefix_localized = 32255
    routes_to_subselect = ('region', )
    routes_to_reset = ()
    separator = '%7C'

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie')

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_RELEASE_TYPES
        return DISCOVER_RELEASE_TYPES

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_localized_routes(self.datalist)

    def menu(self):
        if not TMDbDiscoverMethods.menu_with_subselection(self):
            return
        super().menu()


class TMDbDiscoverWithStatus(DiscoverMulti):
    priority = 165
    key = 'with_status'
    label_prefix_localized = 126
    separator = '%7C'

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'tv')

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_TV_STATUS
        return DISCOVER_TV_STATUS

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_localized_routes(self.datalist, sorting=False)


class TMDbDiscoverPrimaryReleaseYear(DiscoverYear):
    priority = 170
    key = 'primary_release_year'
    label_prefix_localized = 32250

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie')


class TMDbDiscoverFirstAirDateYear(TMDbDiscoverPrimaryReleaseYear):
    priority = 170
    key = 'first_air_date_year'
    label_prefix_localized = 32262

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'tv')


class TMDbDiscoverPrimaryReleaseDateGte(DiscoverQuery):
    priority = 180
    key = 'primary_release_date.gte'
    label_prefix_localized = 32251

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie')

    @property
    def query_header(self):
        return f'{get_localized(32114)} YYYY-MM-DD\n{get_localized(32113)}'


class TMDbDiscoverFirstAirDateGte(TMDbDiscoverPrimaryReleaseDateGte):
    priority = 180
    key = 'first_air_date.gte'
    label_prefix_localized = 32260

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'tv')


class TMDbDiscoverPrimaryReleaseDateLte(TMDbDiscoverPrimaryReleaseDateGte):
    priority = 190
    key = 'primary_release_date.lte'
    label_prefix_localized = 32252


class TMDbDiscoverFirstAirDateLte(TMDbDiscoverFirstAirDateGte):
    priority = 190
    key = 'first_air_date.lte'
    label_prefix_localized = 32261


class TMDbDiscoverReleaseDateGte(TMDbDiscoverPrimaryReleaseDateGte):
    priority = 200
    key = 'release_date.gte'
    label_prefix_localized = 32253


class TMDbDiscoverAirDateGte(TMDbDiscoverFirstAirDateGte):
    priority = 200
    key = 'air_date.gte'
    label_prefix_localized = 32258


class TMDbDiscoverReleaseDateLte(TMDbDiscoverPrimaryReleaseDateGte):
    priority = 210
    key = 'release_date.lte'
    label_prefix_localized = 32254


class TMDbDiscoverAirDateLte(TMDbDiscoverFirstAirDateGte):
    priority = 210
    key = 'air_date.lte'
    label_prefix_localized = 32259


class TMDbDiscoverTimezone(TMDbDiscoverRegion):
    priority = 214
    key = 'timezone'
    label_prefix_localized = 32346
    timezone_region = None

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'tv')

    @property
    def region_preselect(self):
        return next((x for x, i in enumerate(self.timezone_regions) if f'({self.main.iso_country})' == i['name'][-4:]), -1)

    @cached_property
    def region_names(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_REGIONS
        return {i['id']: i['name'] for i in DISCOVER_REGIONS}

    @cached_property
    def timezone_regions(self):
        with BusyDialog():
            from tmdbhelper.lib.query.database.database import FindQueriesDatabase
            datalist = FindQueriesDatabase().get_timezones()
            datalist = [
                {'id': j, 'name': self.region_names.get(j, j)}
                for j in {i['iso_country'] for i in datalist}
            ]
            datalist = sorted(datalist, key=lambda x: x['name'])
        return datalist

    @property
    def datalist(self):
        with BusyDialog():
            from tmdbhelper.lib.query.database.database import FindQueriesDatabase
            datalist = FindQueriesDatabase().get_timezones(self.timezone_region)
            datalist = [
                {'id': i['timezone'], 'name': f"{i['timezone']} ({i['iso_country']})"}
                for i in datalist
            ]
            return datalist

    def menu(self):
        x = self.dialog_select(get_localized(20026), [i['name'] for i in self.timezone_regions], preselect=self.region_preselect)
        if x == -1:
            return
        self.timezone_region = self.timezone_regions[x]['id']
        self.reset_routes()
        super().menu()


class TMDbDiscoverWithOriginCountry(TMDbDiscoverRegion):
    priority = 218
    key = 'with_origin_country'
    label_prefix_localized = 32220
    rebuild = False

    @property
    def preselect(self):
        return self.idx if self.idx is not None else -1


class TMDbDiscoverWithOriginalLanguage(DiscoverMulti):
    priority = 220
    key = 'with_original_language'
    label_prefix_localized = 32269
    separator = '%7C'

    @property
    def datalist(self):
        from tmdbhelper.lib.addon.consts import DISCOVER_LANGUAGES
        return DISCOVER_LANGUAGES

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist)


class TMDbDiscoverCertificationCountry(TMDbDiscoverRegion):
    priority = 230
    key = 'certification_country'
    label_prefix_localized = 32219
    routes_to_reset = ('certification', 'certification_lte', 'certification_gte')
    routes_to_subselect = ()
    rebuild = True

    @property
    def preselect(self):
        return self.idx if self.idx is not None else next((x for x, i in enumerate(self.routes) if i.value == self.main.iso_country), -1)

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

    def menu(self):
        if not TMDbDiscoverMethods.menu_with_subselection(self):
            return
        super().menu()


class TMDbDiscoverCertification(TMDbDiscoverRegion):
    priority = 240
    key = 'certification'
    label_prefix_localized = 32486
    routes_to_reset = ('certification_lte', 'certification_gte')
    routes_to_subselect = ('certification_country', )

    @property
    def enabled(self):
        return bool(self.main.tmdb_type == 'movie')

    @property
    def datalist(self):
        with BusyDialog():
            from tmdbhelper.lib.query.database.database import FindQueriesDatabase
            datalist = FindQueriesDatabase().get_certification('movie')
            datalist = [
                {'id': i['certification'], 'name': i['certification']}
                for i in sorted(datalist, key=lambda x: x.get('ordering'))
                if i['iso_country'] == self.main.routes_dict['certification_country'].value
            ]
            return datalist

    def get_routes(self):
        return TMDbDiscoverMethods.get_configured_routes(self.datalist, sorting=False)

    def menu(self):
        if not TMDbDiscoverMethods.menu_with_subselection(self):
            return
        super().menu()


class TMDbDiscoverCertificationGte(TMDbDiscoverCertification):
    priority = 250
    key = 'certification.gte'
    label_prefix_localized = 32488
    routes_to_reset = ('certification', )


class TMDbDiscoverCertificationLte(TMDbDiscoverCertification):
    priority = 260
    key = 'certification.lte'
    label_prefix_localized = 32487
    routes_to_reset = ('certification', )


class TMDbDiscoverVoteAverage(DiscoverRatings):
    priority = 270
    key = 'vote_average'
    label_prefix_localized = 32028
    value_divisor = 10

    @property
    def paramstring(self):
        if not self.value:
            return
        paramstring = f'{self.key}.gte={self.value_a / self.value_divisor}'
        paramstring = f'{paramstring}&{self.key}.lte={self.value_z / self.value_divisor}' if self.value_z else paramstring
        return paramstring


class TMDbDiscoverVoteCountGte(DiscoverNumeric):
    priority = 280
    key = 'vote_count.gte'
    label_prefix_localized = 32270

    @property
    def query_header(self):
        return get_localized(self.label_prefix_localized)


class TMDbDiscoverVoteCountLte(TMDbDiscoverVoteCountGte):
    priority = 290
    key = 'vote_count.lte'
    label_prefix_localized = 32271


class TMDbDiscoverWithRuntime(TMDbDiscoverVoteAverage):
    priority = 300
    key = 'with_runtime'
    label_prefix_localized = 2050
    value_divisor = 1
    base_range_start = 0
    base_range_end = 361  # six hours is surely long enough
    base_range_reverse = False

    @property
    def input_label(self):
        return f'{get_localized(2050)} ({get_localized(12391)})'

    @staticmethod
    def select_options(vals):
        return ['{0:01d}hr {1:02d}min'.format(*divmod(i, 60)) for i in vals]


class TMDbDiscoverReset(DiscoverReset):
    priority = 990


class TMDbDiscoverSave(DiscoverSave):
    priority = 999


def get_all_route_class_instances(*args, **kwargs):
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [obj(*args, **kwargs) for obj in get_all_module_class_objects_by_priority(__name__)]
