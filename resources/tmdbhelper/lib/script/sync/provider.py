from tmdbhelper.lib.script.sync.request import ItemSync as RequestItemSync


class ItemSync(RequestItemSync):
    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        from tmdbhelper.lib.sync.invalidator import SyncInvalidatorAll
        invalidator = SyncInvalidatorAll()
        invalidator.syncdata = self.syncdata
        invalidator.features = (self.sync_feature,)
        invalidator.notification = False
        invalidator.run(sync=True)

    def get_sync_value(self):
        return self.syncdata.get_value(
            self.tmdb_type, self.tmdb_id, self.season, self.episode, self.sync_key)

    def sync(self):
        self.reset_lastactivities()
        super().sync()
