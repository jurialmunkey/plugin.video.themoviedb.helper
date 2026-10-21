from tmdbhelper.lib.script.sync.basic import get_sync_item


def ItemDropped(*args, **kwargs):
    return get_sync_item('ItemDropped', 'watched', *args, **kwargs)
