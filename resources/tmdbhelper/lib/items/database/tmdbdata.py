#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.files.ftools import cached_property, threaded_cached_property
from tmdbhelper.lib.addon.tmdate import set_timestamp
from tmdbhelper.lib.items.database.database import ItemDetailsDataBase
from tmdbhelper.lib.items.database.mappings import ItemMapper
from tmdbhelper.lib.files.database import DataBaseCache
# from tmdbhelper.lib.files.locker import mutexlock
# from tmdbhelper.lib.addon.logger import textviewer_output
# from tmdbhelper.lib.addon.logger import timer_report
# from tmdbhelper.lib.addon.logger import kodi_log


class ItemDetailsDataBaseCache(DataBaseCache):
    cache_filename = 'ItemDetails.db'

    table = None  # Table in database
    conditions = 'id=?'  # WHERE conditions
    values = ()  # WHERE conditions values for ?
    keys = ()  # Keys to lookup
    online_data_func = None  # The function to get data e.g. get_response_json
    online_data_args = ()  # ARGS for online_data_func
    online_data_kwgs = {}  # KWGS for online_data_func
    data_cond = True  # Condition to retrieve any data

    @threaded_cached_property
    def cache(self):
        return ItemDetailsDataBase(filename=self.cache_filename)

    @cached_property
    def window(self):
        from jurialmunkey.window import WindowPropertySetter
        return WindowPropertySetter()

    @threaded_cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    @threaded_cached_property
    def tmdb_imagepath(self):
        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
        return TMDbImagePath()

    @threaded_cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    @staticmethod
    def get_base_id(tmdb_type, tmdb_id):
        return f'{tmdb_type}.{tmdb_id}'

    @staticmethod
    def get_season_id(tmdb_type, tmdb_id, season):
        return f'{tmdb_type}.{tmdb_id}.{season}'

    @staticmethod
    def get_episode_id(tmdb_type, tmdb_id, season, episode):
        return f'{tmdb_type}.{tmdb_id}.{season}.{episode}'

    @property
    def online_data_cond(self):
        """ condition to determine whether to retrieve online data - defaults to data_cond """
        return self.data_cond

    @cached_property
    def online_data(self):
        """ cache online data from func to property """
        if not self.online_data_cond:
            return
        return self.online_data_func(*self.online_data_args, **self.online_data_kwgs)

    def get_online_data(self):
        """ function called when local cache does not have any data """
        return self.online_data

    @cached_property
    def data(self):
        if not self.data_cond:
            return
        return self.use_cached_many(
            self.table, self.keys, self.values, self.conditions,
            self.get_online_data
        )

    @property
    def item_info(self):
        return self.table

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )

    def get_configure_mapped_data(self, data, k):
        if k == 'tvshow_id':
            return self.tvshow_id
        if k == 'season_id':
            return self.season_id
        return data[self.item_info][k]

    def configure_mapped_data(self, data):
        return {self.item_id: [self.get_configure_mapped_data(data, k) for k in self.keys]}


class ItemDetailsListDataBaseCache(ItemDetailsDataBaseCache):
    conditions = 'parent_id=?'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.parent_id, )

    @property
    def cached_data_table(self):
        return self.table

    @property
    def cached_data_keys(self):
        return self.keys

    def get_cached_data(self):
        return self.get_cached_list_values(self.cached_data_table, self.cached_data_keys, self.values, self.conditions)

    @cached_property
    def cached_data(self):
        return self.get_cached_data()

    def get_configure_mapped_data_list(self, i, k):
        if k == 'parent_id':
            return self.item_id
        return i.get(k)

    def configure_mapped_data_list(self, data):
        return [tuple([self.get_configure_mapped_data_list(i, k) for k in self.keys]) for i in data[self.table]]

    def set_cached_data(self, online_data_mapped, return_data=False):
        self.set_cached_list_values(self.table, self.keys, self.configure_mapped_data_list(online_data_mapped))
        if not return_data:
            return
        return self.get_cached_data()


class ArtDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'art'
    keys = ('aspect_ratio', 'height', 'width', 'iso_language', 'icon', 'type', 'extension', 'vote_average', 'vote_count', 'parent_id',)
    conditions = 'parent_id=? ORDER BY vote_average DESC'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?  self.tmdb_api.iso_language
        return (self.item_id, )


