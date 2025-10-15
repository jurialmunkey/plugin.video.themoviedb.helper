#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.files.dbdata import Database
from tmdbhelper.lib.items.database.tabledef import (
    BASEITEM_COLUMNS,
    MOVIE_COLUMNS,
    TVSHOW_COLUMNS,
    SEASON_COLUMNS,
    EPISODE_COLUMNS,
    BELONGS_COLUMNS,
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
    USER_ART_COLUMNS,
    UNIQUE_ID_COLUMNS,
    TRANSLATION_COLUMNS,
    SIMPLECACHE_COLUMNS,
    LACTIVITIES_COLUMNS,
)


class ItemDetailsDatabase(Database):
    cache_filename = 'ItemDetails.db'

    def __init__(self):
        super().__init__(filename=self.cache_filename)

    # DB version must be max of table_version
    database_version = 33

    database_changes = {
        21: (
            'ALTER TABLE tvshow ADD totalseasons INTEGER',
            'ALTER TABLE tvshow ADD totalepisodes INTEGER',
        ),
        22: (),
        23: (
            'ALTER TABLE baseitem ADD datalevel INTEGER DEFAULT 0 NOT NULL',
        ),
        24: (
            'ALTER TABLE tvshow ADD last_episode_to_air_id TEXT',
        ),
        25: (),
        26: (),
        27: (),
        28: (
            'DROP TABLE IF EXISTS unique_id',
            'DROP TABLE IF EXISTS fanart_tv',
            'DROP TABLE IF EXISTS art',
            'DROP TABLE IF EXISTS service',
            'DROP TABLE IF EXISTS provider',
            'DROP TABLE IF EXISTS custom',
            'DROP TABLE IF EXISTS castmember',
            'DROP TABLE IF EXISTS crewmember',
            'DROP TABLE IF EXISTS broadcaster',
            'DROP TABLE IF EXISTS company',
            'DROP TABLE IF EXISTS network',
            'DROP TABLE IF EXISTS studio',
            'DROP TABLE IF EXISTS country',
            'DROP TABLE IF EXISTS genre',
            'DROP TABLE IF EXISTS video',
            'DROP TABLE IF EXISTS certification',
            'DROP TABLE IF EXISTS person',
            'DROP TABLE IF EXISTS ratings',
            'DROP TABLE IF EXISTS collection',
            'DROP TABLE IF EXISTS belongs',
            'DROP TABLE IF EXISTS episode',
            'DROP TABLE IF EXISTS season',
            'DROP TABLE IF EXISTS tvshow',
            'DROP TABLE IF EXISTS movie',
            'DROP TABLE IF EXISTS baseitem',
        ),
        29: (),
        30: (),
        31: (
            'DROP TABLE IF EXISTS simplecache',
            'DROP TABLE IF EXISTS lactivities',
        ),
        32: (
            'ALTER TABLE baseitem ADD fanart_tv INTEGER DEFAULT 0 NOT NULL',
        ),
        33: (
            'ALTER TABLE baseitem ADD language TEXT',
        ),
    }

    baseitem_columns = BASEITEM_COLUMNS
    movie_columns = MOVIE_COLUMNS
    tvshow_columns = TVSHOW_COLUMNS
    season_columns = SEASON_COLUMNS
    episode_columns = EPISODE_COLUMNS
    belongs_columns = BELONGS_COLUMNS
    collection_columns = COLLECTION_COLUMNS
    ratings_columns = RATINGS_COLUMNS
    person_columns = PERSON_COLUMNS
    certification_columns = CERTIFICATION_COLUMNS
    video_columns = VIDEO_COLUMNS
    genre_columns = GENRE_COLUMNS
    country_columns = COUNTRY_COLUMNS
    studio_columns = STUDIO_COLUMNS
    network_columns = NETWORK_COLUMNS
    company_columns = COMPANY_COLUMNS
    broadcaster_columns = BROADCASTER_COLUMNS
    crewmember_columns = CREWMEMBER_COLUMNS
    castmember_columns = CASTMEMBER_COLUMNS
    custom_columns = CUSTOM_COLUMNS
    provider_columns = PROVIDER_COLUMNS
    service_columns = SERVICE_COLUMNS
    art_columns = ART_COLUMNS
    fanart_tv_columns = FANART_TV_COLUMNS
    user_art_columns = USER_ART_COLUMNS
    unique_id_columns = UNIQUE_ID_COLUMNS
    translation_columns = TRANSLATION_COLUMNS
    simplecache_columns = SIMPLECACHE_COLUMNS
    lactivities_columns = LACTIVITIES_COLUMNS

    @property
    def database_tables(self):
        return {
            'baseitem': self.baseitem_columns,
            'belongs': self.belongs_columns,
            'collection': self.collection_columns,
            'movie': self.movie_columns,
            'tvshow': self.tvshow_columns,
            'season': self.season_columns,
            'episode': self.episode_columns,
            'ratings': self.ratings_columns,
            'person': self.person_columns,
            'genre': self.genre_columns,
            'country': self.country_columns,
            'studio': self.studio_columns,
            'company': self.company_columns,
            'network': self.network_columns,
            'broadcaster': self.broadcaster_columns,
            'video': self.video_columns,
            'certification': self.certification_columns,
            'crewmember': self.crewmember_columns,
            'castmember': self.castmember_columns,
            'provider': self.provider_columns,
            'service': self.service_columns,
            'custom': self.custom_columns,
            'art': self.art_columns,
            'fanart_tv': self.fanart_tv_columns,
            'user_art': self.user_art_columns,
            'unique_id': self.unique_id_columns,
            'translation': self.translation_columns,
            'simplecache': self.simplecache_columns,
            'lactivities': self.lactivities_columns,
        }
