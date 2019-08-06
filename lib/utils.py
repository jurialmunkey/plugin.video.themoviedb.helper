import xbmc
import xbmcgui
from copy import copy
from globals import _addonlogname


def kodi_log(value, level=0):
    if level == 1:
        xbmc.log(_addonlogname + str(value), level=xbmc.LOGNOTICE)
    else:
        xbmc.log(_addonlogname + str(value), level=xbmc.LOGDEBUG)


def dictify(r, root=True):
    if root:
        return {r.tag: dictify(r, False)}
    d = copy(r.attrib)
    if r.text:
        d["_text"] = r.text
    for x in r.findall("./*"):
        if x.tag not in d:
            d[x.tag] = []
        d[x.tag].append(dictify(x, False))
    return d


def del_dict_keys(dictionary, keys):
    for key in keys:
        if dictionary.get(key):
            del dictionary[key]
    return dictionary


def concatinate_names(items, key, separator):
    concat = ''
    for i in items:
        if i.get(key):
            if concat:
                concat = concat + ' ' + separator + ' ' + i.get(key)
            else:
                concat = i.get(key)
    return concat


def iter_props(items, name, itemprops):
    x = 0
    for i in items:
        x = x + 1
        itemprops[name + '.' + str(x) + '.Name'] = i.get('name', '')
        if i.get('id'):
            itemprops[name + '.' + str(x) + '.ID'] = i.get('id', '')
    return itemprops


def invalid_apikey():
    xbmcgui.Dialog().ok('Missing/Invalid TheMovieDb API Key',
                        'You must enter a valid TheMovieDb API key to use this add-on')
    xbmc.executebuiltin('Addon.OpenSettings(plugin.video.themoviedb.helper)')


def convert_to_plural_type(tmdb_type):
    if tmdb_type == 'tv':
        return 'Tv Shows'
    elif tmdb_type == 'person':
        return 'People'
    else:
        return tmdb_type.capitalize() + 's'


def convert_to_kodi_type(tmdb_type):
    if tmdb_type == 'tv':
        return 'tvshow'
    elif tmdb_type == 'person':
        return 'actor'
    else:
        return tmdb_type


def convert_to_library_type(tmdb_type):
    if tmdb_type == 'tv' or tmdb_type == 'movie':
        return 'video'
    elif tmdb_type == 'image':
        return 'pictures'
    else:
        return ''


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def make_kwparams(params):
    tempparams = params.copy()
    return del_dict_keys(tempparams, ['info', 'type', 'tmdb_id'])
