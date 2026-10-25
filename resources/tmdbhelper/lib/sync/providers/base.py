from tmdbhelper.lib.sync.providers.features import ACTION_FEATURES, SYNC_FEATURES


class SyncProvider:
    interface_version = None
    provider_id = None
    display_name = None
    sync_classes = {}
    action_classes = {}
    getter_classes = {}
    scrobbler_class = None

    @property
    def capabilities(self):
        features = {SYNC_FEATURES[name] for name in self.sync_classes}
        features.update(ACTION_FEATURES[name] for name in self.action_classes)
        if self.scrobbler_class is not None:
            features.add('scrobbling')
        return tuple(sorted(features))

    def get_sync_class(self, sync_type):
        return self.sync_classes.get(sync_type)

    def is_authorized(self):
        raise NotImplementedError

    def get_last_activities(self):
        raise NotImplementedError
