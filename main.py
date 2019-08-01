# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# With thanks to Roman V. M. for original simple plugin code

import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
ADDON_PATH = xbmcaddon.Addon().getAddonInfo('path')
DIALOG = xbmcgui.Dialog()
OMDB_API_KEY = xbmcplugin.getSetting(_handle, 'omdb_apikey')
OMDB_HTTPS_API = 'http://www.omdbapi.com/'
API_KEY = xbmcplugin.getSetting(_handle, 'tmdb_apikey')
HTTPS_API = 'https://api.themoviedb.org/3'
LANGUAGE = '&language=en-US'
IMAGEPATH = 'https://image.tmdb.org/t/p/original/'
EXCLUDE = ['no_exclusions']
DIR_MAIN = ['search_', 'popular_', 'toprated_', 'upcoming_', 'nowplaying_', 'find_']
CATEGORIES = {'search_movie':
              {'title': 'Search Movies',
               'item_dbtype': 'movie',
               'request_dbtype': 'movie',
               'request_key': 'results',
               },
              'search_tv':
              {'title': 'Search Tv Shows',
               'item_dbtype': 'tv',
               'request_dbtype': 'tv',
               'request_key': 'results',
               },
              'search_people':
              {'title': 'Search People',
               'item_dbtype': 'person',
               'request_dbtype': 'person',
               'request_key': 'results',
               },
              'find_movie':
              {'title': 'Find by IMDb_ID (Movie)',
               'item_dbtype': 'movie',
               'request_dbtype': 'movie',
               'request_key': 'movie_results',
               },
              'find_tv':
              {'title': 'Find by IMDb_ID (Tv Show)',
               'item_dbtype': 'tv',
               'request_dbtype': 'tv',
               'request_key': 'tv_results',
               },
              'popular_movie':
              {'title': 'Popular Movies',
               'item_dbtype': 'movie',
               'request_list': 'popular',
               'request_dbtype': 'movie',
               'request_key': 'results',
               },
              'popular_tv':
              {'title': 'Popular Tv Shows',
               'item_dbtype': 'tv',
               'request_list': 'popular',
               'request_dbtype': 'tv',
               'request_key': 'results',
               },
              'popular_person':
              {'title': 'Popular People',
               'item_dbtype': 'person',
               'request_list': 'popular',
               'request_dbtype': 'person',
               'request_key': 'results',
               },
              'toprated_movie':
              {'title': 'Top Rated Movies',
               'item_dbtype': 'movie',
               'request_list': 'top_rated',
               'request_dbtype': 'movie',
               'request_key': 'results',
               },
              'toprated_tv':
              {'title': 'Top Rated Tv Shows',
               'item_dbtype': 'tv',
               'request_list': 'top_rated',
               'request_dbtype': 'tv',
               'request_key': 'results',
               },
              'upcoming_movie':
              {'title': 'Upcoming Movies',
               'item_dbtype': 'movie',
               'request_list': 'upcoming',
               'request_dbtype': 'movie',
               'request_key': 'results',
               },
              'upcoming_tv':
              {'title': 'Airing Today',
               'item_dbtype': 'tv',
               'request_list': 'airing_today',
               'request_dbtype': 'tv',
               'request_key': 'results',
               },
              'nowplaying_movie':
              {'title': 'In Theatres',
               'item_dbtype': 'movie',
               'request_list': 'now_playing',
               'request_dbtype': 'movie',
               'request_key': 'results',
               },
              'nowplaying_tv':
              {'title': 'Currently Airing',
               'item_dbtype': 'tv',
               'request_list': 'on_the_air',
               'request_dbtype': 'tv',
               'request_key': 'results',
               },
              'recommended_movie':
              {'title': 'Recommended Movies',
               'item_dbtype': 'movie',
               'request_list': 'recommendations',
               'request_dbtype': 'movie',
               'request_key': 'results',
               },
              'recommended_tv':
              {'title': 'Recommended Tv Shows',
               'item_dbtype': 'tv',
               'request_list': 'recommendations',
               'request_dbtype': 'tv',
               'request_key': 'results',
               },
              'similar_movie':
              {'title': 'Similar Movies',
               'item_dbtype': 'movie',
               'request_list': 'similar',
               'request_dbtype': 'movie',
               'request_key': 'results',
               },
              'similar_tv':
              {'title': 'Similar Tv Shows',
               'item_dbtype': 'tv',
               'request_list': 'similar',
               'request_dbtype': 'tv',
               'request_key': 'results',
               },
              'review_movie':
              {'title': 'Reviews',
               'item_dbtype': 'review',
               'request_list': 'reviews',
               'request_dbtype': 'movie',
               'request_key': 'results',
               },
              'review_tv':
              {'title': 'Reviews',
               'item_dbtype': 'review',
               'request_list': 'reviews',
               'request_dbtype': 'tv',
               'request_key': 'results',
               },
              'cast_movie':
              {'title': 'Cast',
               'item_dbtype': 'person',
               'request_list': 'credits',
               'request_dbtype': 'movie',
               'request_key': 'cast',
               },
              'cast_tv':
              {'title': 'Cast',
               'item_dbtype': 'person',
               'request_list': 'credits',
               'request_dbtype': 'tv',
               'request_key': 'cast',
               },
              'crew_movie':
              {'title': 'Crew',
               'item_dbtype': 'person',
               'request_list': 'credits',
               'request_dbtype': 'movie',
               'request_key': 'crew',
               },
              'crew_tv':
              {'title': 'Crew',
               'item_dbtype': 'person',
               'request_list': 'credits',
               'request_dbtype': 'tv',
               'request_key': 'crew',
               },
              'keywords_movie':
              {'title': 'Keywords',
               'item_dbtype': 'keyword',
               'request_list': 'keywords',
               'request_dbtype': 'movie',
               'request_key': 'keywords',
               },
              'keywords_tv':
              {'title': 'Keywords',
               'item_dbtype': 'keyword',
               'request_list': 'keywords',
               'request_dbtype': 'tv',
               'request_key': 'results',
               },
              'moviecast_person':
              {'title': 'Movies as Cast',
               'item_dbtype': 'movie',
               'request_list': 'movie_credits',
               'request_dbtype': 'person',
               'request_key': 'cast',
               },
              'tvcast_person':
              {'title': 'Tv Shows as Cast',
               'item_dbtype': 'tv',
               'request_list': 'tv_credits',
               'request_dbtype': 'person',
               'request_key': 'cast',
               },
              'moviecrew_person':
              {'title': 'Movies as Crew',
               'item_dbtype': 'movie',
               'request_list': 'movie_credits',
               'request_dbtype': 'person',
               'request_key': 'crew',
               },
              'tvcrew_person':
              {'title': 'Tv Shows as Crew',
               'item_dbtype': 'tv',
               'request_list': 'tv_credits',
               'request_dbtype': 'person',
               'request_key': 'crew',
               },
              'images_person':
              {'title': 'Images',
               'item_dbtype': 'image',
               'request_list': 'images',
               'request_dbtype': 'person',
               'request_key': 'profiles',
               },
              }

