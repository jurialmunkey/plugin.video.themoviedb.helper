def select_sort_list(sort_methods, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.plugin import executebuiltin, format_folderpath, encode_url
    x = Dialog().contextmenu([i['name'] for i in sort_methods])
    if x == -1:
        return
    for k, v in sort_methods[x]['params'].items():
        kwargs[k] = v
    executebuiltin(format_folderpath(encode_url(**kwargs)))
