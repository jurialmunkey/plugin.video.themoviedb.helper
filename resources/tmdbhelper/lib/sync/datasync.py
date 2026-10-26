#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from jurialmunkey.checks import has_arg_value
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.files.dbdata import DatabaseStatements


class SyncItemDetailsDatabase(ItemDetailsDatabase):
    def get_provider_activity_ids(self, provider_id):
        escaped_id = provider_id.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        items = self.get_list_values(
            table='lactivities', keys=('id',), values=(f'%.{escaped_id}.%',),
            conditions="id LIKE ? ESCAPE '\\'")
        return tuple(item['id'] for item in items)

    def set_activity(self, item_type, method, value, expiry):
        cursor = self.execute_sql(
            DatabaseStatements.insert_or_replace('lactivities', keys=('id', 'data', 'expiry')),
            (f'{item_type}.{method}', value, expiry))
        cursor.close() if cursor else None

    def get_activity(self, item_type, method, expiry=0):
        cursor = self.execute_sql(
            DatabaseStatements.select_limit('lactivities', keys=('data', ), conditions='id=? and expiry>=?'),
            (f'{item_type}.{method}', expiry))
        if not cursor:
            return
        result = cursor.fetchone()
        cursor.close()
        if not result:
            return
        return result[0]


class SyncDataGetterAll:

    operator = 'OR'
    query_clauses = ('item_type=?', )  # WHERE {query_clauses}
    query_values = ('', )  # WHERE {query_clauses}={query_values}
    clause_keys = ()  # WHERE {query_clauses} AND ({clause_key} IS NOT NULL {operator} {clause_key} IS NOT NULL)
    additional_keys = ()  # Additional keys to retrieve values for
    query_value_item_argx = 0  # Query value to use as sync item_type (normally item_type query is first ie 0 index)

    def __init__(self, instance_syncdata, provider=None):
        self.instance_syncdata = instance_syncdata
        self.provider = provider

    @cached_property
    def item_type(self):
        return self.get_item_type()

    def get_item_type(self):
        return self.query_values[self.query_value_item_argx]

    @cached_property
    def base_keys(self):
        return self.get_base_keys()

    def get_base_keys(self):
        if self.item_type == 'season':
            return ('tmdb_id', 'title', 'season_number', )
        if self.item_type == 'episode':
            return ('tmdb_id', 'title', 'season_number', 'episode_number', )
        return ('tmdb_id', 'title', )

    @cached_property
    def clause(self):
        return self.get_clause()

    def get_clause(self):
        clause = [f'{k} IS NOT NULL' for k in self.clause_keys]
        clause = '({})'.format(f' {self.operator} '.join(clause))
        clause = (*self.query_clauses, clause, )
        clause = ' AND '.join(clause)
        return clause

    @cached_property
    def keys(self):
        return self.get_keys()

    def get_keys(self):
        return (*(self.base_keys or ()), *(self.clause_keys or ()), *(self.additional_keys or ()), )

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        self.instance_syncdata.sync(self.item_type, self.keys)
        return self.instance_syncdata.cache.get_list_values(keys=self.keys, values=self.query_values, conditions=self.clause)


class SyncDataGetterProgressWatchedUnHidden(SyncDataGetterAll):
    query_clauses = ('item_type=?', 'progress_watched_hidden_at IS NULL', )


class SyncDataGetterProgressCollectedUnHidden(SyncDataGetterAll):
    query_clauses = ('item_type=?', 'progress_collected_hidden_at IS NULL', )


class SyncDataGetterCalendarUnHidden(SyncDataGetterAll):
    query_clauses = ('item_type=?', 'calendar_hidden_at IS NULL', )


class SyncDataGetterDroppedWatchedUnHidden(SyncDataGetterAll):
    query_clauses = ('item_type=?', 'dropped_hidden_at IS NULL AND progress_watched_hidden_at IS NULL', )


class SyncDataGetterDroppedCollectionUnHidden(SyncDataGetterAll):
    query_clauses = ('item_type=?', 'dropped_hidden_at IS NULL AND progress_collected_hidden_at IS NULL', )


