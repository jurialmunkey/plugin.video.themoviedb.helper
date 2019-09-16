import xbmc
import json
from datetime import datetime
from copy import copy
from globals import _addonlogname, IMAGEPATH
from urllib import urlencode
_url = 'plugin://plugin.video.themoviedb.helper/'


def jsonrpc_library(method="VideoLibrary.GetMovies", dbtype="movie"):
    query = {"jsonrpc": "2.0",
             "params": {"properties": ["title", "imdbnumber", "originaltitle", "year"]},
             "method": method,
             "id": 1}
    response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
    my_list = []
    dbid_name = '{0}id'.format(dbtype)
    key_to_get = '{0}s'.format(dbtype)
    for item in response.get('result', {}).get(key_to_get, []):
        my_list.append({'imdb_id': item.get('imdbnumber'),
                        'dbid': item.get(dbid_name),
                        'title': item.get('title'),
                        'originaltitle': item.get('originaltitle'),
                        'year': item.get('year')})
    return my_list


def get_kodi_dbid(item, kodi_library):
    dbid = None
    if kodi_library:
        index_list = find_dict_in_list(kodi_library, 'imdb_id', item.get('imdb_id')) if item.get('imdb_id') else []
        if not index_list and item.get('original_title'):
            index_list = find_dict_in_list(kodi_library, 'originaltitle', item.get('original_title'))
        if not index_list and item.get('name'):
            index_list = find_dict_in_list(kodi_library, 'title', item.get('name'))
        for i in index_list:
            if item.get('year'):
                if item.get('year') in str(kodi_library[i].get('year')):
                    dbid = kodi_library[i].get('dbid')
            else:
                dbid = kodi_library[i].get('dbid')
            if dbid:
                return dbid


def get_kodi_library(list_type):
    if list_type == 'movie':
        return jsonrpc_library("VideoLibrary.GetMovies", "movie")
    elif list_type == 'tv':
        return jsonrpc_library("VideoLibrary.GetTVShows", "tvshow")


def get_title(request_item):
    if request_item.get('title'):
        return request_item.get('title')
    elif request_item.get('name'):
        return request_item.get('name')
    elif request_item.get('author'):
        return request_item.get('author')
    elif request_item.get('width') and request_item.get('height'):
        return u'{0}x{1}'.format(request_item.get('width'), request_item.get('height'))
    else:
        return u'N/A'


def get_icon(request_item):
    if request_item.get('poster_path'):
        return '{0}{1}'.format(IMAGEPATH, request_item.get('poster_path'))
    elif request_item.get('profile_path'):
        return '{0}{1}'.format(IMAGEPATH, request_item.get('profile_path'))
    elif request_item.get('file_path'):
        return '{0}{1}'.format(IMAGEPATH, request_item.get('file_path'))


def get_year(request_item):
    if request_item.get('air_date'):
        return request_item.get('air_date')[:4]
    if request_item.get('release_date'):
        return request_item.get('release_date')[:4]
    if request_item.get('first_air_date'):
        return request_item.get('first_air_date')[:4]


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def filtered_item(item, key, value, false_val=False):
    true_val = False if false_val else True  # Flip values if we want to exclude instead of include
    if key and value:
        if item.get(key):
            if item.get(key) == value:
                return false_val
            else:
                return true_val
        else:
            return true_val
    else:
        return False


def age_difference(birthday, deathday=''):
    try:  # Added Error Checking as strptime doesn't work correctly on LibreElec
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
        xbmc.log('{0}{1}'.format(_addonlogname, value), level=xbmc.LOGNOTICE)
    else:
        xbmc.log('{0}{1}'.format(_addonlogname, value), level=xbmc.LOGDEBUG)


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
                concat = '{0} {1} {2}'.format(concat, separator, i.get(key))
            else:
                concat = i.get(key)
    return concat


def dict_to_list(items, key):
    mylist = []
    for i in items:
        if i.get(key):
            mylist.append(i.get(key))
    return mylist


def find_dict_in_list(list_of_dicts, key, value):
    index_list = []
    for list_index, dic in enumerate(list_of_dicts):
        if dic.get(key) == value:
            index_list.append(list_index)
    return index_list


def split_items(items, separator='/'):
    separator = ' {0} '.format(separator)
    if separator in items:
        items = items.split(separator)
    items = [items] if isinstance(items, str) else items  # Make sure we return a list to prevent a string being iterated over characters
    return items


def iter_props(items, property, itemprops, **kwargs):
    x = 0
    for i in items:
        x = x + 1
        for key, value in kwargs.items():
            if i.get(value):
                itemprops['{0}.{1}.{2}'.format(property, x, key)] = i.get(value)
    return itemprops


def convert_to_plural_type(tmdb_type):
    if tmdb_type == 'tv':
        return 'Tv Shows'
    elif tmdb_type == 'person':
        return 'People'
    else:
        return '{0}s'.format(tmdb_type.capitalize())


def convert_to_listitem_type(tmdb_type):
    if tmdb_type == 'tv':
        return 'tvshow'
    elif tmdb_type == 'person':
        return 'actor'
    else:
        return tmdb_type


def convert_to_container_type(tmdb_type):
    if tmdb_type == 'tv':
        return 'tvshows'
    elif tmdb_type == 'person':
        return 'actors'
    else:
        return '{0}s'.format(tmdb_type)


def convert_to_library_type(tmdb_type):
    if tmdb_type == 'image':
        return 'pictures'
    else:
        return 'video'


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def make_kwparams(params):
    tempparams = params.copy()
    return del_dict_keys(tempparams, ['info', 'type', 'tmdb_id', 'filter_key', 'filter_value',
                                      'with_separator', 'with_id', 'season', 'episode', 'prop_id',
                                      'exclude_key', 'exclude_value'])
