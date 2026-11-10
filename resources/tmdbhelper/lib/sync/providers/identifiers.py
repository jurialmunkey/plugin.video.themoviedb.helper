from jurialmunkey.ftools import cached_property


class IdentifierResolver:
    def __init__(self, provider):
        self.provider = provider

    def get_ids(self, tmdb_type, tmdb_id, season=None, episode=None):
        raise NotImplementedError

    def get_id(self, id_value, id_type, item_type, output_type, season=None, episode=None):
        """Optional single-ID lookup used by legacy provider entry points."""
        raise NotImplementedError


class IdentifierResolvers:
    def __init__(self, registry=None):
        self._registry = registry

    @cached_property
    def registry(self):
        return self.get_registry()

    def get_registry(self):
        if self._registry is not None:
            return self._registry
        from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
        return SyncProviderRegistry()

    def get_ids(self, tmdb_type, tmdb_id, season=None, episode=None):
        ids = {}
        for provider in self.registry.get_capable_providers('identifiers'):
            resolved = provider.identifier_resolver_class(provider).get_ids(tmdb_type, tmdb_id, season, episode)
            ids.update({key: value for key, value in resolved.items() if key not in ids and value not in (None, '')})
        return ids
