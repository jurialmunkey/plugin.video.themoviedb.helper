from sys import modules

_LEVELS = {
    'general': 2 ** 0,
    'fanarttv': 2 ** 1,
    'mdblist': 2 ** 2,
    'omdb': 2 ** 3,
    'tmdb': 2 ** 4,
    'trakt': 2 ** 5,
    'tvdb': 2 ** 6,
}


def third_party_permissions(require=None, grant=None):
    if require:
        granted = getattr(modules.get('themoviedb_helper'), '__permissions__',
                          False)
        if not granted:
            return True
        permissions = require
    else:
        granted = None
        permissions = grant

    if not permissions or 'none' in permissions:
        permissions_set = set()
    elif 'deny' in permissions:
        permissions_set = {None}
    elif 'all' in permissions:
        permissions_set = set(_LEVELS.values())
    else:
        permissions_set = set()
        for permission in permissions:
            permission = _LEVELS.get(permission)
            if permission:
                permissions_set.add(permission)

    if granted:
        return not bool(permissions_set - granted)
    return permissions_set
