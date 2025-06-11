from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.api.mapping import get_empty_item


def get_year_directory_item(x, tmdb_type):
    item = get_empty_item()
    item['label'] = f'{x}'
    item['params'] = {
        'info': 'trakt_popular',
        'tmdb_type': tmdb_type,
        'years': f'{x}'
    }
    return item


class ListTraktYears(ContainerDirectory):
    def get_items(self, tmdb_type, **kwargs):
        from tmdbhelper.lib.addon.tmdate import get_datetime_today
        return [
            get_year_directory_item(x, tmdb_type)
            for x in reversed(range(1900, int(get_datetime_today().strftime("%Y")) + 1))
        ]
