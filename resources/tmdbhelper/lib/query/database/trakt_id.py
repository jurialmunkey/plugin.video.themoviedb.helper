class FindQueriesDatabaseTraktID:
    """Temporary entry point for provider modules using the former core lookup."""

    def get_trakt_id(self, id_value, id_type='tmdb', item_type=None, output_type='slug', season=None, episode=None):
        from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
        from tmdbhelper.lib.script.sync.provider_errors import SyncProviderIdentifierErrorDialog
        provider = SyncProviderRegistry().find_provider('trakt')
        if provider is None:
            return
        dialog = SyncProviderIdentifierErrorDialog(provider.addon_id)
        if provider.identifier_resolver_class is None:
            dialog.show()
            return
        dialog.clear()
        return provider.identifier_resolver_class(provider).get_id(
            id_value, id_type, item_type, output_type, season, episode)
