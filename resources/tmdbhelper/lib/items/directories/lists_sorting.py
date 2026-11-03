from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.api.mapping import get_empty_item


def get_sort_methods(info=None):
    info = {
        'trakt_collection': 'sync_collection',
        'trakt_inprogress': 'sync_inprogress',
        'trakt_watchlist': 'sync_watchlist',
        'trakt_watchlist_released': 'sync_watchlist_released',
        'trakt_watchlist_anticipated': 'sync_watchlist_anticipated',
    }.get(info, info)
    from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
    registry = SyncProviderRegistry()
    for provider in registry.providers.values():
        if info in provider.list_routes:
            container = registry.get_list_container(f'{provider.provider_id}_sortby', provider.provider_id)
            if container is not None:
                return container.get_sort_methods(info)
    items = [
        {
            'name': f'{get_localized(32287)}: {get_localized(571)}',
            'params': {}},
        {
            'name': f'{get_localized(32287)}: {get_localized(32473)} {get_localized(584)}',
            'params': {'sort_by': 'collected', 'sort_how': 'asc'},
            'allowlist': ('sync_collection',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32473)} {get_localized(585)}',
            'params': {'sort_by': 'collected', 'sort_how': 'desc'},
            'allowlist': ('sync_collection',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(369)} (A-Z)',
            'params': {'sort_by': 'title', 'sort_how': 'asc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(369)} (Z-A)',
            'params': {'sort_by': 'title', 'sort_how': 'desc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(345)} {get_localized(584)}',
            'params': {'sort_by': 'year', 'sort_how': 'asc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(345)} {get_localized(585)}',
            'params': {'sort_by': 'year', 'sort_how': 'desc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(32453).capitalize()}',
            'params': {'sort_by': 'plays', 'sort_how': 'asc'},
            'allowlist': ('sync_inprogress',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32205)}',
            'params': {'sort_by': 'plays', 'sort_how': 'desc'},
            'allowlist': ('sync_inprogress',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32242)} {get_localized(584)}',
            'params': {'sort_by': 'released', 'sort_how': 'asc'},
            'allowlist': ('sync_inprogress', 'sync_watchlist', 'sync_watchlist_released', 'sync_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32242)} {get_localized(585)}',
            'params': {'sort_by': 'released', 'sort_how': 'desc'},
            'allowlist': ('sync_inprogress', 'sync_watchlist', 'sync_watchlist_released', 'sync_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(2050)} {get_localized(584)}',
            'params': {'sort_by': 'runtime', 'sort_how': 'asc'},
            'allowlist': ('sync_inprogress', 'sync_watchlist', 'sync_watchlist_released', 'sync_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(2050)} {get_localized(585)}',
            'params': {'sort_by': 'runtime', 'sort_how': 'desc'},
            'allowlist': ('sync_inprogress', 'sync_watchlist', 'sync_watchlist_released', 'sync_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(205)} {get_localized(584)}',
            'params': {'sort_by': 'votes', 'sort_how': 'asc'},
            'allowlist': ('sync_inprogress', 'sync_watchlist', 'sync_watchlist_released', 'sync_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(205)} {get_localized(585)}',
            'params': {'sort_by': 'votes', 'sort_how': 'desc'},
            'allowlist': ('sync_inprogress', 'sync_watchlist', 'sync_watchlist_released', 'sync_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(590)}',
            'params': {'sort_by': 'random'}}]

    return [
        i for i in items
        if (
            ('allowlist' not in i or info in i['allowlist'])
            and ('blocklist' not in i or info not in i['blocklist'])
        )]


def get_sort_directory_item(i, **params):
    item = get_empty_item()
    item['label'] = f'{params.get("list_name")} - {i["name"]}'
    item['params'] = params
    item['params'].update(i['params'])
    return item


class ListSortBy(ContainerDirectory):
    def get_items(self, info, parent_info=None, **kwargs):
        items = [get_sort_directory_item(i, info=parent_info, **kwargs) for i in get_sort_methods(parent_info)]
        return items
