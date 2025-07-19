#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from jurialmunkey.checks import has_arg_value
from tmdbhelper.lib.addon.consts import LASTACTIVITIES_DATA
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.files.dbdata import DatabaseStatements


class SyncItemDetailsDatabase(ItemDetailsDatabase):
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


class SyncDataSetters:
    """ Add-in class to group setter methods for SyncData class """

    def like_userlist(self, user_slug=None, list_slug=None, confirmation=False, delete=False):
        from tmdbhelper.lib.addon.plugin import get_localized
        func = self.delete_response if delete else self.post_response
        response = func('users', user_slug, 'lists', list_slug, 'like')
        if confirmation:
            from xbmcgui import Dialog
            affix = get_localized(32320) if delete else get_localized(32321)
            body = [
                get_localized(32316).format(affix),
                get_localized(32168).format(list_slug, user_slug)
            ] if response.status_code == 204 else [
                get_localized(32317).format(affix),
                get_localized(32168).format(list_slug, user_slug),
                get_localized(32318).format(response.status_code)
            ]
            Dialog().ok(get_localized(32315), '\n'.join(body))
        if response.status_code == 204:
            return response


class SyncDataGetterAll:

    operator = 'OR'
    query_clauses = ('item_type=?', )  # WHERE {query_clauses}
    query_values = ('', )  # WHERE {query_clauses}={query_values}
    clause_keys = ()  # WHERE {query_clauses} AND ({clause_key} IS NOT NULL {operator} {clause_key} IS NOT NULL)
    additional_keys = ()  # Additional keys to retrieve values for
    query_value_item_argx = 0  # Query value to use as sync item_type (normally item_type query is first ie 0 index)

    def __init__(self, instance_syncdata):
        self.instance_syncdata = instance_syncdata  # The SyncData object sync called from

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


class SyncDataGetterAllUnHiddenMoviesToWatch(SyncDataGetterProgressWatchedUnHidden):
    query_values = ('movie', )
    clause_keys = ('playback_progress', 'watchlist_listed_at', )


class SyncDataGetterAllUnHiddenShowsToWatch(SyncDataGetterDroppedWatchedUnHidden):
    query_values = ('show', )
    clause_keys = ('next_episode_id', 'watchlist_listed_at', )


class SyncDataGetterAllUnHiddenShowsStarted(SyncDataGetterDroppedWatchedUnHidden):
    query_values = ('show', )
    clause_keys = ('last_watched_at', )


class SyncDataGetterAllUnHiddenShowsNextEpisode(SyncDataGetterDroppedWatchedUnHidden):
    query_values = ('show', )
    clause_keys = ('next_episode_id', )


class SyncDataGetterAllUnHiddenEpisodesUpNext(SyncDataGetterDroppedWatchedUnHidden):  # TODO: UNSURE ABOUT THIS ONE
    query_values = ('episode', )
    clause_keys = ('upnext_episode_id', )


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


