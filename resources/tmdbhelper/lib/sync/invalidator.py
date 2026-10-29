from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.sync.features import FEATURE_LABELS, SYNC_FEATURES
from tmdbhelper.lib.sync.datasync import SyncDataFactory
from tmdbhelper.lib.sync.activity import SyncLastActivities
from tmdbhelper.lib.sync.providers.stats import StatsInvalidator


class SyncInvalidatorAll:
    notification = True
    features = tuple(FEATURE_LABELS)
    localized_id = 593
    sync_table = {
        'plays': ('movie', 'show'),
        'aired_episodes': ('show',),
        'watched_episodes': ('show',),
        'reset_at': ('movie', 'show'),
        'last_watched_at': ('movie', 'show'),
        'last_updated_at': ('movie', 'show'),
        'rating': ('movie', 'show'),
        'rated_at': ('movie', 'show'),
        'favorites_rank': ('movie', 'show'),
        'favorites_listed_at': ('movie', 'show'),
        'favorites_notes': ('movie', 'show'),
        'watchlist_rank': ('movie', 'show', 'season', 'episode'),
        'watchlist_listed_at': ('movie', 'show', 'season', 'episode'),
        'watchlist_notes': ('movie', 'show', 'season', 'episode'),
        'collection_last_collected_at': ('movie', 'show', 'episode'),
        'collection_last_updated_at': ('movie', 'show', 'episode'),
        'playback_progress': ('movie', 'show'),
        'playback_paused_at': ('movie', 'show'),
        'playback_id': ('movie', 'show'),
        'progress_watched_hidden_at': ('movie', 'show'),
        'progress_collected_hidden_at': ('movie', 'show'),
        'calendar_hidden_at': ('movie', 'show'),
        'dropped_hidden_at': ('movie', 'show'),
        'next_episode_id': ('show',),
        'next_episode_aired_at': ('show',),
        'upnext_episode_id': ('show',),
    }

    @cached_property
    def syncdata(self):
        return SyncDataFactory()

    @cached_property
    def database_keys(self):
        return self.get_database_keys()

    def get_database_keys(self):
        return tuple(key for key, sync_type in self.syncdata.routes.items()
                     if sync_type and SYNC_FEATURES[sync_type] in self.features)

    @cached_property
    def providers(self):
        return self.get_providers()

    def get_providers(self):
        return tuple(
            provider for provider in self.syncdata.registry.providers.values()
            if any(SYNC_FEATURES[name] in self.features
                   for name in (*provider.sync_classes, *provider.service_sync_classes)))

    def invalidate_provider(self, provider):
        sync_classes = {**provider.sync_classes, **provider.service_sync_classes}
        methods = {
            sync_class.method for name, sync_class in sync_classes.items()
            if SYNC_FEATURES[name] in self.features}
        for method in methods:
            self.invalidate_method(provider.provider_id, method)
        SyncLastActivities(self.syncdata, provider).clear()
        for name, sync_class in provider.service_sync_classes.items():
            if SYNC_FEATURES[name] in self.features:
                sync_class.invalidate_cache(provider)

    def invalidate_method(self, provider_id, method):
        for item_type in ('movie', 'show', 'season', 'episode'):
            item_id = f'{item_type}.{provider_id}.{method}'
            self.syncdata.invalidate_activity(item_id)

    def invalidate(self, clear_data=True):
        if clear_data and self.database_keys:
            self.syncdata.cache.del_column_values(keys=self.database_keys)
        for provider in self.providers:
            self.invalidate_provider(provider)

    def sync(self):
        for item_type in ('movie', 'show', 'season', 'episode'):
            keys = tuple(key for key in self.database_keys if item_type in self.sync_table[key])
            self.syncdata.sync(item_type, keys)

    def run(self, sync=False):
        # Resync replaces columns after a successful response; keep them available until then.
        self.invalidate(clear_data=not sync)
        if sync:
            self.sync()
        if self.notification:
            Dialog().ok(get_localized(32549), get_localized(32146 if sync else 32027).format(get_localized(self.localized_id).lower()))


class SyncInvalidatorWatchedProgress(SyncInvalidatorAll):
    features = ('watched',)
    localized_id = 32408


class SyncInvalidatorCollection(SyncInvalidatorAll):
    features = ('collection',)
    localized_id = 32192


class SyncInvalidatorWatchlist(SyncInvalidatorAll):
    features = ('watchlist',)
    localized_id = 32193


class SyncInvalidatorFavorites(SyncInvalidatorAll):
    features = ('favorites',)
    localized_id = 1036


class SyncInvalidatorRatings(SyncInvalidatorAll):
    features = ('ratings',)
    localized_id = 563


def SyncInvalidator(datatype):
    routes = {'watched': SyncInvalidatorWatchedProgress, 'collection': SyncInvalidatorCollection,
              'watchlist': SyncInvalidatorWatchlist, 'favorites': SyncInvalidatorFavorites,
              'ratings': SyncInvalidatorRatings, 'stats': StatsInvalidator, 'all': SyncInvalidatorAll}
    try:
        selected = routes[datatype]
    except KeyError:
        choices = tuple(routes.values())
        index = Dialog().select(get_localized(32549), [get_localized(choice.localized_id) for choice in choices])
        if index == -1:
            return
        selected = choices[index]
    return selected()
