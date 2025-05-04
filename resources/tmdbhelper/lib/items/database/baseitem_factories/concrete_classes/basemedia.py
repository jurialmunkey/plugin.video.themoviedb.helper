from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.baseclass import BaseItem
from tmdbhelper.lib.addon.logger import kodi_log


class MediaItem(BaseItem):
    db_studio_table = 'studio'
    ftv_id = None
    ftv_type = None

    def config_basemeta_db_studio(self, database_obj):
        """ Special function to configure studio cache to switch between studios and networks depending on content type """
        database_obj = self.config_basemeta_db(database_obj)
        database_obj.table = self.db_studio_table
        return database_obj

    @cached_property
    def routes_basemeta_db(self):
        """ Database tables to get additional data from as part of cache getter """
        return {
            'basemeta_db_studio': self.config_basemeta_db_studio
        }

    @cached_property
    def db_table_caches(self):
        """ Database tables that will have data set as part of cache setter """
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('genre'),
            self.return_basemeta_db('country'),
            self.return_basemeta_db('certification'),
            self.return_basemeta_db('video'),
            self.return_basemeta_db('company'),
            self.return_basemeta_db('studio'),
            self.return_basemeta_db('service'),
            self.return_basemeta_db('provider'),
            self.return_basemeta_db('person'),
            self.return_basemeta_db('castmember'),
            self.return_basemeta_db('crewmember'),
            self.return_basemeta_db('unique_id'),
            self.return_basemeta_db('custom'),
            self.return_basemeta_db('fanart_tv'),
            self.return_basemeta_db('art'),

        )

    @cached_property
    def ftv_data(self):
        """ Get data from fanart tv if enabled """
        if not self.has_fanart_tv:
            return
        data = self.common_apis.ftv_api.get_request(
            self.ftv_type, self.ftv_id,
            cache_force=7,  # Force dummy request caching to prevent rerequesting 404s
            cache_fallback={'dummy': None},
            cache_days=30)
        if not data:
            return
        if 'dummy' in data:
            return
        return data

    @cached_property
    def online_data(self):
        """ Get data from online source """
        if not self.online_data_cond:
            return
        # kodi_log(f'SYNC CACHE: {self.online_data_args}', 2)
        tmdb_data = self.online_data_func(*self.online_data_args, **self.online_data_kwgs) or {}
        if not self.ftv_data:
            return tmdb_data
        tmdb_data['fanart_tv'] = self.ftv_data
        return tmdb_data