class SyncDataGetterAllUnHiddenShowsInProgress:
    calendar_startdate = -14
    calendar_days = 15
    additional_keys = ()

    def __init__(self, instance_syncdata):
        self.instance_syncdata = instance_syncdata

    @property
    def get_episode_watchedcount(self):
        return self.instance_syncdata.get_episode_watchedcount

    @property
    def get_episode_playcount(self):
        return self.instance_syncdata.get_episode_playcount

    @cached_property
    def calendar_data(self):
        return self.get_calendar_data()

    def get_calendar_data(self):
        from tmdbhelper.lib.items.directories.trakt.lists_calendar import ListTraktCalendarProperties
        list_properties = ListTraktCalendarProperties()
        list_properties.trakt_api = self.instance_syncdata.trakt_api
        list_properties.trakt_date = self.calendar_startdate
        list_properties.trakt_days = self.calendar_days
        list_properties.trakt_type = 'episode'
        return list_properties.api_response_json

    @cached_property
    def calendar_episodes(self):
        return self.get_calendar_episodes()

    def get_calendar_episodes(self):
        from tmdbhelper.lib.addon.tmdate import date_in_range
        from tmdbhelper.lib.addon.plugin import get_setting

        if not get_setting('nextepisodes_usecalendar'):
            return

        if not self.calendar_data:
            return

        calendar = {}

        for i in self.calendar_data:
            try:
                # Check that date is still in range once utc_converted
                if not date_in_range(
                    i['first_aired'],
                    utc_convert=True,
                    start_date=self.calendar_startdate,
                    days=self.calendar_days
                ):
                    continue

                # Ignore specials
                if i['episode']['season'] == 0:
                    continue

                show = calendar.setdefault(i['show']['ids']['tmdb'], {})
                show.setdefault(i['episode']['season'], []).append(i['episode']['number'])

            except KeyError:
                continue

        return calendar

    def is_calendar_watched(self, tmdb_id):
        if not self.calendar_episodes:
            return True
        if tmdb_id not in self.calendar_episodes:
            return True
        for season in self.calendar_episodes[tmdb_id]:
            # Check for a new season airing
            if not self.get_episode_watchedcount(tmdb_id, season):
                return False
            # Check for a new episode airing
            for episode in self.calendar_episodes[tmdb_id][season]:
                if not self.get_episode_playcount(tmdb_id, season, episode):
                    return False
        return True

    def is_inprogress_show(self, tmdb_id, aired_episodes, watched_episodes):
        if aired_episodes <= watched_episodes:
            if self.is_calendar_watched(tmdb_id):
                return False
        return True

    @cached_property
    def parent_getter(self):
        return self.get_parent_getter()

    def get_parent_getter(self):
        sd = self.instance_syncdata.get_all_unhidden_shows_started_getter()
        sd.additional_keys = self.parent_additional_keys
        return sd

    @cached_property
    def keys(self):
        return self.get_keys()

    def get_keys(self):
        return self.parent_getter.keys

    @property
    def parent_additional_keys(self):
        return ('aired_episodes', 'watched_episodes', 'dropped_hidden_at', 'last_watched_at', *(self.additional_keys or ()))

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        sd = self.parent_getter
        return [
            i for i in sd.items
            if self.is_inprogress_show(
                i['tmdb_id'],
                i['aired_episodes'],
                i['watched_episodes']
            )
        ]


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

    def __init__(self, trakt_api):
        self.trakt_api = trakt_api  # The TraktAPI object sync called from

    def delete_response(self, *args, **kwargs):
        return self.trakt_api.delete_response(*args, **kwargs)

    def post_response(self, *args, **kwargs):
        return self.trakt_api.post_response(*args, **kwargs)

    def get_response_json(self, *args, **kwargs):
        return self.trakt_api.get_response_json(*args, **kwargs)

    @cached_property
    def routes(self):
        return self.get_routes()

    def get_routes(self):
        return {k: v['sync'] for k, v in self.cache.simplecache_columns.items()}

    def reset_lastactivities(self):
        self.window.get_property(LASTACTIVITIES_DATA, clear_property=True)  # Wipe new last activities cache

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
    def get_values(self, tmdb_type, tmdb_id, season=None, episode=None, keys=None):
        self.sync('show' if tmdb_type == 'tv' else 'movie', keys)
        return self.cache.get_values(item_id=self.get_name(tmdb_type, tmdb_id, season, episode), keys=keys)

    def get_value(self, tmdb_type, tmdb_id, season=None, episode=None, key=None):
        data = self.get_values(tmdb_type, tmdb_id, season, episode, keys=(key,))
        return data[0] if data else None

    def sync(self, item_type, keys, forced=False):
        from jurialmunkey.modimp import importmodule
        for route in set([j for j in (self.routes.get(k) for k in keys) if j]):
            importmodule(*route)(self, item_type).sync(forced=forced)
