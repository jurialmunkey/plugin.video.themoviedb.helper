from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.logger import kodi_try_except
from tmdbhelper.lib.api.contains import CommonContainerAPIs, CommonRatingsAPIs
from jurialmunkey.window import WindowPropertySetter


class CommonMonitorDetails(CommonContainerAPIs):
    @cached_property
    def lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        lidc = ListItemDetails(self)
        lidc.cache_refresh = None
        lidc.cache_translations = False
        lidc.extendedinfo = True
        lidc.parent_params = {}
        return lidc

    @kodi_try_except('lib.monitor.common get_tmdb_id')
    def get_tmdb_id(self, tmdb_type, imdb_id=None, query=None, year=None, episode_year=None):
        return self.query_database.get_tmdb_id(
            tmdb_type=tmdb_type,
            imdb_id=imdb_id if imdb_id and imdb_id.startswith('tt') else None,
            query=query,
            year=year,
            episode_year=episode_year,
        )

    @kodi_try_except('lib.monitor.common get_tmdb_id_multi')
    def get_tmdb_id_multi(self, tmdb_type=None, imdb_id=None, query=None, year=None, episode_year=None):
        return self.query_database.get_tmdb_id(
            tmdb_type=tmdb_type,
            imdb_id=imdb_id if imdb_id and imdb_id.startswith('tt') else None,
            query=query,
            year=year,
            episode_year=episode_year,
            use_multisearch=True
        )

    @kodi_try_except('lib.monitor.common get_tmdb_id_parent')
    def get_tmdb_id_parent(self, tmdb_id, item_type, season=None, episode=None):
        return self.query_database.get_trakt_id(
            id_value=tmdb_id,
            id_type='tmdb',
            item_type=item_type,
            output_type='tmdb',
            season=season,
            episode=episode
        )

    @kodi_try_except('lib.monitor.common get_identifier_details')
    def get_identifier_details(self, identifier):
        return self.query_database.get_identifier(identifier)

    @kodi_try_except('lib.monitor.common set_identifier_details')
    def set_identifier_details(self, identifier, tmdb_id, tmdb_type):
        return self.query_database.set_identifier(identifier, tmdb_id, tmdb_type)

    @kodi_try_except('lib.monitor.common del_identifier_details')
    def del_identifier_details(self, identifier):
        return self.query_database.del_identifier(identifier)

    @cached_property
    def all_awards(self):
        return CommonRatingsAPIs.get_awards_data()

    def get_all_ratings(self, tmdb_type, tmdb_id, season=None, episode=None):
        ratings_api = CommonRatingsAPIs()

        # Reuse awards to avoid rescraping
        ratings_api.all_awards = self.all_awards

        # Set defaults
        ratings_api.tmdb_type = tmdb_type
        ratings_api.tmdb_id = tmdb_id
        ratings_api.season = season
        ratings_api.episode = episode

        # Reuse some APIs to avoid reinit
        ratings_api.tmdb_api = self.tmdb_api
        ratings_api.tmdb_imagepath = self.tmdb_imagepath
        ratings_api.trakt_api = self.trakt_api
        ratings_api.ftv_api = self.ftv_api
        ratings_api.tvdb_api = self.tvdb_api
        ratings_api.mdblist_api = self.mdblist_api
        ratings_api.omdb_api = self.omdb_api
        ratings_api.query_database = self.query_database

        return ratings_api.all_ratings


