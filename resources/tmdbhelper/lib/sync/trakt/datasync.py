from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.mixins import SyncDataParentProperties
from tmdbhelper.lib.sync.trakt.activity import TraktLastActivities
from tmdbhelper.lib.sync.trakt.features import SYNC_FEATURES
from tmdbhelper.lib.sync.trakt.synctype import SyncRatings, SyncFavorites


class TraktSyncData(SyncDataParentProperties):
    sync_classes = {'SyncRatings': SyncRatings, 'SyncFavorites': SyncFavorites}

    @cached_property
    def api(self):
        return self.get_api()

    def get_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    def get_sync_class(self, sync_type):
        if self.api.authenticator.is_authorized:
            return self.sync_classes[sync_type]

    def create_sync(self, sync_type, item_type):
        sync_class = self.get_sync_class(sync_type)
        if sync_class is not None:
            return sync_class(self.instance_syncdata, item_type)

    def clear_activities(self, sync_types):
        for sync_type in sync_types:
            self.clear_method(self.sync_classes[sync_type].method)
        TraktLastActivities(self.instance_syncdata).clear()

    def clear_method(self, method):
        for item_type in ('movie', 'show', 'season', 'episode'):
            item_id = f'{item_type}.trakt.{method}'
            self.cache.del_item(table='lactivities', item_id=item_id)
            self.window.get_property(f'syncdecorators.timerlock.sync_data.{item_id}', clear_property=True)

    def invalidate(self, features):
        sync_types = tuple(name for name, feature in SYNC_FEATURES.items() if feature in features)
        if sync_types:
            self.clear_activities(sync_types)
