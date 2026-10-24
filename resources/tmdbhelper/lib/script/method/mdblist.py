from tmdbhelper.lib.script.method.lists import select_sort_list


def sort_mdblist(**kwargs):
    from tmdbhelper.lib.items.directories.mdblist.lists_sorting import get_sort_methods
    sort_methods = get_sort_methods(kwargs['info'])
    return select_sort_list(sort_methods, **kwargs)
