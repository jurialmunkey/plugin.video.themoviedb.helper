from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.script.actions.trakt.item import ItemAction
from tmdbhelper.lib.sync.datasync import SyncDataFactory
from tmdbhelper.lib.sync.invalidator import SyncInvalidatorFavorites


class ItemFavorites(ItemAction):
    localized_name_add = 32490
    localized_name_rem = 32491
    sync_key = 'favorites_listed_at'
    sync_url = 'favorites'

    @cached_property
    def syncdata(self):
        return self.get_syncdata()

    def get_syncdata(self):
        syncdata = SyncDataFactory()
        syncdata.core_sync.api = self.trakt_api
        return syncdata

    def get_sync_value(self):
        return self.syncdata.get_value(self.tmdb_type, self.tmdb_id, key=self.sync_key)

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        invalidator = SyncInvalidatorFavorites()
        invalidator.syncdata = self.syncdata
        invalidator.notification = False
        invalidator.run(sync=True)

    def sync(self):
        self.reset_lastactivities()
        super().sync()
