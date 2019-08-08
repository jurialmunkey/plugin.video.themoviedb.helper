import xbmc
import xbmcgui
from datetime import datetime
from copy import copy
from globals import _addonlogname


def age_difference(birthday, deathday=''):
    try:
        deathday = datetime.strptime(deathday, '%Y-%m-%d') if deathday else datetime.now()
        birthday = datetime.strptime(birthday, '%Y-%m-%d')
        age = deathday.year - birthday.year
        if birthday.month * 100 + birthday.day > deathday.month * 100 + deathday.day:
            age = age - 1
        return age
    except Exception:
        return


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


def dict_to_list(items, key):
    mylist = []
    for i in items:
        if i.get(key):
            mylist.append(i.get(key))
    return mylist


def iter_props(items, property, itemprops, **kwargs):
    x = 0
    for i in items:
        x = x + 1
        for key, value in kwargs.items():
            if i.get(value):
                itemprops[property + '.' + str(x) + '.' + key] = i.get(value)
    return itemprops


def invalid_apikey(api_name='TMDb'):
    xbmcgui.Dialog().ok('Missing/Invalid ' + api_name + ' API Key',
                        'You must enter a valid ' + api_name + ' API key to use this add-on')
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
