from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.api.mapping import get_empty_item


def get_sort_methods_asc_desc(sort_by, localized_name):
    return [
        {
            'name': f'{localized_name}: {get_localized(584)}',
            'params': {'sort_by': sort_by, 'sort_how': 'asc'}
        },
        {
            'name': f'{localized_name}: {get_localized(585)}',
            'params': {'sort_by': sort_by, 'sort_how': 'desc'}
        },
    ]


def get_sort_methods(info=None):
    items = [
        {
            'name': f'{get_localized(32287)}: {get_localized(571)}',
            'params': {}
        },
    ]
    items += get_sort_methods_asc_desc('rank', get_localized(32286))
    items += get_sort_methods_asc_desc('score', get_localized(32072))
    items += get_sort_methods_asc_desc('usort', get_localized(32079))
    items += get_sort_methods_asc_desc('score_average', get_localized(563))
    items += get_sort_methods_asc_desc('released', get_localized(172))
    items += get_sort_methods_asc_desc('releasedigital', f'{get_localized(172)} ({get_localized(32245)})')
    items += get_sort_methods_asc_desc('imdbrating', f'IMDb {get_localized(563)}')
    items += get_sort_methods_asc_desc('imdbvotes', f'IMDb {get_localized(205)}')
    items += get_sort_methods_asc_desc('last_air_date', get_localized(32069))
    items += get_sort_methods_asc_desc('imdbpopular', f'IMDb {get_localized(32175)}')
    items += get_sort_methods_asc_desc('tmdbpopular', f'TMDb {get_localized(32175)}')
    items += get_sort_methods_asc_desc('rogerebert', 'Roger Ebert')
    items += get_sort_methods_asc_desc('rtomatoes', 'Rotten Tomatoes')
    items += get_sort_methods_asc_desc('rtaudience', 'Rotten Tomatoes Audience')
    items += get_sort_methods_asc_desc('metacritic', f'Metacritic {get_localized(563)}')
    items += get_sort_methods_asc_desc('myanimelist', f'MyAnimeList {get_localized(563)}')
    items += get_sort_methods_asc_desc('letterrating', f'Letterboxd {get_localized(563)}')
    items += get_sort_methods_asc_desc('lettervotes', f'Letterboxd {get_localized(205)}')
    items += get_sort_methods_asc_desc('budget', get_localized(32067))
    items += get_sort_methods_asc_desc('revenue', get_localized(32068))
    items += get_sort_methods_asc_desc('runtime', get_localized(180))
    items += get_sort_methods_asc_desc('title', get_localized(369))
    items += get_sort_methods_asc_desc('added', get_localized(32063))
    items += get_sort_methods_asc_desc('random', get_localized(590))

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


class ListMDbListSortBy(ContainerDirectory):
    def get_items(self, info, parent_info=None, **kwargs):
        items = [get_sort_directory_item(i, info=parent_info, **kwargs) for i in get_sort_methods(parent_info)]
        return items
