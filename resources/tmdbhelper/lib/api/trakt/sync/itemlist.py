#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from collections import namedtuple


class ItemListSyncDataProperties:
    @cached_property
    def items(self):
        if not self.trakt_syncdata:
            return
        return self.get_items()

    @cached_property
    def additional_keys(self):
        return self.get_additional_keys()

    @cached_property
    def syncdata_getter(self):
        return self.get_syncdata_getter()

    @cached_property
    def presorted_items(self):
        return self.get_presorted_items()

    @cached_property
    def sort_method(self):
        return self.get_sort_method()

    @cached_property
    def sort_key(self):
        return self.get_sort_key()

    @cached_property
    def nonetype(self):
        return self.get_nonetype()

    @cached_property
    def reverse(self):
        return self.get_reverse()

    @property
    def trakt_syncdata(self):
        return self.trakt_api.trakt_syncdata

    @cached_property
    def namedtuple_basic(self):
        BasicTuple = namedtuple("BasicTuple", "item mediatype")
        return BasicTuple

    @cached_property
    def namedtuple_episode(self):
        EpisodeTuple = namedtuple("EpisodeTuple", "item mediatype season_number episode_number")
        return EpisodeTuple

    @property
    def item_types(self):
        if self.item_type == 'both':
            return ('movie', 'show', )
        return (self.item_type, )


class ItemListSyncDataMethods:
    def sort_data(self, data):
        if self.sort_by == 'random':
            import random
            random.shuffle(data)
            return data
        if not self.additional_keys:
            return data
        return sorted(data, key=lambda x: x[0][self.sort_key] if x[0][self.sort_key] is not None else self.nonetype, reverse=self.reverse)

    def make_list(self, sd_func):
        data = []
        for item_type in self.item_types:
            sd = sd_func(item_type)
            sd.additional_keys = self.additional_keys
            data += [self.namedtuple_basic(i, item_type, ) for i in sd.items] if sd.items else []

        if not data:
            return

        data = sorted(data, key=lambda x: x.item[sd.clause_keys[0]], reverse=True)
        return [self.make_item(i) for i in self.sort_data(data) if i]

    def make_item(self, i):
        item = {'id': i.item['tmdb_id'], 'mediatype': i.mediatype, 'title': i.item['title']}
        if i.mediatype in ('season', 'episode', ):
            item['season'] = i.season_number if 'season_number' in i._fields else i.item['season_number']
        if i.mediatype == 'episode':
            item['episode'] = i.episode_number if 'episode_number' in i._fields else i.item['episode_number']
        for k in (self.item_keys or ()):
            try:
                item.setdefault('infoproperties', {})[k] = i.item[k]
            except IndexError:
                pass
        return item


class ItemListSyncData(ItemListSyncDataProperties, ItemListSyncDataMethods):

    # Tuple of column_name, reverse_sort, fallback_nonetype
    sort = {
        'year': ('year', True, 0, ),
        'released': ('premiered', True, '', ),
        'title': ('title', True, '', ),
        'watched': ('last_watched_at', True, '', ),
        'paused': ('playback_paused_at', True, '', ),
        'votes': ('trakt_votes', True, 0, ),
        'plays': ('plays', True, 0, ),
        'runtime': ('runtime', True, 0, ),
        'collected': ('collection_last_collected_at', True, '', ),
        'airdate': ('last_watched_at', True, '', ),
        'todays': ('last_watched_at', True, '', ),
        'lastweek': ('last_watched_at', True, '', ),
    }

    def __init__(self, trakt_api, item_type=None, sort_by=None, sort_how=None, item_keys=None, tmdb_id=None):
        self.trakt_api = trakt_api
        self.sort_by, self.sort_how = sort_by, sort_how
        self.item_keys = item_keys or ()
        self.item_type = item_type
        self.tmdb_id = tmdb_id

    def get_sort_method(self):
        try:
            return self.sort[self.sort_by]
        except KeyError:
            return

    def get_sort_key(self):
        try:
            return self.sort_method[0]
        except TypeError:  # No sort method
            return

    def get_additional_keys(self):
        try:
            return (self.sort_method[0], *self.item_keys)
        except TypeError:  # No sort method
            return

    def get_reverse(self):
        try:
            reverse = self.sort_method[1]
        except TypeError:  # No sort method
            return
        if self.sort_how != 'asc':
            return reverse
        return not reverse

    def get_nonetype(self):
        try:
            return self.sort_method[2]
        except TypeError:  # No sort method
            return


class ItemListSyncDataCollection(ItemListSyncData):
    """ Items in collection """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_collected_getter)


class ItemListSyncDataWatchlist(ItemListSyncData):
    """ Items on watchlist """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_watchlist_getter)


class ItemListSyncDataReleasedWatchlist(ItemListSyncData):
    """ Items on watchlist that have been released """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_released_watchlist_getter)


class ItemListSyncDataAnticipatedWatchlist(ItemListSyncData):
    """ Items on watchlist that have been released """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_anticipated_watchlist_getter)


class ItemListSyncDataWatched(ItemListSyncData):
    """ Items that have been watched """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_watched_getter)


class ItemListSyncDataPlayback(ItemListSyncData):
    """ Episodes and movies partially watched with resume points """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_playback_getter)


class ItemListSyncDataFavorites(ItemListSyncData):
    """ Items in favourites """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_favorites_getter)


class ItemListSyncDataDropped(ItemListSyncData):
    """ Items in favourites """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_dropped_shows_getter)