class SyncDataGetterDroppedCalendarUnHidden(SyncDataGetterAll):
    query_clauses = ('item_type=?', 'dropped_hidden_at IS NULL AND calendar_hidden_at IS NULL', )


class SyncDataGetterAllMoviesToWatch(SyncDataGetterAll):
    query_values = ('movie', )
    clause_keys = ('playback_progress', 'watchlist_listed_at', )
    filter_keys = ()

    def get_keys(self):
        return (*super().get_keys(), *self.filter_keys, )


class SyncDataGetterAllShowsToWatch(SyncDataGetterAll):
    query_values = ('show', )
    clause_keys = ('next_episode_id', 'watchlist_listed_at', )
    filter_keys = ()

    def get_keys(self):
        return (*super().get_keys(), *self.filter_keys, )


class SyncDataGetterAllUnHiddenShowsStarted(SyncDataGetterDroppedWatchedUnHidden):
    query_values = ('show', )
    clause_keys = ('last_watched_at', )


class SyncDataGetterAllUnHiddenShowsNextEpisode(SyncDataGetterDroppedWatchedUnHidden):
    query_values = ('show', )
    clause_keys = ('next_episode_id', )


class SyncDataGetterAllUnHiddenEpisodesUpNext(SyncDataGetterDroppedWatchedUnHidden):  # TODO: UNSURE ABOUT THIS ONE
    query_values = ('episode', )
    clause_keys = ('upnext_episode_id', )


class SyncDataGetterAllEpisodePlaycounts(SyncDataGetterAll):
    query_values = ('episode', )
    clause_keys = ('plays', )
    base_keys = ('id', )


class SyncDataGetterAllItems(SyncDataGetterAll):
    @property
    def query_values(self):
        return (self.item_type, )


class SyncDataGetterAllUnwatchedItems(SyncDataGetterAll):
    query_clauses = ('item_type=?', 'last_watched_at IS NULL')  # WHERE {query_clauses}

    @property
    def query_values(self):
        return (self.item_type, )


class SyncDataGetterAllReleasedItems(SyncDataGetterAll):
    query_clauses = ('item_type=?', 'premiered < date(\'now\')', 'premiered IS NOT NULL')  # WHERE {query_clauses}

    @property
    def query_values(self):
        return (self.item_type, )


class SyncDataGetterAllAnticipatedItems(SyncDataGetterAll):
    query_clauses = ('item_type=?', '(premiered >= date(\'now\') OR premiered IS NULL)')  # WHERE {query_clauses}

    @property
    def query_values(self):
        return (self.item_type, )


class SyncDataGetterAllItemsCollected(SyncDataGetterAllItems):
    clause_keys = ('collection_last_collected_at', )


class SyncDataGetterAllItemsWatchlist(SyncDataGetterAllItems):
    clause_keys = ('watchlist_listed_at', )


class SyncDataGetterAllReleasedItemsWatchlist(SyncDataGetterAllReleasedItems):
    clause_keys = ('watchlist_listed_at', )


class SyncDataGetterAllAnticipatedItemsWatchlist(SyncDataGetterAllAnticipatedItems):
    clause_keys = ('watchlist_listed_at', )


class SyncDataGetterAllItemsFavorites(SyncDataGetterAllItems):
    clause_keys = ('favorites_listed_at', )


class SyncDataGetterAllItemsDropped(SyncDataGetterAllItems):
    clause_keys = ('dropped_hidden_at', )


class SyncDataGetterAllItemsWatched(SyncDataGetterAllItems):
    clause_keys = ('last_watched_at', )


