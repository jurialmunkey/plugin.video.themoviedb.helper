# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

def map_kwargs(mapping={}):
    """ Decorator to remap kwargs key names """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for k, v in mapping.items():
                if k in kwargs:
                    kwargs[v] = kwargs.pop(k, None)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def is_in_kwargs(mapping={}):
    """ Decorator to check that kwargs values match allowlist before running
    Accepts a dictionary of {kwarg: [allowlist]} key value pairs
    Decorated method is not run if kwargs.get(kwarg) not in [allowlist]
    Optionally can use {kwarg: True} to check kwarg exists and has any value
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for k, v in mapping.items():
                if v is True:
                    if kwargs.get(k) is None:
                        return
                else:
                    if kwargs.get(k) not in v:
                        return
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_tmdb_id(func):
    """ Decorator to get tmdb_id if not in kwargs """
    def wrapper(*args, **kwargs):
        from tmdbhelper.lib.addon.dialog import BusyDialog
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        with BusyDialog():
            kwargs['tmdb_id'] = kwargs.get('tmdb_id') or FindQueriesDatabase().get_tmdb_id(**kwargs)
            if not kwargs['tmdb_id']:
                return
        return func(*args, **kwargs)
    return wrapper
