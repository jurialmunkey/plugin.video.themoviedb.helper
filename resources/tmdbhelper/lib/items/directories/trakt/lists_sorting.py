from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.api.mapping import get_empty_item


def get_sort_methods(info=None):
    items = [
        {
            'name': f'{get_localized(32287)}: {get_localized(571)}',
            'params': {}},
        {
            'name': f'{get_localized(32287)}: {get_localized(32451)} {get_localized(32286)}',
            'params': {'sort_by': 'rank', 'sort_how': 'asc'},
            'allowlist': ('trakt_userlist', )},
        {
            'name': f'{get_localized(32287)}: {get_localized(32452)} {get_localized(32286)}',
            'params': {'sort_by': 'rank', 'sort_how': 'desc'},
            'allowlist': ('trakt_userlist', )},
        {
            'name': f'{get_localized(32287)}: {get_localized(32063)} {get_localized(584)}',
            'params': {'sort_by': 'added', 'sort_how': 'asc'},
            'allowlist': ('trakt_userlist', )},
        {
            'name': f'{get_localized(32287)}: {get_localized(32063)} {get_localized(585)}',
            'params': {'sort_by': 'added', 'sort_how': 'desc'},
            'allowlist': ('trakt_userlist', )},
        {
            'name': f'{get_localized(32287)}: {get_localized(32473)} {get_localized(584)}',
            'params': {'sort_by': 'collected', 'sort_how': 'asc'},
            'allowlist': ('trakt_collection', 'trakt_userlist')},
        {
            'name': f'{get_localized(32287)}: {get_localized(32473)} {get_localized(585)}',
            'params': {'sort_by': 'collected', 'sort_how': 'desc'},
            'allowlist': ('trakt_collection', 'trakt_userlist')},
        {
            'name': f'{get_localized(32287)}: {get_localized(369)} (A-Z)',
            'params': {'sort_by': 'title', 'sort_how': 'asc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(369)} (Z-A)',
            'params': {'sort_by': 'title', 'sort_how': 'desc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(563)} {get_localized(584)}',
            'params': {'sort_by': 'percentage', 'sort_how': 'asc'},
            'allowlist': ('trakt_userlist', )},
        {
            'name': f'{get_localized(32287)}: {get_localized(563)} {get_localized(585)}',
            'params': {'sort_by': 'percentage', 'sort_how': 'desc'},
            'allowlist': ('trakt_userlist', )},
        {
            'name': f'{get_localized(32287)}: {get_localized(345)} {get_localized(584)}',
            'params': {'sort_by': 'year', 'sort_how': 'asc'},
            'blocklist': ('trakt_userlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(345)} {get_localized(585)}',
            'params': {'sort_by': 'year', 'sort_how': 'desc'},
            'blocklist': ('trakt_userlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32453).capitalize()}',
            'params': {'sort_by': 'plays', 'sort_how': 'asc'},
            'allowlist': ('trakt_inprogress',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32205)}',
            'params': {'sort_by': 'plays', 'sort_how': 'desc'},
            'allowlist': ('trakt_inprogress',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32242)} {get_localized(584)}',
            'params': {'sort_by': 'released', 'sort_how': 'asc'},
            'allowlist': ('trakt_userlist', 'trakt_inprogress', 'trakt_watchlist', 'trakt_watchlist_released', 'trakt_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32242)} {get_localized(585)}',
            'params': {'sort_by': 'released', 'sort_how': 'desc'},
            'allowlist': ('trakt_userlist', 'trakt_inprogress', 'trakt_watchlist', 'trakt_watchlist_released', 'trakt_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(2050)} {get_localized(584)}',
            'params': {'sort_by': 'runtime', 'sort_how': 'asc'},
            'allowlist': ('trakt_userlist', 'trakt_inprogress', 'trakt_watchlist', 'trakt_watchlist_released', 'trakt_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(2050)} {get_localized(585)}',
            'params': {'sort_by': 'runtime', 'sort_how': 'desc'},
            'allowlist': ('trakt_userlist', 'trakt_inprogress', 'trakt_watchlist', 'trakt_watchlist_released', 'trakt_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(205)} {get_localized(584)}',
            'params': {'sort_by': 'votes', 'sort_how': 'asc'},
            'allowlist': ('trakt_userlist', 'trakt_inprogress', 'trakt_watchlist', 'trakt_watchlist_released', 'trakt_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(205)} {get_localized(585)}',
            'params': {'sort_by': 'votes', 'sort_how': 'desc'},
            'allowlist': ('trakt_userlist', 'trakt_inprogress', 'trakt_watchlist', 'trakt_watchlist_released', 'trakt_watchlist_anticipated',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32175)} {get_localized(584)}',
            'params': {'sort_by': 'popularity', 'sort_how': 'asc'},
            'allowlist': ('trakt_userlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32175)} {get_localized(585)}',
            'params': {'sort_by': 'popularity', 'sort_how': 'desc'},
            'allowlist': ('trakt_userlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(16102)} {get_localized(584)}',
            'params': {'sort_by': 'watched', 'sort_how': 'asc'},
            'allowlist': ('trakt_userlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(16102)} {get_localized(585)}',
            'params': {'sort_by': 'watched', 'sort_how': 'desc'},
            'allowlist': ('trakt_userlist',)},
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


class ListTraktSortBy(ContainerDirectory):
    def get_items(self, info, parent_info=None, **kwargs):
        items = [get_sort_directory_item(i, info=parent_info, **kwargs) for i in get_sort_methods(parent_info)]
        return items