class ArtTypeDetailsDataBaseCache(ArtDetailsDataBaseCache):
    conditions = 'parent_id=? AND type=? ORDER BY vote_average DESC LIMIT 1'  # WHERE conditions

    def image_path_func(self, v):
        return self.tmdb_imagepath.get_imagepath_fanart(v)

    def get_cached_data_by_language(self):
        conditions = f'iso_language=? AND {self.conditions}'
        values = (self.tmdb_api.iso_language, *self.values)
        return self.get_cached_list_values(self.cached_data_table, self.cached_data_keys, values, conditions)

    def get_cached_data_by_english(self):
        conditions = f'iso_language=? AND {self.conditions}'
        values = ('en', *self.values)
        return self.get_cached_list_values(self.cached_data_table, self.cached_data_keys, values, conditions)

    def get_cached_data_by_null(self):
        conditions = f'iso_language IS NULL AND {self.conditions}'
        return self.get_cached_list_values(self.cached_data_table, self.cached_data_keys, self.values, conditions)

    def get_cached_data(self):
        return self.get_cached_data_by_language() or self.get_cached_data_by_english() or self.get_cached_data_by_null()


class ArtPosterDetailsDataBaseCache(ArtTypeDetailsDataBaseCache):
    @property
    def values(self):  # WHERE conditions values for ?  self.tmdb_api.iso_language
        return (self.item_id, 'posters')

    def image_path_func(self, v):
        return self.tmdb_imagepath.get_imagepath_poster(v)


class ArtFanartDetailsDataBaseCache(ArtTypeDetailsDataBaseCache):
    conditions = 'parent_id=? AND type=? AND aspect_ratio=? ORDER BY vote_average DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?  self.tmdb_api.iso_language
        return (self.item_id, 'backdrops', 'landscape')

    def image_path_func(self, v):
        return self.tmdb_imagepath.get_imagepath_fanart(v)

    def get_cached_data(self):
        return self.get_cached_data_by_null()


class ArtLandscapeDetailsDataBaseCache(ArtFanartDetailsDataBaseCache):
    def get_cached_data(self):
        return self.get_cached_data_by_language() or self.get_cached_data_by_english()


class ArtClearlogoDetailsDataBaseCache(ArtTypeDetailsDataBaseCache):
    conditions = 'parent_id=? AND type=? AND extension=? ORDER BY vote_average DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?  self.tmdb_api.iso_language
        return (self.item_id, 'logos', 'png')

    def image_path_func(self, v):
        return self.tmdb_imagepath.get_imagepath_clogos(v)


class StudioDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'studio'
    keys = ('tmdb_id', 'parent_id')

    def image_path_func(self, v):
        return self.tmdb_imagepath.get_imagepath_thumbs(v)

    @property
    def cached_data_table(self):
        table = ' '.join((
            f'{self.table}',
            f'INNER JOIN company ON company.tmdb_id = {self.table}.tmdb_id'
        ))
        return f'({table}) as studiocompany'

    @property
    def cached_data_keys(self):
        return [f'studiocompany.{k}' for k in (*self.keys, 'name', 'tmdb_id', 'logo', 'country')]


class CertificationDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'certification'
    keys = ('name', 'iso_country', 'iso_language', 'release_date', 'release_type', 'parent_id', )
    conditions = 'parent_id=? AND iso_country=? ORDER BY release_date ASC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, self.tmdb_api.iso_country)


class VideoDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'video'
    keys = ('name', 'iso_country', 'iso_language', 'release_date', 'path', 'content', 'parent_id', )
    conditions = 'parent_id=? AND content=? ORDER BY iso_language=?, release_date DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Trailer', self.tmdb_api.iso_language)


class CountryDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'country'
    keys = ('name', 'iso_country', 'parent_id', )


class GenreDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'genre'
    keys = ('name', 'tmdb_id', 'parent_id', )


class UniqueIdDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'unique_id'
    keys = ('key', 'value', 'parent_id', )

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )


class ServiceDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'service'
    keys = ('tmdb_id', 'name', 'display_priority', 'iso_country', 'logo')
    conditions = 'tmdb_id=?'

    def image_path_func(self, v):
        return self.tmdb_imagepath.get_imagepath_thumbs(v)


class ProviderDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'provider'
    keys = ('tmdb_id', 'availability', 'parent_id')
    conditions = 'parent_id=? AND iso_country=? ORDER BY display_priority ASC'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, self.tmdb_api.iso_country)

    def image_path_func(self, v):
        return self.tmdb_imagepath.get_imagepath_thumbs(v)

    @property
    def cached_data_table(self):
        table = ' '.join((
            f'{self.table}',
            f'INNER JOIN service ON service.tmdb_id = {self.table}.tmdb_id'
        ))
        return f'({table}) as providerservice'

    @property
    def cached_data_keys(self):
        return [f'providerservice.{k}' for k in (*self.keys, 'name', 'display_priority', 'iso_country', 'logo')]


class CastMemberDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'castmember'
    keys = ('tmdb_id', 'role', 'ordering', 'parent_id')
    conditions = 'parent_id=? ORDER BY ordering ASC'  # WHERE conditions

    def image_path_func(self, v):
        return self.tmdb_imagepath.get_imagepath_poster(v)

    @property
    def cached_data_table(self):
        table = ' '.join((
            f'{self.table}',
            f'INNER JOIN person ON person.tmdb_id = {self.table}.tmdb_id'
        ))
        return f'({table}) as creditedperson'

    @property
    def cached_data_keys(self):
        return [f'creditedperson.{k}' for k in (*self.keys, 'thumb', 'name', 'gender', 'biography', 'known_for_department')]


class CrewMemberDetailsDataBaseCache(CastMemberDetailsDataBaseCache):
    table = 'crewmember'
    keys = ('tmdb_id', 'role', 'department', 'parent_id')
    conditions = 'parent_id=?'


class DirectorDetailsDataBaseCache(CrewMemberDetailsDataBaseCache):
    conditions = 'parent_id=? AND department=? AND role=?'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Directing', 'Director')


class WriterDetailsDataBaseCache(CrewMemberDetailsDataBaseCache):
    conditions = 'parent_id=? AND department=?'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Writing', )


class PersonDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'person'
    keys = ('tmdb_id', 'thumb', 'name', 'gender', 'biography', 'known_for_department')
    conditions = 'tmdb_id=?'


class CompanyDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'company'
    keys = ('tmdb_id', 'name', 'logo', 'country')
    conditions = 'tmdb_id=?'

    def image_path_func(self, v):
        return self.tmdb_imagepath.get_imagepath_thumbs(v)


