from tmdbhelper.lib.sync.providers.features import ACTION_FEATURES, SYNC_FEATURES


class SyncProvider:
    interface_version = None
    provider_id = None
    display_name = None
    sync_classes = {}
    action_classes = {}
    service_sync_classes = {}
    service_action_classes = {}
    getter_classes = {}
    ratings_classes = {}
    imdb_top250_classes = {}
    stats_class = None
    monitor_lists_class = None
    scrobbler_class = None
    directory_item_class = None
    list_routes = {}

    @property
    def capabilities(self):
        features = {SYNC_FEATURES[name] for name in self.sync_classes}
        features.update(ACTION_FEATURES[name] for name in self.action_classes)
        if self.service_sync_classes:
            features.add('service_sync')
        if self.scrobbler_class is not None:
            features.add('scrobbling')
        if self.list_routes:
            features.add('lists')
        if self.ratings_classes:
            features.add('ratings')
        if self.imdb_top250_classes:
            features.add('imdb_top250')
        if self.stats_class is not None:
            features.add('stats')
        if self.monitor_lists_class is not None:
            features.add('monitor_lists')
        if self.service_action_classes:
            features.add('service_actions')
        return tuple(sorted(features))

    def get_sync_class(self, sync_type):
        return self.sync_classes.get(sync_type) or self.service_sync_classes.get(sync_type)

    def is_authorized(self):
        raise NotImplementedError

    def migrate_settings(self):
        """Migrate provider settings before constructing any API clients."""
        pass

    def get_last_activities(self):
        raise NotImplementedError
