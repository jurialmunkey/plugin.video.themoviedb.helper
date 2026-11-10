class ListActions:
    def __init__(self, provider):
        self.provider = provider

    def like_list(self, list_slug, user_slug='me', delete=False):
        raise NotImplementedError

    def rename_list(self, list_slug):
        raise NotImplementedError

    def delete_list(self, list_slug):
        raise NotImplementedError


def get_provider_list_actions(provider_id, registry=None):
    from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
    registry = registry if registry is not None else SyncProviderRegistry()
    provider = registry.find_provider(provider_id)
    if provider is None or provider.list_actions_class is None:
        return
    if not provider.is_authorized():
        return
    return provider.list_actions_class(provider)
