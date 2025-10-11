from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.baseclass import BaseItem


class MediaItem(BaseItem):
    ftv_type = None

    @cached_property
    def db_table_caches(self):
        """ Database tables that will have data set as part of cache setter """
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('belongs'),
            self.return_basemeta_db('genre'),
            self.return_basemeta_db('country'),
            self.return_basemeta_db('certification'),
            self.return_basemeta_db('translation'),
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
    def online_data_ftv(self):
        """ Get data from fanart tv if enabled """
        if not self.common_apis.ftv_api:
            return {}

        if not self.ftv_type:
            return {}

        if self.ftv_type == 'tv':
            try:
                ftv_id = self.online_data_tmdb['external_ids']['tvdb_id']
            except (KeyError, TypeError, AttributeError):
                ftv_id = None
        else:
            ftv_id = self.tmdb_id

        if not ftv_id:
            return {}

        data = self.common_apis.ftv_api.get_request(
            self.ftv_type, ftv_id,
            cache_force=7,  # Force dummy request caching to prevent rerequesting 404s
            cache_fallback={'dummy': None},
            cache_days=30)

        if not data:
            return {}

        if 'dummy' in data:
            return {}

        return data

    @cached_property
    def online_data_tmdb(self):
        if not self.online_data_cond:
            return
        return self.online_data_func(*self.online_data_args, **self.online_data_kwgs)

    @cached_property
    def online_data_combined(self):
        data = self.online_data_tmdb
        data['fanart_tv'] = self.online_data_ftv
        return data

    @cached_property
    def online_data(self):
        """ Get data from online source """
        if not self.online_data_cond:
            return
        if not self.online_data_tmdb:
            return {}
        return self.online_data_combined
