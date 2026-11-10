from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.datasync import SyncDataFactory


class SyncStatsFeature:
    item_types = {'movies': 'movie', 'shows': 'show', 'episodes': 'episode'}

    def __init__(self, syncdata):
        self.syncdata = syncdata

    def get_getter(self, item_type):
        raise NotImplementedError

    @cached_property
    def getters(self):
        return self.get_getters()

    def get_getters(self):
        return {name: self.get_getter(item_type) for name, item_type in self.item_types.items()}

    @cached_property
    def sync_succeeded(self):
        return self.get_sync_succeeded()

    def get_sync_succeeded(self):
        return all([getter.sync_succeeded for getter in self.getters.values()])

    @cached_property
    def counts(self):
        return self.get_counts()

    def get_counts(self):
        return {name: getter.items[0]['item_count'] for name, getter in self.getters.items()}

    @cached_property
    def total(self):
        return self.get_total()

    def get_total(self):
        return self.counts['movies'] + self.counts['episodes']

    @cached_property
    def properties(self):
        return self.get_properties()

    def get_properties(self):
        return {**self.counts, 'total': self.total}

    def get_property_name(self, item_type):
        return f'SyncStats.{item_type}.{self.statistic}'

    def clear(self):
        for item_type in (*self.item_types, 'total'):
            self.syncdata.window.get_property(self.get_property_name(item_type), clear_property=True)

    def update(self):
        if self.syncdata.get_sync_provider(self.sync_type) is None:
            if not self.syncdata.is_sync_provider_unavailable(self.sync_type):
                self.clear()
            return
        if not self.sync_succeeded:
            return  # Retain the published stats until all prerequisites are current.
        for item_type, value in self.properties.items():
            self.syncdata.window.get_property(self.get_property_name(item_type), set_property=str(value))


class SyncStatsWatched(SyncStatsFeature):
    statistic = 'watched'
    sync_type = 'SyncWatched'
    sync_types = ('SyncWatched', 'SyncAiredEpisodes')

    def get_getter(self, item_type):
        return self.syncdata.get_watched_stats_getter(item_type)


class SyncStatsCollected(SyncStatsFeature):
    statistic = 'collected'
    sync_type = 'SyncCollection'
    sync_types = ('SyncCollection', )

    def get_getter(self, item_type):
        return self.syncdata.get_collected_stats_getter(item_type)


class SyncStats:
    """Publish fresh counts using a new set of getters for each update."""

    stats_classes = {'watched': SyncStatsWatched, 'collection': SyncStatsCollected}

    def __init__(self, syncdata=None):
        self.syncdata = syncdata if syncdata is not None else SyncDataFactory()

    def update(self, features=('watched', 'collection')):
        for feature in self.stats_classes.keys() & set(features):
            self.stats_classes[feature](self.syncdata).update()

    def clear(self, features=('watched', 'collection')):
        for feature in self.stats_classes.keys() & set(features):
            self.stats_classes[feature](self.syncdata).clear()

    def update_sync_types(self, sync_types):
        sync_types = set(sync_types)
        self.update(
            feature
            for feature, stats_class in self.stats_classes.items()
            if sync_types.intersection(stats_class.sync_types)
        )
