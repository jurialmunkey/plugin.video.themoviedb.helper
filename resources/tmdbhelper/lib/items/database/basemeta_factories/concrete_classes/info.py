from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.database.tabledef import (
    MOVIE_COLUMNS,
    TVSHOW_COLUMNS,
    SEASON_COLUMNS,
    EPISODE_COLUMNS,
    BELONGS_COLUMNS,
    COLLECTION_COLUMNS,
    CERTIFICATION_COLUMNS,
    VIDEO_COLUMNS,
    GENRE_COLUMNS,
    COUNTRY_COLUMNS,
    STUDIO_COLUMNS,
    NETWORK_COLUMNS,
    COMPANY_COLUMNS,
    BROADCASTER_COLUMNS,
    CUSTOM_COLUMNS,
    PROVIDER_COLUMNS,
    SERVICE_COLUMNS,
    UNIQUE_ID_COLUMNS,
)


class Studio(ItemDetailsList):
    table = 'studio'
    cached_data_parent_table = 'company'
    keys = tuple(STUDIO_COLUMNS.keys())

    @property
    def cached_data_keys(self):
        cached_data_keys = ('name', 'tmdb_id', 'logo', 'country')
        return tuple((f'{self.cached_data_parent_table}.{k}' for k in cached_data_keys))

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_thumbs(v)

    @property
    def cached_data_table(self):
        return (
            f'{self.table} INNER JOIN {self.cached_data_parent_table} '
            f'ON {self.cached_data_parent_table}.tmdb_id = {self.table}.tmdb_id'
        )


class Network(Studio):
    table = 'network'
    cached_data_parent_table = 'broadcaster'
    keys = tuple(NETWORK_COLUMNS.keys())


class Certification(ItemDetailsList):
    table = 'certification'
    keys = tuple(CERTIFICATION_COLUMNS.keys())
    conditions = 'parent_id=? AND iso_country=? AND name IS NOT NULL AND name != "" ORDER BY IFNULL(release_date, "9999-99-99") ASC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.parent_id, self.common_apis.tmdb_api.iso_country)


class Video(ItemDetailsList):
    table = 'video'
    keys = tuple(VIDEO_COLUMNS.keys())
    conditions = 'parent_id=? AND content=? ORDER BY iso_language=?, release_date DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.parent_id, 'Trailer', self.common_apis.tmdb_api.iso_language)


class Country(ItemDetailsList):
    table = 'country'
    keys = tuple(COUNTRY_COLUMNS.keys())


class Genre(ItemDetailsList):
    table = 'genre'
    keys = tuple(GENRE_COLUMNS.keys())


class UniqueId(ItemDetailsList):
    table = 'unique_id'
    keys = tuple(UNIQUE_ID_COLUMNS.keys())

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )


class Custom(UniqueId):
    table = 'custom'
    keys = tuple(CUSTOM_COLUMNS.keys())


class Service(ItemDetailsList):
    table = 'service'
    keys = tuple(SERVICE_COLUMNS.keys())
    conditions = 'tmdb_id=?'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_thumbs(v)


class Provider(ItemDetailsList):
    table = 'provider'
    keys = tuple(PROVIDER_COLUMNS.keys())

    cached_data_keys = ('provider.tmdb_id', 'availability', 'name', 'display_priority', 'iso_country', 'logo')
    cached_data_table = 'provider INNER JOIN service ON service.tmdb_id = provider.tmdb_id'

    @cached_property
    def provider_allowlist(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        provider_allowlist = get_setting('provider_allowlist', 'str')
        provider_allowlist = provider_allowlist.split(' | ') if provider_allowlist else []
        provider_allowlist = [f"'{i}'" for i in provider_allowlist]
        provider_allowlist = ', '.join(provider_allowlist)
        provider_allowlist = f'name IN ({provider_allowlist}) AND ' if provider_allowlist else ''
        return provider_allowlist

    @property
    def conditions(self):
        return f'{self.provider_allowlist}parent_id=? AND iso_country=? ORDER BY IFNULL(display_priority, 9999) ASC'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, self.common_apis.tmdb_api.iso_country)

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_thumbs(v)


class Company(ItemDetailsList):
    table = 'company'
    keys = tuple(COMPANY_COLUMNS.keys())
    conditions = 'tmdb_id=?'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_thumbs(v)


class Broadcaster(Company):
    table = 'broadcaster'
    keys = tuple(BROADCASTER_COLUMNS.keys())


class Base(ItemDetailsList):
    table = 'baseitem'
    keys = ('id', 'mediatype', 'expiry')


class Belongs(ItemDetailsList):
    table = 'belongs'
    keys = tuple(BELONGS_COLUMNS.keys())


class Movie(ItemDetailsList):
    table = 'movie'
    keys = tuple(MOVIE_COLUMNS.keys())


class Tvshow(ItemDetailsList):
    table = 'tvshow'
    keys = tuple(TVSHOW_COLUMNS.keys())


class Season(ItemDetailsList):
    table = 'season'
    keys = tuple(SEASON_COLUMNS.keys())


class Episode(ItemDetailsList):
    table = 'episode'
    keys = tuple(EPISODE_COLUMNS.keys())


class Series(ItemDetailsList):
    table = 'collection'
    keys = tuple(COLLECTION_COLUMNS.keys())