DBTYPE_DICT = {'movie': ('video', 'movie', 'movies'),
               'tv': ('video', 'tvshow', 'tvshows'),
               'person': ('', '', 'actors'),
               'image': ('pictures', '', 'actors'),
               }


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def textviewer(title, text):
    DIALOG.textviewer(str(title), str(text))


def make_request(request):
    xbmcgui.Window(10000).setProperty('TheMovieDb.Helper.APIRequest', request)  # DEBUGGING
    request = requests.get(request)  # Request our data
    if not request.status_code == requests.codes.ok:  # Error Checking
        if request.status_code == 401:
            invalid_apikey()
            exit()
        else:
            raise ValueError(request.raise_for_status())
    request = request.json()  # Make the request nice
    return request


def tmdb_api_request(*args, **kwargs):
    request = HTTPS_API
    for arg in args:
        if arg:  # Don't add empty args
            request = request + '/' + arg
    request = request + '?api_key=' + API_KEY + LANGUAGE
    for key, value in kwargs.items():
        if value:  # Don't add empty kwargs
            request = request + '&' + key + '=' + value
    request = make_request(request)
    return request


def omdb_api_request(**kwargs):
    request = OMDB_HTTPS_API + '?apikey=' + OMDB_API_KEY
    for key, value in kwargs.items():
        if value:  # Don't add empty kwargs
            request = request + '&' + key + '=' + value
    request = make_request(request)
    return request


