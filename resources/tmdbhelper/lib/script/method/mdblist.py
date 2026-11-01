from tmdbhelper.lib.script.method.lists import select_sort_list
from tmdbhelper.lib.script.method.decorators import is_in_kwargs


@is_in_kwargs({'like_mdblist': True})
def like_mdblist(like_mdblist=None, delete=False, **kwargs):
    from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
    from tmdbhelper.lib.addon.plugin import get_localized
    from xbmcgui import Dialog

    provider = SyncProviderRegistry().find_provider('mdblist')
    if provider is None:
        return
    api = provider.api
    if api is None:
        Dialog().ok(get_localized(32315), f'{get_localized(32516)}\n{get_localized(32517)}')
        return

    response = api.like_list(like_mdblist, delete=delete)
    successful = response is not None and response.status_code == 200
    affix = get_localized(32320 if delete else 32321)
    message = get_localized(32316 if successful else 32317).format(affix)
    if not successful and response is not None:
        message = f'{message}\n{get_localized(32318).format(response.status_code)}'
    Dialog().ok(get_localized(32319 if delete else 32315), message)
    if successful:
        from tmdbhelper.lib.script.method.kodi_utils import container_refresh
        container_refresh()


def sort_mdblist(**kwargs):
    from tmdbhelper.lib.sync.providers.directories import get_provider_list_container
    container = get_provider_list_container('mdblist_sortby', 'mdblist')
    if container is None:
        return
    sort_methods = container.get_sort_methods(kwargs['info'])
    return select_sort_list(sort_methods, **kwargs)
