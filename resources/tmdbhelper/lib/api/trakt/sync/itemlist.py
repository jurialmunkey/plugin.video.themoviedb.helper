#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.parser import LazyPropertyProtected
from tmdbhelper.lib.addon.thread import ParallelThread


class ItemListSyncData:

    # Tuple of column_name, reverse_sort, fallback_nonetype
    sort = {
        'year': ('year', True, 0, ),
        'released': ('premiered', True, '', ),
        'title': ('title', True, '', ),
        'watched': ('last_watched_at', True, '', ),
        'votes': ('trakt_votes', True, 0, ),
        'plays': ('plays', True, 0, ),
        'runtime': ('runtime', True, 0, ),
        'collected': ('collection_last_collected_at', True, '', ),
        'airdate': ('last_watched_at', True, '', ),
        'todays': ('last_watched_at', True, '', ),
        'lastweek': ('last_watched_at', True, '', ),
    }

    items = LazyPropertyProtected('items')
    additional_keys = LazyPropertyProtected('additional_keys')
    syncdata_getter = LazyPropertyProtected('syncdata_getter')
    argx_dictionary = LazyPropertyProtected('argx_dictionary')
    presorted_items = LazyPropertyProtected('presorted_items')
    sort_method = LazyPropertyProtected('sort_method')
    sort_key = LazyPropertyProtected('sort_key')
    nonetype = LazyPropertyProtected('nonetype')
    reverse = LazyPropertyProtected('reverse')

    def __init__(self, class_instance_trakt_api, item_type=None, sort_by=None, sort_how=None, item_keys=None, tmdb_id=None):
        self._class_instance_trakt_api = class_instance_trakt_api
        self._sort_by, self._sort_how = sort_by, sort_how
        self._item_keys = item_keys or ()
        self._item_type = item_type
        self._tmdb_id = tmdb_id

    @property
    def trakt_syncdata(self):
        return self._class_instance_trakt_api.trakt_syncdata

    @property
    def sort_by(self):
        return self._sort_by

    @property
    def sort_how(self):
        return self._sort_how

    @property
    def tmdb_id(self):
        return self._tmdb_id

    @property
    def detailed_item(self):
        if self._item_type != 'episode':
            return False
        if self.sort_by not in ('airdate', 'todays', 'lastweek', ):
            return False
        return True

    @property
    def item_types(self):
        if self._item_type == 'both':
            return ('movie', 'show', )
        return (self._item_type, )

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
            return (self.sort_method[0], *self._item_keys)
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

    def make_detailed_item(self, i, item_type='show'):
        if not i['id']:
            return i
        slug = self._class_instance_trakt_api.get_id(unique_id=i['id'], id_type='tmdb', trakt_type=item_type, output_type='slug')
        if not slug:
            return i
        item = self._class_instance_trakt_api.get_details(item_type, slug, season=i.get('season'), episode=i.get('episode'))
        if not item:
            return i
        item.pop('ids', None)
        item.update(i)
        return item

    def sort_data(self, data, sd, argx_offset=1):
        if self.sort_by == 'random':
            import random
            random.shuffle(data)
            return data
        if not self.additional_keys:
            return data
        argx = sd.keys.index(self.sort_key) + argx_offset
        return sorted(data, key=lambda x: x[argx] if x[argx] is not None else self.nonetype, reverse=self.reverse)

    def make_list(self, sd_func):
        data = []
        for item_type in self.item_types:
            sd = sd_func(item_type)
            sd.additional_keys = self.additional_keys
            data += [(item_type, *i, ) for i in sd.items] if sd.items else []

        if not data:
            return

        argx = sd.keys.index(sd.clause_keys[0]) + 1  # item_type pushed to front so offset argx positions by 1
        data = sorted(data, key=lambda x: x[argx], reverse=True)

        # Store argx positions for keys in dict for quick access
        argx_dictionary = self.make_argx_dictionary(sd)
        return [self.make_item(i, argx_dictionary) for i in self.sort_data(data, sd) if i]

    def make_item(self, i, argx_dictionary, detailed_item=False):
        item = {'id': i[argx_dictionary['tmdb_id']], 'mediatype': i[argx_dictionary['mediatype']], 'title': i[argx_dictionary['title']]}
        if i[argx_dictionary['mediatype']] in ('season', 'episode', ):
            item['season'] = i[argx_dictionary['season_number']]
        if i[argx_dictionary['mediatype']] == 'episode':
            item['episode'] = i[argx_dictionary['episode_number']]
        for k in (self._item_keys or ()):
            item.setdefault('infoproperties', {})[k] = i[argx_dictionary[k]]
        if detailed_item:
            item = self.make_detailed_item(item)
        return item

    @staticmethod
    def make_argx_dictionary(sd, additional_key_index=('mediatype', )):
        offset = len(additional_key_index) if additional_key_index else 0
        argx_dictionary = {k: (sd.keys.index(k) + offset) for k in sd.keys}
        for x, k in enumerate(additional_key_index):
            argx_dictionary[k] = x
        return argx_dictionary

    def get_argx_dictionary(self):
        return self.make_argx_dictionary(self.syncdata_getter)


class ItemListSyncDataCollection(ItemListSyncData):
    """ Items in collection """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_collected_getter)