class BaseItemDetailsDataBaseCache(ItemDetailsDataBaseCache):
    data_cond = True  # Condition to retrieve any data
    cache_refresh = None  # Set to "never" for cache only, or "force" for forced refresh
    item_info = 'item'
    expiry_time = 30 * 86400  # 30d = 86400 = 60s(1m) * 60m(1h) * 24h(1d)
    db_studio_table = 'studio'
    cached_data_check_key = 'tmdb_id'
    thread_locks = None
    deny_infolabel_keys = ('id', 'tmdb_id', 'parent_id', 'season_id', 'tvshow_id')  # Dont add these keys to infolabels

    @cached_property
    def thread_lock(self):
        if not self.thread_locks:
            from contextlib import nullcontext
            return nullcontext()
        return self.thread_locks[self.mutex_lockname]

    @property
    def expiry(self):
        return self.current_time + self.expiry_time

    @property
    def current_time(self):
        return set_timestamp(0, set_int=True)

    @cached_property
    def keys(self):
        return [k for k in getattr(self.cache, f'{self.table}_columns').keys()]

    @property
    def item_id(self):
        return self.parent_id

    @property
    def parent_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @cached_property
    def item_mapper(self):
        return ItemMapper()

    def get_db_cache(self, database_class):
        dbc = database_class()
        dbc.cache = self.cache
        dbc.mediatype = self.mediatype
        dbc.item_id = self.item_id
        dbc.parent_id = self.parent_id
        dbc.tmdb_api = self.tmdb_api
        dbc.connection = self.connection
        return dbc

    def get_tvshow_db_cache(self, database_class):
        dbc = self.get_db_cache(database_class)
        dbc.item_id = self.tvshow_id
        dbc.parent_id = self.tvshow_id
        dbc.mediatype = 'tvshow'
        return dbc

    def get_season_db_cache(self, database_class):
        dbc = self.get_db_cache(database_class)
        dbc.item_id = self.season_id
        dbc.parent_id = self.season_id
        dbc.mediatype = 'season'
        return dbc

    @cached_property
    def db_art_cache(self):
        return self.get_db_cache(ArtDetailsDataBaseCache)

    @cached_property
    def db_art_poster_cache(self):
        return self.get_db_cache(ArtPosterDetailsDataBaseCache)

    @cached_property
    def db_art_fanart_cache(self):
        return self.get_db_cache(ArtFanartDetailsDataBaseCache)

    @cached_property
    def db_art_clearlogo_cache(self):
        return self.get_db_cache(ArtClearlogoDetailsDataBaseCache)

    @cached_property
    def db_art_tvshow_poster_cache(self):
        return self.get_tvshow_db_cache(ArtPosterDetailsDataBaseCache)

    @cached_property
    def db_art_tvshow_fanart_cache(self):
        return self.get_tvshow_db_cache(ArtFanartDetailsDataBaseCache)

    @cached_property
    def db_art_tvshow_clearlogo_cache(self):
        return self.get_tvshow_db_cache(ArtClearlogoDetailsDataBaseCache)

    @cached_property
    def db_art_season_poster_cache(self):
        return self.get_season_db_cache(ArtPosterDetailsDataBaseCache)

    @cached_property
    def db_art_season_fanart_cache(self):
        return self.get_season_db_cache(ArtFanartDetailsDataBaseCache)

    @cached_property
    def db_art_season_clearlogo_cache(self):
        return self.get_season_db_cache(ArtClearlogoDetailsDataBaseCache)

    @cached_property
    def db_unique_id_tvshow_cache(self):
        return self.get_tvshow_db_cache(UniqueIdDetailsDataBaseCache)

    @cached_property
    def db_unique_id_season_cache(self):
        return self.get_season_db_cache(UniqueIdDetailsDataBaseCache)

    @cached_property
    def db_unique_id_cache(self):
        return self.get_db_cache(UniqueIdDetailsDataBaseCache)

    @cached_property
    def db_genre_cache(self):
        return self.get_db_cache(GenreDetailsDataBaseCache)

    @cached_property
    def db_country_cache(self):
        return self.get_db_cache(CountryDetailsDataBaseCache)

    @cached_property
    def db_video_cache(self):
        return self.get_db_cache(VideoDetailsDataBaseCache)

    @cached_property
    def db_certification_cache(self):
        return self.get_db_cache(CertificationDetailsDataBaseCache)

    @cached_property
    def db_company_cache(self):
        return self.get_db_cache(CompanyDetailsDataBaseCache)

    @cached_property
    def db_service_cache(self):
        return self.get_db_cache(ServiceDetailsDataBaseCache)

    @cached_property
    def db_studio_cache(self):
        dbc = self.get_db_cache(StudioDetailsDataBaseCache)
        dbc.table = self.db_studio_table  # Use networks not studios for TV
        return dbc

    @cached_property
    def db_castmember_cache(self):
        return self.get_db_cache(CastMemberDetailsDataBaseCache)

    @cached_property
    def db_crewmember_cache(self):
        return self.get_db_cache(CrewMemberDetailsDataBaseCache)

    @cached_property
    def db_director_cache(self):
        return self.get_db_cache(DirectorDetailsDataBaseCache)

    @cached_property
    def db_writer_cache(self):
        return self.get_db_cache(WriterDetailsDataBaseCache)

    @cached_property
    def db_person_cache(self):
        return self.get_db_cache(PersonDetailsDataBaseCache)

    @cached_property
    def db_provider_cache(self):
        return self.get_db_cache(ProviderDetailsDataBaseCache)

    @property
    def mutex_lockname(self):
        return f'{self.cache._db_file}.{self.item_id}.lockfile'

    @property
    def online_data_func(self):  # The function to get data e.g. get_response_json
        return self.tmdb_api.get_request_sc

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, )

    @property
    def online_data_kwgs(self):
        return {'append_to_response': self.tmdb_api.append_to_response}

    @cached_property
    def online_data_mapped(self):
        """ function called when local cache does not have any data """
        if not self.online_data:
            return
        data = self.item_mapper.get_info(self.online_data)
        data['item']['mediatype'] = self.mediatype
        return data

    @property
    def cached_data_keys(self):
        """ SELECT """
        return tuple([f'{self.table}.{k}' for k in self.keys])

    @property
    def cached_data_table(self):
        """ FROM """
        return ' '.join((
            'baseitem',
            f'LEFT JOIN {self.table} ON {self.table}.id = baseitem.id'
        ))

    @property
    def cached_data_conditions(self):
        """ WHERE """
        return f'baseitem.id=? AND baseitem.expiry>=?'

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.item_id, self.current_time, )

    def db_baseitem_cache_get_parent_data(self):
        return

    def db_baseitem_cache_set_cached_data(self):
        self.set_cached_values('baseitem', self.item_id, keys=('mediatype', 'expiry'), values=(self.mediatype, self.expiry))
        self.set_cached_many(self.table, self.keys, self.configure_mapped_data(self.online_data_mapped))

    @property
    def db_table_caches(self):
        return (
            self.db_genre_cache,
            self.db_country_cache,
            self.db_certification_cache,
            self.db_video_cache,
            self.db_company_cache,
            self.db_studio_cache,
            self.db_service_cache,
            self.db_provider_cache,
            self.db_person_cache,
            self.db_castmember_cache,
            self.db_crewmember_cache,
            self.db_unique_id_cache,
            self.db_art_cache,
        )

    def set_cached_data(self, return_data=False):
        with self.thread_lock:
            if not self.online_data_mapped:
                return

            self.db_baseitem_cache_get_parent_data()

            with self.cache.get_database() as self.connection:
                self.db_baseitem_cache_set_cached_data()

                for db_cache in self.db_table_caches:
                    db_cache.set_cached_data(self.online_data_mapped)
            self.connection = None

            if not return_data:
                return

        return self.get_cached_data()

    def database_connection(func):
        def wrapper(self, *args, **kwargs):
            with self.cache.get_database() as self.connection:
                data = func(self, *args, **kwargs)
            self.connection = None
            return data
        return wrapper

    @staticmethod
    def get_configured_item_value(i, ikey, instance):
        if ikey not in ('thumb', 'logo', ):
            return i[ikey]
        return instance.image_path_func(i[ikey])

    @database_connection
    def get_cached_data(self):
        data = self.get_cached_list_values(self.cached_data_table, self.cached_data_keys, self.cached_data_values, self.cached_data_conditions)

        if not data or not data[0] or not data[0][self.cached_data_check_key]:
            return

        """
        INFOLABELS
        """
        infolabels = {k: data[0][k] for k in data[0].keys() if k not in self.deny_infolabel_keys}

        # instance, key from instance item, infolabel [list methods]
        infolabel_routes = (
            (self.db_genre_cache, 'name', 'genre'),
            (self.db_country_cache, 'name', 'country'),
            (self.db_studio_cache, 'name', 'studio'),
            (self.db_director_cache, 'name', 'director'),
            (self.db_writer_cache, 'name', 'writer'),
        )

        for instance, ikey, dkey in infolabel_routes:
            try:
                infolabels[dkey] = [i[ikey] for i in instance.cached_data]
            except (IndexError, TypeError, KeyError):
                pass

        # instance, key from instance item, infolabel [item methods]
        infolabel_routes = (
            (self.db_certification_cache, 'name', 'mpaa'),
            (self.db_video_cache, 'path', 'trailer'),
        )

        for instance, ikey, dkey in infolabel_routes:
            try:
                infolabels[dkey] = instance.cached_data[0][ikey]
            except (IndexError, TypeError, KeyError):
                pass

        if self.mediatype == 'tvshow':
            try:
                infolabels['tvshowtitle'] = infolabels['title']
            except (TypeError, KeyError):
                pass

        """
        INFOPROPERTIES
        """

        infoproperties = {}

        # instance, dictionary of infoproperty name and key from instance item, infoproperty basename, tuple pair of infoproperty and key value to concatenate as separated list
        infoproperty_routes = (
            (self.db_genre_cache, {'name': 'name', 'tmdb_id': 'tmdb_id'}, 'genre', None),
            (self.db_country_cache, {'name': 'name', 'iso_country': 'iso_country'}, 'country', None),
            (self.db_studio_cache, {'name': 'name', 'tmdb_id': 'tmdb_id', 'logo': 'logo', 'country': 'country'}, 'studio', None),
            (self.db_provider_cache, {'name': 'name', 'tmdb_id': 'tmdb_id', 'type': 'availability', 'logo': 'logo'}, 'provider', ('providers', 'name')),
            (self.db_castmember_cache, {'name': 'name', 'tmdb_id': 'tmdb_id', 'role': 'role', 'thumb': 'thumb'}, 'cast', ('cast', 'name')),
            (self.db_crewmember_cache, {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'thumb': 'thumb'}, 'crew', ('crew', 'name')),
            (self.db_director_cache, {'name': 'name', 'tmdb_id': 'tmdb_id', 'role': 'role', 'thumb': 'thumb'}, 'director', ('director', 'name')),
            (self.db_writer_cache, {'name': 'name', 'tmdb_id': 'tmdb_id', 'role': 'role', 'thumb': 'thumb'}, 'writer', ('writer', 'name')),
        )

        for instance, keys, prop, ckey in infoproperty_routes:
            for x, i in enumerate(instance.cached_data):
                for dkey, ikey in keys.items():
                    infoproperties[f'{prop}.{x}.{dkey}'] = self.get_configured_item_value(i, ikey, instance)
            if ckey is None:
                continue
            join_data = [i[ckey[1]] for i in instance.cached_data if i[ckey[1]]]
            infoproperties[ckey[0]] = ' / '.join(join_data)
            infoproperties[f'{ckey[0]}_CR'] = '[CR]'.join(join_data)

        if self.mediatype == 'episode':
            infoproperties['episode_type'] = data[0]['status']

        """
        CAST
        """

        cast = [
            {
                'name': i['name'],
                'role': i['role'],
                'order': i['ordering'],
                'thumbnail': self.tmdb_imagepath.get_imagepath_poster(i['thumb'])
            }
            for i in self.db_castmember_cache.cached_data
        ]

        """
        ART
        """

        art = {}

        artwork_routes = (
            (self.db_art_poster_cache, 'poster'),
            (self.db_art_fanart_cache, 'fanart'),
            (self.db_art_clearlogo_cache, 'clearlogo'),
        )

        for instance, dkey in artwork_routes:
            art[dkey] = instance.image_path_func(instance.cached_data[0]['icon'] if instance.cached_data else None)

        if self.mediatype == 'episode':
            artwork_routes = (
                (self.db_art_season_poster_cache, 'poster'),
                (self.db_art_season_fanart_cache, 'fanart'),
                (self.db_art_season_clearlogo_cache, 'clearlogo'),
            )

            for instance, dkey in artwork_routes:
                art[dkey] = art[dkey] or instance.image_path_func(instance.cached_data[0]['icon'] if instance.cached_data else None)
                art[f'season.{dkey}'] = instance.image_path_func(instance.cached_data[0]['icon'] if instance.cached_data else None)

        if self.mediatype in ('season', 'episode'):
            artwork_routes = (
                (self.db_art_tvshow_poster_cache, 'poster'),
                (self.db_art_tvshow_fanart_cache, 'fanart'),
                (self.db_art_tvshow_clearlogo_cache, 'clearlogo'),
            )

            for instance, dkey in artwork_routes:
                art[dkey] = art[dkey] or instance.image_path_func(instance.cached_data[0]['icon'] if instance.cached_data else None)
                art[f'tvshow.{dkey}'] = instance.image_path_func(instance.cached_data[0]['icon'] if instance.cached_data else None)

        """
        UNIQUE IDS
        """

        unique_ids = {}

        for i in self.db_unique_id_cache.cached_data:
            unique_ids[i['key']] = i['value']

        if self.mediatype == 'episode':
            for i in self.db_unique_id_season_cache.cached_data:
                unique_ids[f"tvshow.{i['key']}"] = i['value']

        if self.mediatype in ('season', 'episode'):
            for i in self.db_unique_id_tvshow_cache.cached_data:
                unique_ids[f"season.{i['key']}"] = i['value']

        """
        ITEM MAP
        """

        return {
            'infolabels': infolabels,
            'infoproperties': infoproperties,
            'cast': cast,
            'art': art,
            'unique_ids': unique_ids,
        }

    # @mutexlock  # Use a mutex lock on the item_id to avoid double up of setting data or attempting get in middle of set
    def use_cached_data(self):
        return self.get_cached_data() or self.set_cached_data(return_data=True)

    @cached_property
    def data(self):
        return self.get_data()

    # @timer_report
    def get_data(self):
        if not self.data_cond:
            return
        if self.cache_refresh == 'force':
            return self.set_cached_data(return_data=True)
        if self.cache_refresh == 'never':
            return self.get_cached_data()
        return self.use_cached_data()


