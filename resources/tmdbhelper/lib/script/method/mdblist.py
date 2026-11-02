from tmdbhelper.lib.script.method.lists import select_sort_list


def sort_mdblist(**kwargs):
    from tmdbhelper.lib.sync.providers.directories import get_provider_list_container
    container = get_provider_list_container('mdblist_sortby', 'mdblist')
    if container is None:
        return
    sort_methods = container.get_sort_methods(kwargs['info'])
    return select_sort_list(sort_methods, **kwargs)
