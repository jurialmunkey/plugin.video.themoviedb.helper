import xbmcplugin
import utils
import apis
from globals import _handle, _omdb_apikey
from listitem import ListItem


class Container:
    def __init__(self):
        self.name = ''  # Container.PluginCategory
        self.list_type = ''  # DBType of Items in List
        self.request_tmdb_id = ''  # TMDb ID to request
        self.request_tmdb_type = ''  # TMDb ID to request
        self.request_path = ''  # TMDb path to request
        self.request_key = ''  # The JSON key containing our request
        self.request_filter_key = ''  # Filter: Combines with request_filter_value
        self.request_filter_value = ''  # Filter: Include only items with key matching this value
        self.request_kwparams = {}  # Additional kwparams to pass to request
        self.omdb_info = {}  # OMDb info dict
        self.next_type = ''  # &type= for next action in ListItem.FolderPath
        self.next_info = ''  # ?info= for next action in ListItem.FolderPath
        self.listitems = []  # The list of items to add
        self.kodi_library = {}  # JSON RPC Results to check DBID

    def start_container(self):
        xbmcplugin.setPluginCategory(_handle, self.name)
        container_content = utils.convert_to_kodi_type(self.list_type) + 's' if self.list_type else ''
        xbmcplugin.setContent(_handle, container_content)

    def finish_container(self):
        xbmcplugin.endOfDirectory(_handle)

    def create_folders(self, categories, inclusions, exclusions, dbtype, **kwargs):
        """
        Creates the folders for plugin base and ?info=details
        Includes keys matching inclusions and excludes key matching exclusions
        Constructs a folder for each type (or the specified dbtype) per each permitted key
        """
        for key, category in sorted(categories.items(), key=lambda keycat: keycat[1].get('index')):
            if not inclusions or key in inclusions:
                if not exclusions or key not in exclusions:
                    for category_type in category.get('types'):
                        if not dbtype or category_type == dbtype:
                            listitem = ListItem()
                            listitem.request_tmdb_type = category_type
                            listitem.plural_type = utils.convert_to_plural_type(category_type)
                            listitem.name = category.get('name').format(self=listitem)
                            # if category.get('list_type'):
                            #     category_type = category.get('list_type').format(self=listitem)
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
        if self.request_tmdb_type == 'movie':
            self.kodi_library = utils.jsonrpc_library('VideoLibrary.GetMovies', 'movie')
        elif self.request_tmdb_type == 'tv':
            self.kodi_library = utils.jsonrpc_library('VideoLibrary.GetTVShows', 'tvshow')
        for item in self.listitems:
            # Check if filter key is present in item
            # If key is present must match value to be included in items
            # If the key is not present then don't include either
            if self.request_filter_key and self.request_filter_value:
                if item.get(self.request_filter_key):
                    if item.get(self.request_filter_key) != self.request_filter_value:
                        continue
                else:
                    continue
            # Create Item
            listitem = ListItem()
            # Get additional CACHED info
            if item.get('id') and self.request_tmdb_type:
                request_path = '{0}/{1}'.format(self.request_tmdb_type, item.get('id'))
                kwparams = {}
                if self.request_tmdb_type in ['movie', 'tv']:
                    kwparams['append_to_response'] = 'credits'
                listitem.detailed_info = apis.tmdb_api_only_cached(request_path, **kwparams)
                if listitem.detailed_info:
                    item = utils.merge_two_dicts(item, listitem.detailed_info)
                    if item.get('imdb_id') and self.request_tmdb_type in ['movie', 'tv']:
                        listitem.omdb_info = apis.omdb_api_only_cached(i=item.get('imdb_id'))
            # Get item info
            listitem.get_title(item)
            if self.kodi_library.get(listitem.name):
                listitem.dbid = self.kodi_library.get(listitem.name).get('dbid')
            listitem.get_autofilled_info(item)
            listitem.get_dbtypes(self.list_type)
            if listitem.omdb_info:
                listitem.get_omdb_info(listitem.omdb_info)
            if self.omdb_info:
                listitem.get_omdb_info(self.omdb_info)
            listitem.create_kwparams(self.next_type, self.next_info)
            listitem.create_listitem(**listitem.kwparams)

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
            if self.request_key:
                self.listitems = self.listitems.get(self.request_key, [])
            if self.listitems and not isinstance(self.listitems, list):
                self.listitems = [self.listitems]
        else:
            raise ValueError('No API request path specified')
