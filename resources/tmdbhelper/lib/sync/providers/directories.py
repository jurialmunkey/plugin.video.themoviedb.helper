from jurialmunkey.modimp import importmodule
from tmdbhelper.lib.sync.providers.catalog import PROVIDERS
from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry


def get_provider_list_container(info, provider_id=None, prompt=True):
    registry = SyncProviderRegistry()
    container = registry.get_list_container(info, provider_id)
    if container is not None:
        return container
    candidates = (
        addon_id for addon_id, entry in PROVIDERS.items()
        if 'lists' in entry['capabilities']
        and (entry['provider_id'] == provider_id if provider_id is not None
             else info.startswith(f"{entry['provider_id']}_"))
    )
    addon_id = next(candidates, None)
    if not prompt or addon_id is None:
        return
    from tmdbhelper.lib.script.sync.provider_directory import SyncProviderDirectorySetup
    provider = SyncProviderDirectorySetup(addon_id, info).ensure_provider()
    if provider is None:
        return
    try:
        route = provider.list_routes[info]
    except KeyError:
        raise ValueError(f'info={info} is not a valid route in {provider.display_name}') from None
    return importmodule(**route)