class MovieItemDetailsDataBaseCache(BaseItemDetailsDataBaseCache):
    table = 'movie'
    tmdb_type = 'movie'


class TVShowItemDetailsDataBaseCache(BaseItemDetailsDataBaseCache):
    table = 'tvshow'
    tmdb_type = 'tv'
    db_studio_table = 'network'


class SeasonItemDetailsDataBaseCache(TVShowItemDetailsDataBaseCache):
    table = 'season'
    cached_data_check_key = 'tvshow_id'

    @property
    def item_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)

    @property
    def tvshow_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, 'season', self.season)

    @property
    def cached_data_table(self):
        """ FROM """
        return ' '.join((
            'baseitem',
            f'LEFT JOIN {self.table} ON {self.table}.id = baseitem.id',
            f'LEFT JOIN tvshow ON tvshow.id = season.tvshow_id'
        ))

    def db_baseitem_cache_get_parent_data(self):
        base_dbc = TVShowItemDetailsDataBaseCache()
        base_dbc.tmdb_api = self.tmdb_api
        base_dbc.connection = self.connection
        base_dbc.mediatype = 'tvshow'
        base_dbc.tmdb_id = self.tmdb_id
        return base_dbc.data

    @property
    def db_table_caches(self):
        return (
            self.db_service_cache,
            self.db_provider_cache,
            self.db_person_cache,
            self.db_castmember_cache,
            self.db_crewmember_cache,
            self.db_unique_id_cache,
            self.db_art_cache,
        )


