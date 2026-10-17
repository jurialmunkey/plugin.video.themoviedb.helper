from jurialmunkey.modimp import importmodule
from tmdbhelper.lib.addon.plugin import get_setting


def get_sync_item(item_class, source, *args, module='basic', **kwargs):
    provider = 'mdblist' if get_setting(f'sync_source_{source}', 'str') == 'MDbList' else 'trakt'
    item_class = importmodule(f'tmdbhelper.lib.script.sync.{provider}.{module}', item_class)
    return item_class(*args, **kwargs)


def ItemWatched(*args, **kwargs):
    return get_sync_item('ItemWatched', 'watched', *args, **kwargs)


def ItemUnwatched(*args, **kwargs):
    return get_sync_item('ItemUnwatched', 'watched', *args, **kwargs)


def ItemWatchlist(*args, **kwargs):
    return get_sync_item('ItemWatchlist', 'watchlist', *args, **kwargs)


def ItemCollection(*args, **kwargs):
    return get_sync_item('ItemCollection', 'collection', *args, **kwargs)


def ItemProgress(*args, **kwargs):
    return get_sync_item('ItemProgress', 'watched', *args, module='progress', **kwargs)