class SyncDataGetterWatchedHistoryStats(SyncDataGetterAllItemsWatched):
    days = 30
    query_clauses = (
        'item_type=?',
        "DATE(last_watched_at, 'localtime') >= DATE('now', 'localtime', ?)",
        "DATE(last_watched_at, 'localtime') <= DATE('now', 'localtime')",
    )

    @property
    def query_values(self):
        return (self.item_type, f'-{self.days - 1} days', )

    def get_keys(self):
        return (
            "DATE(last_watched_at, 'localtime') AS watched_date",
            'COUNT(*) AS watched_count',
        )

    def get_clause(self):
        return f'{super().get_clause()} GROUP BY watched_date ORDER BY watched_date DESC'

    def get_items(self):
        self.instance_syncdata.sync(self.item_type, self.clause_keys)
        return self.instance_syncdata.cache.get_list_values(keys=self.keys, values=self.query_values, conditions=self.clause)


class SyncDataGetterWatchedMonthlyHistoryStats(SyncDataGetterWatchedHistoryStats):
    months = 12
    query_clauses = (
        'item_type=?',
        "DATE(last_watched_at, 'localtime') >= DATE('now', 'localtime', 'start of month', ?)",
        "DATE(last_watched_at, 'localtime') <= DATE('now', 'localtime')",
    )

    @property
    def query_values(self):
        return (self.item_type, f'-{self.months - 1} months', )

    def get_keys(self):
        return (
            "DATE(last_watched_at, 'localtime', 'start of month') AS watched_date",
            'COUNT(*) AS watched_count',
        )


class SyncDataGetterAllItemsPlayback(SyncDataGetterAllItems):
    clause_keys = ('playback_progress', )


class SyncDataGetterAllUnwatchedItemsPlayback(SyncDataGetterAllUnwatchedItems):
    clause_keys = ('playback_progress', )


class SyncDataGetterUnHiddenShowEpisodesUpNext(SyncDataGetterDroppedWatchedUnHidden):
    clause_keys = ('upnext_episode_id', )
    query_clauses = ('item_type=?', 'tmdb_id=?', )

    @property
    def query_values(self):
        return ('episode', self.tmdb_id, )


class SyncDataGetterEmpty:
    items = ()
    keys = ()
    additional_keys = ()

    def __init__(self, instance_syncdata):
        self.instance_syncdata = instance_syncdata


def get_provider_getter(instance_syncdata, name, fallback_class):
    provider = instance_syncdata.registry.get_selected_provider('watched')
    if provider is not None and provider.is_authorized():
        return provider.getter_classes[name](instance_syncdata, provider)
    return fallback_class(instance_syncdata)


def SyncDataGetterAllUnHiddenMoviesToWatch(instance_syncdata):
    return get_provider_getter(instance_syncdata, 'movies_to_watch', SyncDataGetterAllMoviesToWatch)


def SyncDataGetterAllUnHiddenShowsToWatch(instance_syncdata):
    return get_provider_getter(instance_syncdata, 'shows_to_watch', SyncDataGetterAllShowsToWatch)


def SyncDataGetterAllUnHiddenShowsInProgress(instance_syncdata):
    return get_provider_getter(instance_syncdata, 'shows_in_progress', SyncDataGetterEmpty)