class EpisodeItemDetailsDataBaseCache(SeasonItemDetailsDataBaseCache):
    table = 'episode'

    @property
    def item_id(self):
        return self.get_episode_id(self.tmdb_type, self.tmdb_id, self.season, self.episode)

    @property
    def season_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, 'season', self.season, 'episode', self.episode)

    @cached_property
    def online_data(self):
        """ cache online data from func to property """
        if not self.online_data_cond:
            return
        data = self.online_data_func(*self.online_data_args, **self.online_data_kwgs)

        trakt_id = self.trakt_api.get_id(self.tmdb_id, 'tmdb', 'show', 'trakt')
        if not trakt_id:
            return data

        trakt_data = self.trakt_api.get_request_sc('shows', trakt_id, 'seasons', self.season, 'episodes', self.episode, extended='full')
        if not trakt_data:
            return data

        trakt_data.update(data)
        return trakt_data

    @property
    def cached_data_table(self):
        """ FROM """
        return ' '.join((
            'baseitem',
            f'LEFT JOIN {self.table} ON {self.table}.id = baseitem.id',
            f'LEFT JOIN season ON season.id = episode.season_id',
            f'LEFT JOIN tvshow ON tvshow.id = episode.tvshow_id',
        ))

    def db_baseitem_cache_get_parent_data(self):
        base_dbc = SeasonItemDetailsDataBaseCache()
        base_dbc.tmdb_api = self.tmdb_api
        base_dbc.connection = self.connection
        base_dbc.mediatype = 'season'
        base_dbc.tmdb_id = self.tmdb_id
        base_dbc.season = self.season
        return base_dbc.data

    @property
    def db_table_caches(self):
        return (
            self.db_service_cache,
            self.db_provider_cache,
            self.db_person_cache,
            self.db_castmember_cache,
            self.db_crewmember_cache,
            self.db_unique_id_cache,
            self.db_art_cache,
        )


def ItemDetailsDataBaseCacheFactory(mediatype, *args, **kwargs):

    routes = {
        'movie': MovieItemDetailsDataBaseCache,
        'tvshow': TVShowItemDetailsDataBaseCache,
        'season': SeasonItemDetailsDataBaseCache,
        'episode': EpisodeItemDetailsDataBaseCache,
    }

    dbc = routes[mediatype](*args, **kwargs)
    dbc.mediatype = mediatype
    return dbc