class CommonMonitorItem:
    def __init__(self, common_monitor_functions_instance, item):
        self.common_monitor_functions_instance = common_monitor_functions_instance
        self.properties = set()
        self.item = item

    def set_single_property(self, key, dictionary):
        if not isinstance(dictionary, dict):
            return
        if key not in dictionary:
            return
        if dictionary[key] in (None, ''):
            return
        self.common_monitor_functions_instance.set_property(key, dictionary[key])
        self.properties.add(key)

    def update_property(self, key, value):
        self.common_monitor_functions_instance.set_property(key, value)
        self.properties.add(key)

    def set_property(self, key, value):
        if key in self.properties:
            return
        self.update_property(key, value)

    def clear_property(self, key):
        self.common_monitor_functions_instance.clear_property(key)
        self.properties.discard(key)

    @cached_property
    def cast(self):
        return self.item.get('cast') or []

    @cached_property
    def art(self):
        return self.item.get('art') or {}

    @cached_property
    def ratings(self):
        return self.item.get('ratings') or {}

    @cached_property
    def infolabels(self):
        infolabels = self.item.get('infolabels') or {}
        return infolabels

    @cached_property
    def infoproperties(self):
        return self.item.get('infoproperties') or {}

    @cached_property
    def unique_ids(self):  # TODO: DOUBLE CHECK CORRECT?
        return self.item.get('unique_ids') or {}

    @cached_property
    def duration(self):
        return self.infolabels.get('duration')

    @cached_property
    def premiered(self):
        return self.infolabels.get('premiered')

    def set_info_properties(self, dictionary: dict, affix=None):
        if not dictionary:
            return

        if not isinstance(dictionary, dict):
            return

        for k, v in dictionary.items():
            if v is None:
                continue

            if affix:
                k = f'{k}_{affix}'

            if isinstance(v, list):
                self.set_property(k, ' / '.join(v))
                continue

            if isinstance(v, dict):
                continue

            self.set_property(k, v)

    def set_properties(self):
        self.set_info_properties(self.art)
        self.set_info_properties(self.unique_ids, affix='id')
        self.set_single_property('premiered', self.infoproperties)  # Set Premiered first from infoproperties to ensure correct formatting for shortdate
        self.set_info_properties(self.infolabels)
        self.set_info_properties(self.infoproperties)

    def clear_properties(self, ignore_keys=None):
        for k in self.properties - (ignore_keys or set()):
            self.clear_property(k)


class CommonMonitorFunctions(WindowPropertySetter, CommonMonitorDetails):
    def __init__(self):
        self.cur_item_instance = None
        self.pre_item_instance = None
        self.cur_ratings_item_instance = None
        self.pre_ratings_item_instance = None
        self.property_prefix = 'ListItem'
        super().__init__()

    def clear_property(self, key):
        key = f'{self.property_prefix}.{key}'
        self.get_property(key, clear_property=True)

    def set_property(self, key, value):
        key = f'{self.property_prefix}.{key}'
        if value is None:
            self.get_property(key, clear_property=True)
            return
        self.get_property(key, set_property=f'{value}')

    @kodi_try_except('lib.monitor.common set_properties')
    def set_properties(self, item):
        self.pre_item_instance = self.cur_item_instance
        self.cur_item_instance = CommonMonitorItem(self, item)
        self.cur_item_instance.set_properties()
        if not self.pre_item_instance:
            return
        self.pre_item_instance.clear_properties(ignore_keys=self.cur_item_instance.properties)

    @kodi_try_except('lib.monitor.common set_ratings_properties')
    def set_ratings_properties(self, item):
        self.pre_ratings_item_instance = self.cur_ratings_item_instance
        self.cur_ratings_item_instance = CommonMonitorItem(self, item)
        self.cur_ratings_item_instance.set_info_properties(self.cur_ratings_item_instance.ratings)
        if not self.pre_ratings_item_instance:
            return
        self.pre_ratings_item_instance.clear_properties(ignore_keys=self.cur_ratings_item_instance.properties)

    @kodi_try_except('lib.monitor.common clear_properties')
    def clear_properties(self):
        if self.cur_item_instance:
            self.cur_item_instance.clear_properties()
            self.cur_item_instance = None
            self.pre_item_instance = None

        if self.cur_ratings_item_instance:
            self.cur_ratings_item_instance.clear_properties()
            self.cur_ratings_item_instance = None
            self.pre_ratings_item_instance = None