def convert_to_librarytype(dbtype):
    if dbtype in DBTYPE_DICT:
        return DBTYPE_DICT[dbtype][0]
    else:
        return 'video'


def convert_to_dbtype(dbtype):
    if dbtype in DBTYPE_DICT:
        return DBTYPE_DICT[dbtype][1]
    else:
        return 'video'


def convert_to_containercontent(dbtype):
    if dbtype in DBTYPE_DICT:
        return DBTYPE_DICT[dbtype][2]
    else:
        return ''


def get_title(item):
    if item.get('title'):
        return item['title']
    elif item.get('name'):
        return item['name']
    elif item.get('author'):
        return item['author']
    elif item.get('width') and item.get('height'):
        return str(item['width']) + 'x' + str(item['height'])
    else:
        return 'N/A'


def get_artwork_poster(item):
    if item.get('poster_path'):
        return IMAGEPATH + item['poster_path']
    elif item.get('profile_path'):
        return IMAGEPATH + item['profile_path']
    elif item.get('file_path'):
        return IMAGEPATH + item['file_path']
    else:
        return ADDON_PATH + '/icon.png'


def get_artwork_fanart(item):
    if item.get('backdrop_path'):
        return IMAGEPATH + item['backdrop_path']
    else:
        return ADDON_PATH + '/fanart.jpg'


def concatinate_names(items, key, separator):
    concat = ''
    for i in items:
        if i.get(key):
            if concat:
                concat = concat + ' ' + separator + ' ' + i.get(key)
            else:
                concat = i.get(key)
    return concat


def get_omdb_item_info(i, iteminfo):
    if i.get('Rated'):
        iteminfo['MPAA'] = 'Rated ' + i['Rated']
    if i.get('Writer'):
        iteminfo['Writer'] = i['Writer']
    if i.get('Director'):
        iteminfo['Director'] = i['Director']
    return iteminfo


def get_omdb_item_props(i, itemprops):
    if i.get('Ratings'):
        for rating in i.get('Ratings'):
            if rating.get('Source') == 'Internet Movie Database':
                itemprops['Rating.IMDB'] = rating.get('Value', '')[:-3]
            elif rating.get('Source') == 'Rotten Tomatoes':
                itemprops['Rating.RottenTomatoes'] = rating.get('Value', '')[:-1]
            elif rating.get('Source') == 'Metacritic':
                itemprops['Rating.Metacritic'] = rating.get('Value', '')[:-4]
    if i.get('Awards'):
        itemprops['Awards'] = i.get('Awards', '')
    return itemprops


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


