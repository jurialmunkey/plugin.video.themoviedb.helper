from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.database.tabledef import (
    BASEITEM_COLUMNS,
    MOVIE_COLUMNS,
    TVSHOW_COLUMNS,
    SEASON_COLUMNS,
    EPISODE_COLUMNS,
    COLLECTION_COLUMNS,
    RATINGS_COLUMNS,
    PERSON_COLUMNS,
    CERTIFICATION_COLUMNS,
    VIDEO_COLUMNS,
    GENRE_COLUMNS,
    COUNTRY_COLUMNS,
    STUDIO_COLUMNS,
    NETWORK_COLUMNS,
    COMPANY_COLUMNS,
    BROADCASTER_COLUMNS,
    CREWMEMBER_COLUMNS,
    CASTMEMBER_COLUMNS,
    CUSTOM_COLUMNS,
    PROVIDER_COLUMNS,
    SERVICE_COLUMNS,
    ART_COLUMNS,
    FANART_TV_COLUMNS,
    UNIQUE_ID_COLUMNS,
    SIMPLECACHE_COLUMNS,
    LACTIVITIES_COLUMNS,
)


class Studio(ItemDetailsList):
    table = 'studio'
    cached_data_parent_table = 'company'
    keys = ('tmdb_id', 'parent_id')

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


class Certification(ItemDetailsList):
    table = 'certification'
    keys = ('name', 'iso_country', 'iso_language', 'release_date', 'release_type', 'parent_id', )
    conditions = 'parent_id=? AND iso_country=? AND name IS NOT NULL AND name != "" ORDER BY IFNULL(release_date, "9999-99-99") ASC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.parent_id, self.common_apis.tmdb_api.iso_country)


class Video(ItemDetailsList):
    table = 'video'
    keys = ('name', 'iso_country', 'iso_language', 'release_date', 'path', 'content', 'key', 'parent_id', )
    conditions = 'parent_id=? AND content=? ORDER BY iso_language=?, release_date DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.parent_id, 'Trailer', self.common_apis.tmdb_api.iso_language)


class Country(ItemDetailsList):
    table = 'country'
    keys = ('name', 'iso_country', 'parent_id', )


class Genre(ItemDetailsList):
    table = 'genre'
    keys = ('name', 'tmdb_id', 'parent_id', )


class UniqueId(ItemDetailsList):
    table = 'unique_id'
    keys = ('key', 'value', 'parent_id', )

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )


class Custom(UniqueId):
    table = 'custom'


class Service(ItemDetailsList):
    table = 'service'
    keys = ('tmdb_id', 'name', 'display_priority', 'iso_country', 'logo')
    conditions = 'tmdb_id=?'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_thumbs(v)


class Provider(ItemDetailsList):
    table = 'provider'
    keys = ('tmdb_id', 'availability', 'parent_id')

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
    keys = ('tmdb_id', 'name', 'logo', 'country')
    conditions = 'tmdb_id=?'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_thumbs(v)


class Broadcaster(Company):
    table = 'broadcaster'


class Base(ItemDetailsList):
    table = 'baseitem'
    keys = ('id', 'mediatype', 'expiry', )


class Movie(ItemDetailsList):
    table = 'movie'
    keys = tuple(MOVIE_COLUMNS.keys())


class Tvshow(ItemDetailsList):
    table = 'tvshow'
    keys = ('id', 'tmdb_id', 'year', 'premiered', 'plot', 'title', 'originaltitle', 'rating', 'votes', 'popularity', 'totalseasons', 'totalepisodes')


class Season(ItemDetailsList):
    table = 'season'
    keys = ('id', 'season', 'year', 'plot', 'title', 'originaltitle', 'premiered', 'status', 'rating', 'votes', 'popularity', 'tvshow_id')


class Episode(ItemDetailsList):
    table = 'episode'
    keys = ('id', 'episode', 'year', 'plot', 'title', 'originaltitle', 'premiered', 'duration', 'status', 'rating', 'votes', 'popularity', 'season_id', 'tvshow_id')


class MovieCollection(ItemDetailsList):
    table = 'collection'
    keys = ('id', 'tmdb_id', 'title', 'plot', 'poster', 'fanart')
