from jurialmunkey.modimp import importmodule
from tmdbhelper.lib.addon.consts import (
    ROUTE_NOID,
    ROUTE_TMDBID,
)

ALL_ROUTES = [
    ROUTE_NOID,
    ROUTE_TMDBID
]


def get_container(info):
    for routes in ALL_ROUTES:
        try:
            route = routes[info]
        except KeyError:
            continue
        if 'redirect' in route:
            return get_container(route['redirect'])
        return importmodule(**route['route'])

    if info and info[:4] != 'dir_':
        from tmdbhelper.lib.sync.providers.directories import get_provider_list_container
        container = get_provider_list_container(info)
        if container is not None:
            return container
        # A known, unavailable provider may have had its installation declined.
        from tmdbhelper.lib.sync.providers.catalog import PROVIDERS
        if any('lists' in entry['capabilities'] and info.startswith(f"{entry['provider_id']}_")
               for entry in PROVIDERS.values()):
            return importmodule(module_name='tmdbhelper.lib.items.container', import_attr='ContainerDirectory')
        raise Exception(f'info={info} is not valid route')
    return importmodule(module_name='tmdbhelper.lib.items.directories.base.lists_base', import_attr='ListBaseDir')