def list_create_infoitem(dbtype, tmdb_id, title):
    if not dbtype:
        return  # Need a type to make a request
    elif not tmdb_id and not title:
        return  # Need an ID or search query
    elif not tmdb_id:
        return  # TODO use search function to grab id
    i = tmdb_api_request(dbtype, tmdb_id)
    mediatype = convert_to_dbtype(dbtype)
    librarytype = convert_to_librarytype(dbtype)
    title = get_title(i)
    list_item = xbmcgui.ListItem(label=title)

    # ADD INFO
    iteminfo = {'title': title, 'mediatype': mediatype}
    iteminfo = get_item_info(i, iteminfo)
    if i.get('imdb_id') and OMDB_API_KEY:
        omdb_info = omdb_api_request(i=i.get('imdb_id', ''))
        iteminfo = get_omdb_item_info(omdb_info, iteminfo)
    list_item.setInfo(librarytype, iteminfo)

    # ADD PROPERTIES
    itemprops = {'tmdb_id': tmdb_id}
    itemprops = get_item_properties(i, itemprops)
    if i.get('imdb_id') and OMDB_API_KEY:
        itemprops = get_omdb_item_props(omdb_info, itemprops)
    list_item.setProperties(itemprops)

    # ADD ARTWORK
    poster = get_artwork_poster(i)
    fanart = get_artwork_fanart(i)
    list_item.setArt({'thumb': poster, 'icon': poster, 'poster': poster, 'fanart': fanart})

    # ADD ITEM
    is_folder = True
    url = get_url(info='item', tmdb_id=i.get('id', ''), type=dbtype, title=title)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    return iteminfo, itemprops, poster, fanart


def list_items(items, **kwargs):
    xbmcplugin.setPluginCategory(_handle, '')  # Set Container.PluginCategory
    dbtype = kwargs.get('type', '')
    container_content = convert_to_containercontent(dbtype)
    mediatype = convert_to_dbtype(dbtype)
    librarytype = convert_to_librarytype(dbtype)
    xbmcplugin.setContent(_handle, container_content)  # Container.Content

    for i in items:
        title = get_title(i)
        list_item = xbmcgui.ListItem(label=title)

        # ADD INFO
        iteminfo = {'title': title, 'mediatype': mediatype}
        iteminfo = get_item_info(i, iteminfo)
        list_item.setInfo(librarytype, iteminfo)

        # ADD PROPERTIES
        itemprops = {'tmdb_id': i.get('id', '')}
        itemprops = get_item_properties(i, itemprops)
        list_item.setProperties(itemprops)

        # ADD ARTWORK
        poster = get_artwork_poster(i)
        fanart = get_artwork_fanart(i)
        list_item.setArt({'thumb': poster, 'icon': poster, 'poster': poster, 'fanart': fanart})

        # ADD ITEM
        is_folder = True
        if dbtype == 'review':
            url = get_url(info='textviewer', title=title, text=i.get('content'))
        elif dbtype == 'image':
                url = get_url(info='imageviewer', image=poster)
        else:
            url = get_url(info='item', tmdb_id=i.get('id', ''), **kwargs)
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    xbmcplugin.endOfDirectory(_handle)  # End Dir


def list_search(params, categories):
    # If no query specified in plugin path then prompt user
    if params.get('query'):
        query = params['query']
    else:
        query = DIALOG.input('Enter Search Query', type=xbmcgui.INPUT_ALPHANUM)

    # If no year specified in plugin path then leave blank
    year = params.get('year', '')

    # Check query exists and search type is valid before searching
    if query and params.get('info') in categories:
        category = categories.get(params.get('info'))
        items = tmdb_api_request('search', category.get('request_dbtype'), query=query, year=year)
        items = items.get('results')
        list_items(items, type=category.get('item_dbtype'))


def list_find_by_imdb(params, categories):
    # If no imdb_id specified in plugin path then prompt user
    if params.get('imdb_id'):
        imdb_id = params['imdb_id']
    else:
        imdb_id = DIALOG.input('Enter IMDB ID', type=xbmcgui.INPUT_ALPHANUM)

    # Check query exists and search type is valid before searching
    if imdb_id and params.get('info') in categories:
        category = categories.get(params.get('info'))
        items = tmdb_api_request('find', imdb_id, external_source='imdb_id')
        items = items.get(category.get('request_key'))
        tmdb_id = str(items[0]['id'])  # TODO: Add error checking that we got something
        title = get_title(items[0])
        include_these = ['_' + category.get('request_dbtype')]
        items = construct_categories(include_these, CATEGORIES, DIR_MAIN)
        list_categories(items, type=category.get('request_dbtype'), tmdb_id=tmdb_id, title=title)