class ItemListSyncDataWatchlist(ItemListSyncData):
    """ Items on watchlist """

    def get_items(self):
        return self.make_list(self.trakt_syncdata.get_all_watchlist_getter)


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


class ItemListSyncDataToWatch(ItemListSyncData):
    """ Mix of watchlist and inprogress items """

    def get_syncdata_getter(self):
        if self._item_type == 'movie':
            sd = self.trakt_syncdata.get_all_unhidden_movies_towatch_getter()
        else:
            sd = self.trakt_syncdata.get_all_unhidden_shows_towatch_getter()
        sd.additional_keys = ('last_watched_at', *self._item_keys, )
        return sd

    def get_presorted_items(self):
        sort_x1 = self.syncdata_getter.keys.index('watchlist_listed_at')
        sort_x2 = self.syncdata_getter.keys.index('last_watched_at')
        return sorted(self.syncdata_getter.items, key=lambda x: x[sort_x1] or x[sort_x2], reverse=True)

    def get_items(self):
        data = [(self._item_type, *i, ) for i in self.presorted_items]
        return [self.make_item(i, self.argx_dictionary) for i in self.sort_data(data, self.syncdata_getter) if i]


class ItemListSyncDataInProgress(ItemListSyncData):
    """ Partially watched shows that are inprogress """

    def get_syncdata_getter(self):
        sd = self.trakt_syncdata.get_all_unhidden_shows_inprogress_getter()
        sd.additional_keys = self.additional_keys
        return sd

    def get_presorted_items(self):
        sort_x = self.syncdata_getter.keys.index('last_watched_at')
        return sorted(self.syncdata_getter.items, key=lambda x: x[sort_x], reverse=True)

    def get_items(self):
        data = [('show', *i, ) for i in self.presorted_items]
        return [self.make_item(i, self.argx_dictionary) for i in self.sort_data(data, self.syncdata_getter) if i]


class ItemListSyncDataNextUp(ItemListSyncData):
    """ Episodes next up to watch for all inprogress shows """

    additional_key_index = ('mediatype', 'season_number', 'episode_number',)

    def get_syncdata_getter(self):
        sd = self.trakt_syncdata.get_all_unhidden_shows_nextepisode_getter()
        sd.additional_keys = self.additional_keys
        return sd

    def get_argx_dictionary(self):
        return self.make_argx_dictionary(self.syncdata_getter, additional_key_index=self.additional_key_index)

    def get_presorted_items(self):
        # configure items
        episode_id_x = self.syncdata_getter.keys.index('next_episode_id')
        data = [('episode', i[episode_id_x].split('.')[2], i[episode_id_x].split('.')[3], *i, ) for i in self.syncdata_getter.items]
        data = [i for i in self.sort_data(data, self.syncdata_getter, argx_offset=len(self.additional_key_index)) if i]
        with ParallelThread(data, self.make_item, self.argx_dictionary, detailed_item=self.detailed_item) as pt:
            item_queue = pt.queue
        return [i for i in item_queue if i]

    def get_special_sort(self):
        from tmdbhelper.lib.addon.tmdate import is_future_timestamp
        days = -1 if self.sort_by == 'todays' else -7
        recent, remainder = [], []
        for i in self.presorted_items:
            first_aired = i.get('first_aired')
            if first_aired and is_future_timestamp(first_aired, "%Y-%m-%d", 10, use_today=True, days=days):
                recent.append(i)
                continue
            remainder.append(i)
        return sorted(recent, key=lambda x: x['first_aired'], reverse=True) + remainder

    def get_items(self):
        if self.sort_by == 'airdate':
            return sorted(self.presorted_items, key=lambda x: x.get('first_aired') or '0', reverse=True)
        if self.sort_by in ('todays', 'lastweek', ):
            return self.get_special_sort()
        return self.presorted_items


class ItemListSyncDataUpNext(ItemListSyncData):
    """ Episodes Up Next for specific tmdb_id show """

    additional_key_index = ('mediatype', 'season_number', 'episode_number',)

    def get_syncdata_getter(self):
        sd = self.trakt_syncdata.get_unhidden_show_episodes_upnext(self.tmdb_id)
        sd.additional_keys = self.additional_keys
        return sd

    def get_argx_dictionary(self):
        return self.make_argx_dictionary(self.syncdata_getter, additional_key_index=self.additional_key_index)

    def get_presorted_items(self):
        episode_id_x = self.syncdata_getter.keys.index('upnext_episode_id')
        return [('episode', i[episode_id_x].split('.')[2], i[episode_id_x].split('.')[3], *i, ) for i in self.syncdata_getter.items]

    def get_items(self):
        data = self.sort_data(self.presorted_items, self.syncdata_getter, argx_offset=len(self.additional_key_index))
        return [self.make_item(i, self.argx_dictionary) for i in data if i]


def ItemListSyncDataFactory(sync_type, *args, **kwargs):

    routes = {
        'collection': ItemListSyncDataCollection,
        'watchlist': ItemListSyncDataWatchlist,
        'watched': ItemListSyncDataWatched,
        'playback': ItemListSyncDataPlayback,
        'favorites': ItemListSyncDataFavorites,
        'nextup': ItemListSyncDataNextUp,
        'upnext': ItemListSyncDataUpNext,
        'inprogress': ItemListSyncDataInProgress,
        'towatch': ItemListSyncDataToWatch
    }

    return routes[sync_type](*args, **kwargs)
