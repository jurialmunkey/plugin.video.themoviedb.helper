from jurialmunkey.ftools import cached_property


class StatsSupplier:
    def __init__(self, provider):
        self.provider = provider

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        raise NotImplementedError


class Stats:
    def __init__(self, registry=None):
        self._registry = registry

    @cached_property
    def registry(self):
        return self.get_registry()

    def get_registry(self):
        from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
        return self._registry if self._registry is not None else SyncProviderRegistry()

    @cached_property
    def provider(self):
        return self.get_provider()

    def get_provider(self):
        return self.registry.get_selected_provider('stats')

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        if self.provider is None or not self.provider.is_authorized():
            return
        return self.provider.stats_class(self.provider).items


class StatsInvalidator:
    notification = False
    localized_id = 32598

    def invalidate(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        from tmdbhelper.lib.script.stats import StatsProperties
        stats = FindQueriesDatabase().invalidate_stats()
        StatsProperties(stats).clear()

    def run(self, sync=False):
        self.invalidate()
        if sync:
            from tmdbhelper.lib.script.stats import get_stats
            get_stats(forced=True)