def construct_categories(matches, items, exclusions):
    new_dictionary = {}
    for match in matches:
        for i in items:
            if match in i:
                for exclusion in exclusions:
                    if exclusion in i:
                        break
                else:
                    new_dictionary[i] = items[i]
    return new_dictionary


def list_categories(items, **kwargs):
    xbmcplugin.setPluginCategory(_handle, '')  # Set Container.PluginCategory
    dbtype = kwargs.get('type', '')
    tmdb_id = kwargs.get('tmdb_id', '')
    title = kwargs.get('title', '')
    container_content = convert_to_containercontent(dbtype)
    librarytype = convert_to_librarytype(dbtype)
    xbmcplugin.setContent(_handle, container_content)  # Set Container.Content()
    iteminfo = {}
    itemprops = {}
    poster = ADDON_PATH + '/icon.png'
    fanart = ADDON_PATH + '/fanart.jpg'
    if tmdb_id or title:
        iteminfo, itemprops, poster, fanart = list_create_infoitem(dbtype, tmdb_id, title)
    for i in items:
        list_item = xbmcgui.ListItem(label=items[i]['title'])
        list_item.setInfo(librarytype, iteminfo)
        list_item.setProperties(itemprops)
        list_item.setArt({'thumb': poster, 'icon': poster, 'poster': poster, 'fanart': fanart})
        keywords = get_keywords(kwargs)
        url = get_url(info=i, **keywords)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)  # Add Item
    if not tmdb_id:
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)  # Finish Dir


def get_keywords(dictionary):
    keywords = {}
    for key, value in dictionary.items():
        if value:
            keywords[key] = value
    return keywords


def check_tmdb_id(params, dbtype):
    if params.get('tmdb_id'):
        return params.get('tmdb_id')
    elif params.get('imdb_id'):
        items = tmdb_api_request('find', params.get('imdb_id'), external_source='imdb_id')
        items = items.get('results')
        return str(items[0]['id'])
    elif params.get('title'):
        items = tmdb_api_request('search', dbtype, query=params.get('title'), year=params.get('year'))
        items = items.get('results')
        return str(items[0]['id'])
    else:
        return ''


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params.get('info') == 'item':
            if not params.get('type'):
                raise ValueError('Invalid paramstring - ?info=item must specify type: {0}!'.format(paramstring))
            include_these = ['_' + params.get('type')]
            items = construct_categories(include_these, CATEGORIES, DIR_MAIN)
            tmdb_id = check_tmdb_id(params, params.get('type'))
            list_categories(items, type=params.get('type'), tmdb_id=params.get('tmdb_id'), title=params.get('title'))
        elif 'textviewer' in params.get('info'):
            textviewer(params.get('title'), params.get('text'))
        elif 'imageviewer' in params.get('info'):
            xbmc.executebuiltin('ShowPicture(' + params.get('image') + ')')
        elif 'search_' in params.get('info'):
            list_search(params, CATEGORIES)
        elif 'find_' in params.get('info'):
            list_find_by_imdb(params, CATEGORIES)
        elif params.get('info') in CATEGORIES:
            category = CATEGORIES[params.get('info')]
            tmdb_id = check_tmdb_id(params, category.get('request_dbtype'))
            items = tmdb_api_request(category.get('request_dbtype'), tmdb_id, category.get('request_list'))
            list_items(items.get(category.get('request_key')), type=category.get('item_dbtype'))
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        items = construct_categories(DIR_MAIN, CATEGORIES, EXCLUDE)
        list_categories(items)


def invalid_apikey():
    DIALOG.ok('Missing/Invalid TheMovieDb API Key',
              'You must enter a valid TheMovieDb API key to use this add-on')
    xbmc.executebuiltin('Addon.OpenSettings(plugin.video.themoviedb.helper)')


if not API_KEY:
    invalid_apikey()
elif __name__ == '__main__':
    router(sys.argv[2][1:])
