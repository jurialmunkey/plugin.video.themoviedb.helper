import sys
import xbmcplugin
import xbmcgui
import xbmc
import utils
import apis
from globals import _handle, APPEND_TO_RESPONSE, _omdb_apikey, CATEGORIES, MAINFOLDER, EXCLUSIONS, GENRE_IDS, _prefixname
from listitem import ListItem
from urlparse import parse_qsl


class Container:
    def __init__(self):
        self.paramstring = sys.argv[2][1:]
        self.params = dict(parse_qsl(self.paramstring))
        self.name = ''  # Container.PluginCategory
        self.list_type = ''  # DBType of Items in List
        self.request_tmdb_id = ''  # TMDb ID to request
        self.request_tmdb_type = ''  # TMDb ID to request
        self.request_path = ''  # TMDb path to request
        self.request_key = ''  # The JSON key containing our request
        self.request_season = ''  # The season number to request for episodes
        self.request_episode = ''  # The episode number to request for episodes
        self.request_kwparams = {}  # Additional kwparams to pass to request
        self.extra_request_path = ''  # Extra request to add details
        self.extra_request_key = ''  # Extra request to add details
        self.url_kwargs = {}  # Addition kwargs to pass to url
        self.omdb_info = {}  # OMDb info dict
        self.next_type = ''  # &type= for next action in ListItem.FolderPath
        self.next_info = ''  # ?info= for next action in ListItem.FolderPath
        self.listitems = []  # The list of items to add

    def start_container(self):
        xbmcplugin.setPluginCategory(_handle, self.name)
        container_content = utils.convert_to_container_type(self.list_type) if self.list_type else ''
        xbmcplugin.setContent(_handle, container_content)

    def finish_container(self):
        xbmcplugin.endOfDirectory(_handle)

    def create_folders(self, inclusions=MAINFOLDER, exclusions=EXCLUSIONS, dbtype='', **kwargs):
        """
        Creates the folders for plugin base and ?info=details
        Includes keys matching inclusions and excludes key matching exclusions
        Constructs a folder for each type (or the specified dbtype) per each permitted key
        """
        for key, category in sorted(CATEGORIES.items(), key=lambda keycat: keycat[1].get('index')):
            if not inclusions or key in inclusions:
                if not exclusions or key not in exclusions:
                    for category_type in category.get('types'):
                        if not dbtype or category_type == dbtype:
                            listitem = ListItem()
                            listitem.request_tmdb_type = category_type
                            listitem.plural_type = utils.convert_to_plural_type(category_type)
                            listitem.name = category.get('name').format(self=listitem)
                            if self.listitems:
                                listitem.get_autofilled_info(self.listitems[0])
                                listitem.get_dbtypes(category_type)
                            if self.omdb_info:
                                listitem.get_omdb_info(self.omdb_info)
                            listitem.create_listitem(info=key, type=category_type, **kwargs)

    def create_listitems(self):
        """
        Iterates over self.listitems for each item that should be in the list
        Before creating the listitem, checks if we have a cached detailed item and adds that info too
        Otherwise just uses whatever the api had returned
        """
        added_items = []
        num_dbid_items = 0
        num_tmdb_items = 0
        kodi_library = utils.get_kodi_library(self.list_type)
        listitems = self.listitems[:]
        self.listitems = []
        for item in listitems:
            if item:
                # Filter items by filter_key and filter_value params
                if utils.filtered_item(item, self.params.get('filter_key'), self.params.get('filter_value')):
                    continue  # Skip items that don't match filter item[key]=value
                if utils.filtered_item(item, self.params.get('exclude_key'), self.params.get('exclude_value'), True):
                    continue  # Skip items that match exclusion item[key]=value (true flag flips return vals)
                item['name'] = utils.get_title(item)
                item['year'] = utils.get_year(item)
                item_add_id = '{0}-{1}'.format(item.get('name'), item.get('year'))
                if item_add_id in added_items:
                    continue  # Skip duplicates
                item = apis.get_cached_data(item, self.request_tmdb_type)
                item['dbid'] = utils.get_kodi_dbid(item, kodi_library)
                added_items.append(item_add_id)
                self.listitems.append(item)
        for item in self.listitems:
            if item:
                listitem = ListItem()
                listitem.name = item.get('name')
                listitem.dbid = item.get('dbid')
                listitem.get_autofilled_info(item)
                listitem.get_dbtypes(self.list_type)
                if item.get('imdb_id'):
                    self.omdb_info = apis.omdb_api_only_cached(i=item.get('imdb_id'))
                if self.omdb_info:
                    listitem.get_omdb_info(self.omdb_info)
                if self.next_type == 'person':
                    listitem.create_kwparams(self.next_type, self.next_info)
                else:
                    if self.request_key == 'episodes' or (self.params.get('season') and self.params.get('episode')):
                        listitem.create_kwparams(self.next_type, self.next_info,
                                                 tmdb_id=self.request_tmdb_id,
                                                 season=self.params.get('season', '0'),
                                                 episode=listitem.infolabels.get('episode'))
                    elif self.request_key == 'seasons' or self.params.get('season'):
                        listitem.create_kwparams(self.next_type, self.next_info,
                                                 tmdb_id=self.request_tmdb_id,
                                                 season=listitem.infolabels.get('season', '0'))
                    else:
                        listitem.create_kwparams(self.next_type, self.next_info)
                if listitem.dbid:
                    num_dbid_items = num_dbid_items + 1
                else:
                    num_tmdb_items = num_tmdb_items + 1
                listitem.create_listitem(**listitem.kwparams)
        if num_dbid_items > 0 and self.params.get('prop_id'):
            window_prop = '{0}{1}.NumDBIDItems'.format(_prefixname, self.params.get('prop_id'))
            xbmcgui.Window(10000).setProperty(window_prop, str(num_dbid_items))
        if num_tmdb_items > 0 and self.params.get('prop_id'):
            window_prop = '{0}{1}.NumTMDBItems'.format(_prefixname, self.params.get('prop_id'))
            xbmcgui.Window(10000).setProperty(window_prop, str(num_tmdb_items))

    def request_omdb_info(self):
        if self.request_tmdb_type in ['movie', 'tv']:
            if _omdb_apikey and self.listitems:
                if self.listitems[0].get('imdb_id'):
                    self.imdb_id = self.listitems[0].get('imdb_id')
                    self.omdb_info = apis.omdb_api_request(i=self.imdb_id)

    def request_list(self):
        """
        Makes the request to TMDb API
        Can pass kwargs as additional params
        Checks if a certain request_key is needed and provides that key
        Converts a single item dict to a list containing the dict for iteration purposes
        """
        if self.request_path:
            self.listitems = apis.tmdb_api_request(self.request_path, **self.request_kwparams)
            self.listitems = self.listitems.get(self.request_key, []) if self.request_key else self.listitems
            if self.listitems and not isinstance(self.listitems, list):
                self.listitems = [self.listitems]
        else:
            raise ValueError('No API request path specified')

    def request_extra_list(self, ):
        if self.extra_request_path and self.listitems:
            self.extra_listitems = apis.tmdb_api_request(self.extra_request_path, **self.request_kwparams)
            self.extra_listitems = self.extra_listitems.get(self.extra_request_key, []) if self.extra_request_key else self.extra_listitems
            self.listitems[0] = utils.merge_two_dicts(self.extra_listitems, self.listitems[0])

    def check_tmdb_id(self, request_type=None):
        request_type = self.params.get('type') if not request_type else request_type
        if self.params.get('info') in MAINFOLDER:
            return
        elif self.params.get('tmdb_id'):
            return
        elif self.params.get('imdb_id'):
            self.list_find()
        elif self.params.get('query'):
            self.params['query'] = utils.split_items(self.params.get('query'))[0]
            utils.kodi_log('Searching... [No TMDb ID specified]', 0)
            request_path = 'search/{0}'.format(request_type)
            request_kwparams = utils.make_kwparams(self.params)
            item = apis.tmdb_api_request_longcache(request_path, **request_kwparams)
            if item and item.get('results') and isinstance(item.get('results'), list) and item.get('results')[0].get('id'):
                self.params['tmdb_id'] = item.get('results')[0].get('id')
                utils.kodi_log('Found TMDb ID {0}!\n{1}'.format(self.params.get('tmdb_id'), self.paramstring), 0)
            else:
                utils.kodi_log('Unable to find TMDb ID!\n{0}'.format(self.paramstring), 1)
        else:
            utils.kodi_log('Must specify either &tmdb_id= &imdb_id= &query=: {0}!'.format(self.paramstring), 1)
            exit()

    def translate_discover(self):
        """
        Translate with_ params into IDs for discover method
        Get with_separator=AND|OR|NONE and concatinate IDs accordingly for url request
        TODO: add with_id=True param to skip search and just concatinate
        """
        # Translate our separator into a url encoding
        if self.params.get('with_separator'):
            if self.params.get('with_separator') == 'AND':
                separator = '%2C'
            elif self.params.get('with_separator') == 'OR':
                separator = '%7C'
            else:
                separator = False
        else:
            separator = '%2C'
        # Check if with_id param specified and set request type accordingly
        if self.params.get('with_id') and self.params.get('with_id') != 'False':
            request_genres = False
            request_companies = False
            request_person = False
        else:
            request_genres = GENRE_IDS
            request_companies = 'search/company'
            request_person = 'search/person'
        if self.params.get('with_genres'):
            self.params['with_genres'] = apis.translate_lookup_ids(self.params.get('with_genres'), request_genres, True, separator)
        if self.params.get('without_genres'):
            self.params['without_genres'] = apis.translate_lookup_ids(self.params.get('without_genres'), request_genres, True, separator)
        if self.params.get('with_companies'):
            self.params['with_companies'] = apis.translate_lookup_ids(self.params.get('with_companies'), request_companies, False, False)
        if self.params.get('with_people'):
            self.params['with_people'] = apis.translate_lookup_ids(self.params.get('with_people'), request_person, False, separator)
        if self.params.get('with_crew'):
            self.params['with_crew'] = apis.translate_lookup_ids(self.params.get('with_crew'), request_person, False, separator)
        if self.params.get('with_cast'):
            self.params['with_cast'] = apis.translate_lookup_ids(self.params.get('with_cast'), request_person, False, separator)

    def list_details(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=details&type=&tmdb_id=
        Makes a request from API to get details about an item
        Lists all request lists that are compatible with item dbtype
        """
        exclusions = MAINFOLDER
        exclusions.extend(EXCLUSIONS)
        self.request_tmdb_id = self.params.get('tmdb_id')
        self.request_tmdb_type = self.params.get('type')
        self.params['append_to_response'] = APPEND_TO_RESPONSE
        if self.params.get('type') in ['episode']:
            self.url_kwargs['season'] = self.params.get('season', '0')
            self.url_kwargs['episode'] = self.params.get('episode')
            self.extra_request_path = 'tv/{0}'.format(self.params.get('tmdb_id'))
            self.request_path = 'tv/{0}/season/{1}/episode/{2}'.format(self.params.get('tmdb_id'),
                                                                       self.params.get('season', '0'),
                                                                       self.params.get('episode'))
        else:
            self.request_path = '{self.request_tmdb_type}/{self.request_tmdb_id}'.format(self=self)
        self.request_kwparams = utils.make_kwparams(self.params)
        self.list_type = self.request_tmdb_type
        self.next_type = self.request_tmdb_type
        self.next_info = 'details'
        self.request_list()
        self.request_extra_list()
        self.request_omdb_info()
        self.start_container()
        self.create_listitems()
        self.create_folders([], exclusions, self.request_tmdb_type, tmdb_id=self.request_tmdb_id, **self.url_kwargs)
        self.finish_container()

    def list_items(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=category&type=&tmdb_id=
        Makes a request from API and list the items
        """
        self.category = CATEGORIES[self.params.get('info')]
        self.request_tmdb_id = self.params.get('tmdb_id')
        self.request_tmdb_type = self.params.get('type')
        self.params['append_to_response'] = APPEND_TO_RESPONSE
        self.request_season = self.params.get('season')
        self.request_episode = self.params.get('episode')
        self.request_path = self.category.get('path').format(self=self)
        self.request_key = self.category.get('key').format(self=self)
        self.request_kwparams = utils.make_kwparams(self.params)
        self.list_type = self.category.get('list_type').format(self=self)
        self.next_type = self.category.get('next_type').format(self=self)
        self.next_info = self.category.get('next_info').format(self=self)
        self.request_list()
        self.start_container()
        self.create_listitems()
        self.finish_container()

    def list_search(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=search&query=&year=
        Requests API search for item
        """
        self.params['query'] = self.params.get('query')
        if not self.params.get('query'):
            self.params['query'] = xbmcgui.Dialog().input('Enter Search Query', type=xbmcgui.INPUT_ALPHANUM)
        if self.params.get('query'):
            self.list_items()

    def list_find(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=find&type=&imdb_id=
        Find details of item based on imdb_id
        """
        self.request_tmdb_type = self.params.get('type')
        self.imdb_id = self.params.get('imdb_id')
        if not self.imdb_id and self.params.get('info') == 'find':
            self.imdb_id = xbmcgui.Dialog().input('Enter IMDb ID', type=xbmcgui.INPUT_ALPHANUM)
        if self.imdb_id:
            request_key = CATEGORIES['find']['key'].format(self=self)
            request_path = CATEGORIES['find']['path'].format(self=self)
            item = apis.tmdb_api_request_longcache(request_path, external_source='imdb_id')
            if item and item.get(request_key):
                item = item.get(request_key)[0]
                self.params['tmdb_id'] = item.get('id')
                self.params['type'] = 'movie'
                utils.kodi_log('Found TMDb ID {0}!\n{1}'.format(self.params.get('tmdb_id'), self.paramstring), 1)
                if self.params.get('info') == 'find':
                    self.list_details()

    def list_categories(self):
        """
        plugin://plugin.video.themoviedb.helper/
        The Base Dir of the plugin
        Provides all lists in MAINFOLDER
        """
        self.start_container()
        self.create_folders()
        self.finish_container()

    def router(self):
        """
        Router Function
        Runs different functions depending on ?info= param
        """
        if self.params:
            if self.params.get('info') == 'textviewer':
                xbmcgui.Dialog().textviewer('$INFO[ListItem.Label]', '$INFO[ListItem.Plot]')
            elif self.params.get('info') == 'imageviewer':
                xbmc.executebuiltin('ShowPicture({0})'.format(self.params.get('image')))
            elif self.params.get('info') == 'discover':
                self.translate_discover()
                self.list_items()
            elif self.params.get('info') == 'collection':
                self.check_tmdb_id('collection')
                self.list_items()
            elif not self.params.get('info') or not self.params.get('type'):
                utils.kodi_log('Invalid paramstring - Must specify info and type: {0}!'.format(self.paramstring), 1)
            elif self.params.get('info') == 'search':
                self.list_search()
            elif self.params.get('info') == 'find':
                self.list_find()
            elif self.params.get('info') == 'details':
                self.check_tmdb_id()
                self.list_details()
            elif self.params.get('info') in CATEGORIES:
                self.check_tmdb_id()
                self.list_items()
            else:
                utils.kodi_log('Invalid ?info= param: {0}!'.format(self.paramstring), 1)
        else:
            self.list_categories()