class SyncDataGetters:
    """ Add-in class to group getter methods for SyncData class """

    def get_all_unhidden_movies_towatch_getter(self):
        return SyncDataGetterAllUnHiddenMoviesToWatch(self)

    def get_all_unhidden_shows_towatch_getter(self):
        return SyncDataGetterAllUnHiddenShowsToWatch(self)

    def get_all_unhidden_shows_started_getter(self):
        return SyncDataGetterAllUnHiddenShowsStarted(self)

    def get_all_unhidden_shows_nextepisode_getter(self):
        return SyncDataGetterAllUnHiddenShowsNextEpisode(self)

    def get_all_unhidden_episodes_upnext_getter(self):
        return SyncDataGetterAllUnHiddenEpisodesUpNext(self)

    def get_all_episode_playcounts_getter(self):
        return SyncDataGetterAllEpisodePlaycounts(self)

    def get_all_unhidden_shows_inprogress_getter(self):
        return SyncDataGetterAllUnHiddenShowsInProgress(self)

    def get_item_type_getter(self, sync_data_class, item_type):
        sd = sync_data_class(self)
        sd.item_type = item_type
        return sd

    def get_all_dropped_shows_getter(self, item_type):
        return self.get_item_type_getter(SyncDataGetterAllItemsDropped, item_type)

    def get_all_collected_getter(self, item_type):
        return self.get_item_type_getter(SyncDataGetterAllItemsCollected, item_type)

    def get_all_watchlist_getter(self, item_type):
        return self.get_item_type_getter(SyncDataGetterAllItemsWatchlist, item_type)

    def get_all_released_watchlist_getter(self, item_type):
        return self.get_item_type_getter(SyncDataGetterAllReleasedItemsWatchlist, item_type)

    def get_all_anticipated_watchlist_getter(self, item_type):
        return self.get_item_type_getter(SyncDataGetterAllAnticipatedItemsWatchlist, item_type)

    def get_all_favorites_getter(self, item_type):
        return self.get_item_type_getter(SyncDataGetterAllItemsFavorites, item_type)

    def get_all_watched_getter(self, item_type):
        return self.get_item_type_getter(SyncDataGetterAllItemsWatched, item_type)

    def get_watched_history_stats_getter(self, item_type, days):
        sd = self.get_item_type_getter(SyncDataGetterWatchedHistoryStats, item_type)
        sd.days = days
        return sd

    def get_watched_monthly_history_stats_getter(self, item_type, months):
        sd = self.get_item_type_getter(SyncDataGetterWatchedMonthlyHistoryStats, item_type)
        sd.months = months
        return sd

    def get_all_playback_getter(self, item_type):
        return self.get_item_type_getter(SyncDataGetterAllItemsPlayback, item_type)

    def get_all_unwatched_playback_getter(self, item_type):
        return self.get_item_type_getter(SyncDataGetterAllUnwatchedItemsPlayback, item_type)

    def get_tmdb_id_getter(self, sync_data_class, tmdb_id):
        sd = sync_data_class(self)
        sd.tmdb_id = tmdb_id
        return sd

    def get_unhidden_show_episodes_upnext(self, tmdb_id):
        return self.get_tmdb_id_getter(SyncDataGetterUnHiddenShowEpisodesUpNext, tmdb_id)

    def get_movie_playcount(self, tmdb_id):
        return self.get_value('movie', tmdb_id, key='plays')

    def get_movie_playprogress(self, tmdb_id):
        return self.get_value('movie', tmdb_id, key='playback_progress')

    def get_movie_playprogress_id(self, tmdb_id):
        return self.get_value('movie', tmdb_id, key='playback_id')

    def get_episode_playcount(self, tmdb_id, season, episode):
        return self.get_value('tv', tmdb_id, season, episode, key='plays')

    def get_episode_playprogress(self, tmdb_id, season, episode):
        return self.get_value('tv', tmdb_id, season, episode, key='playback_progress')

    def get_episode_playprogress_id(self, tmdb_id, season, episode):
        return self.get_value('tv', tmdb_id, season, episode, key='playback_id')

    def get_episode_airedcount(self, tmdb_id, season=None, episode=None):
        return self.get_value('tv', tmdb_id, season, episode, key='aired_episodes')

    def get_episode_watchedcount(self, tmdb_id, season=None, episode=None):
        return self.get_value('tv', tmdb_id, season, episode, key='watched_episodes')


