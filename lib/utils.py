from globals import IMAGEPATH, _addonpath
import xbmc
import xbmcgui


def del_dict_keys(dictionary, keys):
    for key in keys:
        if dictionary.get(key):
            del dictionary[key]
    return dictionary


def get_title(i):
    if i.get('title'):
        return i['title']
    elif i.get('name'):
        return i['name']
    elif i.get('author'):
        return i['author']
    elif i.get('width') and i.get('height'):
        return str(i['width']) + 'x' + str(i['height'])
    else:
        return 'N/A'


def get_item_info(i, iteminfo):
    if i.get('overview'):
        iteminfo['plot'] = i['overview']
    elif i.get('biography'):
        iteminfo['plot'] = i['biography']
    elif i.get('content'):
        iteminfo['plot'] = i['content']
    if i.get('vote_average'):
        iteminfo['rating'] = i['vote_average']
    if i.get('vote_count'):
        iteminfo['votes'] = i['vote_count']
    if i.get('release_date'):
        iteminfo['premiered'] = i['release_date']
        iteminfo['year'] = i['release_date'][:4]
    if i.get('imdb_id'):
        iteminfo['imdbnumber'] = i['imdb_id']
    if i.get('runtime'):
        iteminfo['duration'] = i['runtime'] * 60
    if i.get('tagline'):
        iteminfo['tagline'] = i['tagline']
    if i.get('status'):
        iteminfo['status'] = i['status']
    if i.get('genres'):
        iteminfo['genre'] = concatinate_names(i.get('genres'), 'name', '/')
    if i.get('production_companies'):
        iteminfo['studio'] = concatinate_names(i.get('production_companies'), 'name', '/')
    if i.get('production_countries'):
        iteminfo['country'] = concatinate_names(i.get('production_countries'), 'name', '/')
    return iteminfo


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


def get_item_properties(i, itemprops):
    if i.get('genres'):
        itemprops = iter_props(i.get('genres'), 'Genre', itemprops)
    if i.get('production_companies'):
        itemprops = iter_props(i.get('production_companies'), 'Studio', itemprops)
    if i.get('production_countries'):
        itemprops = iter_props(i.get('production_countries'), 'Country', itemprops)
    if i.get('birthday'):
        itemprops['birthday'] = i['birthday']
    if i.get('deathday'):
        itemprops['deathday'] = i['deathday']
    if i.get('also_know_as'):
        itemprops['aliases'] = i['also_know_as']
    if i.get('known_for_department'):
        itemprops['role'] = i['known_for_department']
    if i.get('place_of_birth'):
        itemprops['born'] = i['place_of_birth']
    if i.get('budget'):
        itemprops['budget'] = '${:0,.0f}'.format(i['budget'])
    if i.get('revenue'):
        itemprops['revenue'] = '${:0,.0f}'.format(i['revenue'])
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


def get_poster(item):
    if item.get('poster_path'):
        return IMAGEPATH + item['poster_path']
    elif item.get('profile_path'):
        return IMAGEPATH + item['profile_path']
    elif item.get('file_path'):
        return IMAGEPATH + item['file_path']
    else:
        return _addonpath + '/icon.png'


def get_fanart(item):
    if item.get('backdrop_path'):
        return IMAGEPATH + item['backdrop_path']
    else:
        return _addonpath + '/fanart.jpg'


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def make_kwparams(params):
    return del_dict_keys(params, ['info', 'type', 'tmdb_id'])
