from tmdbhelper.lib.addon.plugin import get_setting


def ItemDropped(*args, **kwargs):
    if get_setting('sync_source_watched', 'str') == 'MDbList':
        from tmdbhelper.lib.script.sync.mdblist.basic import ItemDropped
    else:
        from tmdbhelper.lib.script.sync.trakt.basic import ItemDropped
    return ItemDropped(*args, **kwargs)