class SyncData(SyncDataGetters):
    def __init__(self, registry=None):
        self._registry = registry

    @cached_property
    def core_sync(self):
        return self.get_core_sync()

    def get_core_sync(self):
        from tmdbhelper.lib.sync.trakt.datasync import TraktSyncData
        return TraktSyncData(self)

    @cached_property
    def registry(self):
        return self.get_registry()

    def get_registry(self):
        from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
        return self._registry if self._registry is not None else SyncProviderRegistry()

    @cached_property
    def disabled_sync_types(self):
        return set()

    @cached_property
    def unavailable_providers(self):
        return set()

    def get_sync_provider(self, sync_type):
        from tmdbhelper.lib.sync.providers.features import SYNC_FEATURES
        if sync_type in self.core_sync.sync_classes:
            return
        provider = self.registry.get_selected_provider(SYNC_FEATURES[sync_type])
        if provider is not None and provider.is_authorized():
            return provider

    def get_sync_class(self, sync_type):
        if sync_type in self.core_sync.sync_classes:
            return self.core_sync.get_sync_class(sync_type)
        provider = self.get_sync_provider(sync_type)
        if provider is not None:
            return provider.get_sync_class(sync_type)

    def create_sync(self, sync_type, item_type):
        if sync_type in self.core_sync.sync_classes:
            return self.core_sync.create_sync(sync_type, item_type)
        provider = self.get_sync_provider(sync_type)
        if provider is None:
            return
        sync_class = provider.get_sync_class(sync_type)
        if sync_class is not None:
            return sync_class(self, item_type, provider)

    @cached_property
    def routes(self):
        return self.get_routes()

    def get_routes(self):
        return {k: v['sync'] for k, v in self.cache.simplecache_columns.items()}

    @cached_property
    def cache(self):
        return self.get_cache()

    def get_cache(self):
        return SyncItemDetailsDatabase()

    @cached_property
    def window(self):
        return self.get_window()

    def get_window(self):
        from jurialmunkey.window import WindowPropertySetter
        return WindowPropertySetter()

    @staticmethod
    def get_name(tmdb_type, tmdb_id, season=None, episode=None):
        name = f'{tmdb_type}.{tmdb_id}'
        if season is None:
            return name
        name = f'{name}.{season}'
        if episode is None:
            return name
        name = f'{name}.{episode}'
        return name

    @has_arg_value(0, ('tv', 'movie', ))
    def get_values(self, tmdb_type, tmdb_id, season=None, episode=None, keys=None, item_type=None):
        self.sync(item_type or ('show' if tmdb_type == 'tv' else 'movie'), keys)
        return self.cache.get_values(item_id=self.get_name(tmdb_type, tmdb_id, season, episode), keys=keys)

    def get_value(self, tmdb_type, tmdb_id, season=None, episode=None, key=None, item_type=None):
        data = self.get_values(tmdb_type, tmdb_id, season, episode, keys=(key,), item_type=item_type)
        return data[0] if data else None

    def sync(self, item_type, keys, forced=False):
        sync_types = {self.routes[key] for key in keys if self.routes.get(key)}
        for sync_type in sync_types:
            sync_item = self.create_sync(sync_type, item_type)
            if sync_item is not None:
                sync_item.sync(forced=forced)
            elif sync_type not in self.disabled_sync_types:
                self.clear_disabled_sync_type(sync_type)

    def clear_disabled_sync_type(self, sync_type):
        from tmdbhelper.lib.sync.providers.features import SYNC_FEATURES
        keys = tuple(key for key, key_sync_type in self.routes.items() if key_sync_type == sync_type)
        self.cache.del_column_values(keys=keys)
        if sync_type in self.core_sync.sync_classes:
            self.core_sync.clear_activities((sync_type,))
        else:
            self.clear_unavailable_provider_activities(SYNC_FEATURES[sync_type])
        self.disabled_sync_types.add(sync_type)

    def clear_unavailable_provider_activities(self, feature):
        provider_id = self.registry.get_selected_provider_id(feature)
        if not provider_id or provider_id in self.unavailable_providers:
            return
        provider = self.registry.get_selected_provider(feature)
        if provider is not None and provider.is_authorized():
            return  # An unsupported sync type must not invalidate the provider's supported data.
        from tmdbhelper.lib.sync.activity import SyncLastActivities
        for item_id in self.cache.get_provider_activity_ids(provider_id):
            self.cache.del_item(table='lactivities', item_id=item_id)
            self.window.get_property(f'syncdecorators.timerlock.sync_data.{item_id}', clear_property=True)
        SyncLastActivities.clear_provider(self.window, provider_id)
        self.unavailable_providers.add(provider_id)


def SyncDataFactory():
    return SyncData()
