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
    route = None

    for routes in ALL_ROUTES:
        try:
            route = routes[info]['route']
            return importmodule(**route)
        except KeyError:
            continue

    if info and info[:4] != 'dir_':
        raise Exception(f'info={info} is not valid route')
    return importmodule(module_name='tmdbhelper.lib.items.directories.base.lists_base', import_attr='ListBaseDir')