class ItemListSyncDataUnwatchedPlayback(ItemListSyncData):
    """ Episodes and movies partially watched with resume points """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_unwatched_playback_getter)


class ItemListSyncDataToWatch(ItemListSyncData):
    """ Mix of watchlist and inprogress items """

    @cached_property
    def presorted_fallback_key(self):
        if self.item_type == 'movie':
            return 'playback_paused_at'
        return 'last_watched_at'

    @cached_property
    def syncdata_getter_func(self):
        if self.item_type == 'movie':
            return self.trakt_syncdata.get_all_unhidden_movies_towatch_getter
        return self.trakt_syncdata.get_all_unhidden_shows_towatch_getter

    def get_syncdata_getter(self):
        sd = self.syncdata_getter_func()
        sd.additional_keys = (self.presorted_fallback_key, *self.item_keys, )
        return sd

    def get_presorted_items(self):
        return sorted(self.syncdata_getter.items, key=lambda x: x['watchlist_listed_at'] or x[self.presorted_fallback_key], reverse=True)

    def get_items(self):
        data = [self.namedtuple_basic(i, self.item_type, ) for i in self.presorted_items]
        return [self.make_item(i) for i in self.sort_data(data) if i]


class ItemListSyncDataInProgress(ItemListSyncData):
    """ Partially watched shows that are inprogress """

    def get_syncdata_getter(self):
        sd = self.trakt_syncdata.get_all_unhidden_shows_inprogress_getter()
        sd.additional_keys = self.additional_keys
        return sd

    def get_presorted_items(self):
        return sorted(self.syncdata_getter.items, key=lambda x: x['last_watched_at'], reverse=True)

    def get_items(self):
        data = [self.namedtuple_basic(i, 'show', ) for i in self.presorted_items]
        return [self.make_item(i) for i in self.sort_data(data) if i]


class ItemListSyncDataNextUp(ItemListSyncData):
    """ Episodes next up to watch for all inprogress shows """
    sort_method = ('last_watched_at', True, '', )

    def get_syncdata_getter(self):
        sd = self.trakt_syncdata.get_all_unhidden_shows_nextepisode_getter()
        sd.additional_keys = ('next_episode_aired_at', *self.additional_keys)
        return sd

    def get_presorted_items(self):
        key_presorted = 'next_episode_aired_at' if self.sort_by == 'airdate' else 'last_watched_at'
        return sorted(self.syncdata_getter.items, key=lambda x: x[key_presorted], reverse=True)

    @cached_property
    def sort_by_days(self):
        return -1 if self.sort_by == 'todays' else -7

    def get_special_sorted_item_tuple(self, item):
        from tmdbhelper.lib.addon.tmdate import is_future_timestamp
        if not item['next_episode_aired_at']:
            return (None, item)
        if not is_future_timestamp(
            item['next_episode_aired_at'],
            time_fmt="%Y-%m-%d",
            time_lim=10,
            use_today=True,
            days=self.sort_by_days
        ):
            return (None, item)
        return (item, None)

    @cached_property
    def airsorted_items(self):
        items_a, items_z = zip(*[
            self.get_special_sorted_item_tuple(i)
            for i in self.presorted_items
        ])
        items_a = [i for i in items_a if i]
        items_z = [i for i in items_z if i]
        items_a = sorted(items_a, key=lambda x: x['next_episode_aired_at'], reverse=True)
        return items_a + items_z

    def get_namedtupled_items(self, data):
        return [
            self.make_item(j)
            for j in (
                self.namedtuple_episode(
                    i,
                    'episode',
                    i['next_episode_id'].split('.')[2],
                    i['next_episode_id'].split('.')[3],
                ) for i in data
            ) if j
        ]

    def get_items(self):
        if self.sort_by in ('todays', 'lastweek'):
            return self.get_namedtupled_items(self.airsorted_items)
        if self.sort_by in ('airdate', 'recentlywatched'):
            return self.get_namedtupled_items(self.presorted_items)


class ItemListSyncDataUpNext(ItemListSyncData):
    """ Episodes Up Next for specific tmdb_id show """

    def get_syncdata_getter(self):
        sd = self.trakt_syncdata.get_unhidden_show_episodes_upnext(self.tmdb_id)
        sd.additional_keys = self.additional_keys
        return sd

    def get_presorted_items(self):
        return [
            self.namedtuple_episode(i, 'episode', i['upnext_episode_id'].split('.')[2], i['upnext_episode_id'].split('.')[3], )
            for i in self.syncdata_getter.items]

    def get_items(self):
        return [self.make_item(i) for i in self.sort_data(self.presorted_items) if i]


def ItemListSyncDataFactory(sync_type, *args, **kwargs):

    routes = {
        'collection': ItemListSyncDataCollection,
        'watchlist': ItemListSyncDataWatchlist,
        'watchlistreleased': ItemListSyncDataReleasedWatchlist,
        'watchlistanticipated': ItemListSyncDataAnticipatedWatchlist,
        'watched': ItemListSyncDataWatched,
        'playback': ItemListSyncDataPlayback,
        'favorites': ItemListSyncDataFavorites,
        'dropped': ItemListSyncDataDropped,
        'nextup': ItemListSyncDataNextUp,
        'upnext': ItemListSyncDataUpNext,
        'inprogress': ItemListSyncDataInProgress,
        'towatch': ItemListSyncDataToWatch,
        'unwatchedplayback': ItemListSyncDataUnwatchedPlayback,
    }

    return routes[sync_type](*args, **kwargs)
