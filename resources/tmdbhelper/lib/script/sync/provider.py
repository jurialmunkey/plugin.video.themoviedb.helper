from tmdbhelper.lib.script.sync.request import ItemSync as RequestItemSync


class ItemSync(RequestItemSync):
    sync_types = ()
    show_sync_types = ()

    def get_sync_dependencies(self):
        dependencies = tuple((name, self.item_type) for name in self.sync_types)
        if self.base_item_type == 'show':
            dependencies += tuple((name, 'show') for name in self.show_sync_types)
        return dependencies

    def get_sync_invalidator(self):
        from tmdbhelper.lib.sync.action_invalidator import SyncActionInvalidator
        return SyncActionInvalidator(
            self.syncdata, self.sync_provider, self.get_sync_dependencies())

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.get_sync_invalidator().run()

    def get_sync_value(self):
        return self.syncdata.get_value(
            self.tmdb_type, self.tmdb_id, self.season, self.episode, self.sync_key)

    def sync(self):
        self.reset_lastactivities()
        super().sync()
