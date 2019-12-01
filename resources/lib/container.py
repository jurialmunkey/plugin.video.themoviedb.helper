import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import resources.lib.utils as utils
from resources.lib.traktapi import traktAPI
from resources.lib.listitem import ListItem
from resources.lib.player import Player
from resources.lib.plugin import Plugin
from resources.lib.globals import BASEDIR_MAIN, BASEDIR_TMDB, BASEDIR_LISTS, TMDB_LISTS, DETAILED_CATEGORIES, TRAKT_LISTS, TRAKT_LISTLISTS, TRAKT_HISTORYLISTS, TRAKT_MANAGEMENT
try:
    from urllib.parse import parse_qsl  # Py3
except ImportError:
    from urlparse import parse_qsl  # Py2


class Container(Plugin):
    def __init__(self):
        super(Container, self).__init__()
        self.handle = int(sys.argv[1])
        self.paramstring = sys.argv[2][1:] if sys.version_info.major == 3 else sys.argv[2][1:].decode("utf-8")
        self.params = dict(parse_qsl(self.paramstring))
        self.dbtype = None
        self.nexttype = None
        self.url_info = None
        self.plugincategory = 'TMDb Helper'
        self.containercontent = ''
        self.library = 'video'
        self.updatelisting = False

    def start_container(self):
        xbmcplugin.setPluginCategory(self.handle, self.plugincategory)  # Container.PluginCategory
        xbmcplugin.setContent(self.handle, self.containercontent)  # Container.Content

    def finish_container(self):
        xbmcplugin.endOfDirectory(self.handle, updateListing=self.updatelisting)

    def translate_discover(self):
        lookup_company = None if self.params.get('with_id') and self.params.get('with_id') != 'False' else 'company'
        lookup_person = None if self.params.get('with_id') and self.params.get('with_id') != 'False' else 'person'
        lookup_genre = None if self.params.get('with_id') and self.params.get('with_id') != 'False' else 'genre'

        if self.params.get('with_genres'):
            self.params['with_genres'] = self.tmdb.get_translated_list(
                utils.split_items(self.params.get('with_genres')),
                lookup_genre,
                separator=self.params.get('with_separator'))

        if self.params.get('without_genres'):
            self.params['without_genres'] = self.tmdb.get_translated_list(
                utils.split_items(self.params.get('without_genres')),
                lookup_genre,
                separator=self.params.get('with_separator'))

        if self.params.get('with_companies'):
            self.params['with_companies'] = self.tmdb.get_translated_list(
                utils.split_items(self.params.get('with_companies')),
                lookup_company,
                separator='NONE')

        if self.params.get('with_people'):
            self.params['with_people'] = self.tmdb.get_translated_list(
                utils.split_items(self.params.get('with_people')),
                lookup_person,
                separator=self.params.get('with_separator'))

        if self.params.get('with_cast'):
            self.params['with_cast'] = self.tmdb.get_translated_list(
                utils.split_items(self.params.get('with_cast')),
                lookup_person,
                separator=self.params.get('with_separator'))

        if self.params.get('with_crew'):
            self.params['with_crew'] = self.tmdb.get_translated_list(
                utils.split_items(self.params.get('with_crew')),
                lookup_person,
                separator=self.params.get('with_separator'))

    def url_encoding(self, item):
        url = item.get('url') or {'info': self.url_info}
        url['type'] = item.get('mixed_type') or self.nexttype or self.params.get('type')

        if item.get('tmdb_id'):
            url['tmdb_id'] = item.get('tmdb_id')

        if url.get('info') == 'play':
            item['is_folder'] = False

        if url.get('info') == 'imageviewer':
            item['is_folder'] = False
            url = {'info': 'imageviewer', 'image': item.get('icon')}

        if url.get('info') == 'textviewer':
            item['is_folder'] = False
            url = {'info': 'textviewer'}

        if self.params.get('info') in ['seasons', 'episodes'] or url.get('type') in ['season', 'episode']:
            url['tmdb_id'] = self.params.get('tmdb_id')
            url['season'] = item.get('infolabels', {}).get('season')
            url['episode'] = item.get('infolabels', {}).get('episode')

        item['url'] = url
        return item

    def get_details(self, item):
        if self.params.get('info') in ['seasons', 'episodes'] or item['url'].get('type') in ['season', 'episode']:
            if not self.details_tv:
                self.details_tv = self.tmdb.get_detailed_item('tv', self.params.get('tmdb_id'), season=self.params.get('season', None))

            if self.details_tv:
                item = utils.del_empty_keys(item)
                item['infolabels'] = utils.del_empty_keys(item.get('infolabels', {}))
                item['infoproperties'] = utils.del_empty_keys(item.get('infoproperties', {}))
                item['infolabels'] = utils.merge_two_dicts(self.details_tv.get('infolabels', {}), item.get('infolabels', {}))
                item['infoproperties'] = utils.merge_two_dicts(self.details_tv.get('infoproperties', {}), item.get('infoproperties', {}))
                item = utils.merge_two_dicts(self.details_tv, item)

        if item['url'].get('type') in ['movie', 'tv']:
            detailed_item = self.tmdb.get_detailed_item(item['url'].get('type'), item['url'].get('tmdb_id'), cache_only=True)
            if detailed_item:
                detailed_item['infolabels'] = utils.merge_two_dicts(item.get('infolabels', {}), detailed_item.get('infolabels', {}))
                detailed_item['infoproperties'] = utils.merge_two_dicts(item.get('infoproperties', {}), detailed_item.get('infoproperties', {}))
                detailed_item['label'] = item.get('label')
                item = utils.merge_two_dicts(item, detailed_item)

        if item['url'].get('type') == 'movie':
            item = self.get_omdb_ratings(item, cache_only=True)

        return item

    def list_items(self, items):
        added = []
        dbiditems = []
        tmdbitems = []
        mixed_movies = 0
        mixed_tvshows = 0
        for i in items:
            name = u'{0}{1}'.format(i.get('label'), i.get('poster'))
            if name in added:  # Don't add duplicate items
                continue
            if i.get('infolabels', {}).get('season', 1) == 0:  # Ignore Specials
                continue
            added.append(name)

            i = self.url_encoding(i)
            i = self.get_details(i)
            i = self.get_db_info(i, 'dbid')

            if i.get('mixed_type', '') == 'tv':
                mixed_tvshows += 1
            elif i.get('mixed_type', '') == 'movie':
                mixed_movies += 1

            if i.get('dbid'):
                dbiditems.append(i)
            else:
                tmdbitems.append(i)
        items = dbiditems + tmdbitems

        if self.params.get('type') == 'both':
            self.containercontent = 'tvshows' if mixed_tvshows > mixed_movies else 'movies'

        self.start_container()
        for i in items:
            url = i.pop('url', {})
            self.dbtype = utils.type_convert(i.pop('mixed_type', ''), 'dbtype') or self.dbtype
            i.setdefault('infolabels', {})['mediatype'] = self.dbtype if self.dbtype and not i.get('label') == 'Next Page' else ''
            listitem = ListItem(library=self.library, **i)
            listitem.create_listitem(self.handle, **url)
        self.finish_container()

        if self.params.get('prop_id'):
            window_prop = '{0}{1}.NumDBIDItems'.format(self.prefixname, self.params.get('prop_id'))
            xbmcgui.Window(10000).setProperty(window_prop, str(len(dbiditems)))
            window_prop = '{0}{1}.NumTMDBItems'.format(self.prefixname, self.params.get('prop_id'))
            xbmcgui.Window(10000).setProperty(window_prop, str(len(tmdbitems)))

    def list_tmdb(self, *args, **kwargs):
        if self.params.get('type'):
            cat = TMDB_LISTS.get(self.params.get('info'), {})
            url_ext = dict(parse_qsl(cat.get('url_ext', '').format(**self.params)))
            path = cat.get('path', '').format(**self.params)
            kwparams = utils.make_kwparams(self.params)
            kwparams = utils.merge_two_dicts(kwparams, kwargs)
            kwparams = utils.merge_two_dicts(kwparams, url_ext)
            kwparams.setdefault('key', cat.get('key', 'results'))
            items = self.tmdb.get_list(path, *args, **kwparams)
            itemtype = cat.get('itemtype') or self.params.get('type') or ''
            self.url_info = cat.get('url_info', 'details')
            self.nexttype = cat.get('nexttype')
            self.dbtype = utils.type_convert(itemtype, 'dbtype')
            self.plugincategory = cat.get('name', '').format(utils.type_convert(itemtype, 'plural'))
            self.containercontent = utils.type_convert(itemtype, 'container')
            self.list_items(items)

    def list_play(self):
        Player(
            itemtype=self.params.get('type'), tmdb_id=self.params.get('tmdb_id'),
            season=self.params.get('season'), episode=self.params.get('episode'))

    def list_traktmanagement(self):
        if not self.params.get('trakt') in TRAKT_MANAGEMENT:
            return
        with utils.busy_dialog():
            _traktapi = traktAPI()
            slug_type = 'show' if self.params.get('type') == 'episode' else utils.type_convert(self.params.get('type'), 'trakt')
            trakt_type = utils.type_convert(self.params.get('type'), 'trakt')
            slug = _traktapi.get_traktslug(slug_type, 'tmdb', self.params.get('tmdb_id'))
            item = _traktapi.get_details(slug_type, slug, season=self.params.get('season', None), episode=self.params.get('episode', None))
            items = {trakt_type + 's': [item]}
            if self.params.get('trakt') == 'watchlist_add':
                _traktapi.sync_watchlist(slug_type, mode='add', items=items)
            if self.params.get('trakt') == 'history_add':
                _traktapi.sync_history(slug_type, mode='add', items=items)
            if self.params.get('trakt') == 'collection_add':
                _traktapi.sync_collection(slug_type, mode='add', items=items)
            if self.params.get('trakt') == 'watchlist_remove':
                _traktapi.sync_watchlist(slug_type, mode='remove', items=items)
            if self.params.get('trakt') == 'history_remove':
                _traktapi.sync_history(slug_type, mode='remove', items=items)
            if self.params.get('trakt') == 'collection_remove':
                _traktapi.sync_collection(slug_type, mode='remove', items=items)
            # TODO: Check status response and add dialog
        self.updatelisting = True

    def list_details(self):
        """ Gets detailed information about item and creates folder shortcuts to relevant list categories """
        d_args = ('tv', self.params.get('tmdb_id'), self.params.get('season'), self.params.get('episode')) if self.params.get('type') == 'episode' else (self.params.get('type'), self.params.get('tmdb_id'))
        if self.params.get('refresh') == 'True':
            with utils.busy_dialog():
                self.tmdb.get_detailed_item(*d_args, cache_refresh=True)
            xbmc.executebuiltin('Container.Refresh')
            xbmcgui.Dialog().ok('Cache Refresh', 'Cached details were refreshed')
            self.updatelisting = True

        details = self.tmdb.get_detailed_item(*d_args)
        if not details:
            return

        # URL ENCODING FOR TOP ITEM
        if self.params.get('type') == 'movie':
            details = self.get_omdb_ratings(details, cache_only=False)
            details['url'] = {'info': 'play'}
        if self.params.get('type') == 'tv':
            details['url'] = {'info': 'seasons'}
        if self.params.get('type') == 'episode':
            details['url'] = {'info': 'play'}

        # CREATE CATEGORIES
        items = [details]
        for i in DETAILED_CATEGORIES:
            cat = TMDB_LISTS.get(i) or TRAKT_LISTS.get(i) or {}
            if self.params.get('type') in cat.get('types'):
                item = details.copy()
                item['label'] = cat.get('name')
                item['url'] = cat.get('url', {}).copy()
                item['url']['info'] = i
                if cat.get('url_key') and item.get(cat.get('url_key')):
                    item['url'][cat.get('url_key')] = item.get(cat.get('url_key'))
                items.append(item)

        # ADD TRAKT ITEMS
        if xbmcaddon.Addon().getSetting('trakt_token'):
            _traktapi = traktAPI()
            trakt_collection = _traktapi.sync_collection(utils.type_convert(self.params.get('type'), 'trakt'), 'tmdb')
            if trakt_collection:
                boolean = 'remove' if details.get('tmdb_id') in trakt_collection else 'add'
                item_collection = details.copy()
                item_collection['label'] = 'Remove from Trakt Collection' if boolean == 'remove' else 'Add to Trakt Collection'
                item_collection['url'] = {'info': 'details', 'trakt': 'collection_{0}'.format(boolean)}
                items.append(item_collection)
            trakt_watchlist = _traktapi.sync_watchlist(utils.type_convert(self.params.get('type'), 'trakt'), 'tmdb')
            if trakt_watchlist:
                boolean = 'remove' if details.get('tmdb_id') in trakt_watchlist else 'add'
                item_watchlist = details.copy()
                item_watchlist['label'] = 'Remove from Trakt Watchlist' if boolean == 'remove' else 'Add to Trakt Watchlist'
                item_watchlist['url'] = {'info': 'details', 'trakt': 'watchlist_{0}'.format(boolean)}
                items.append(item_watchlist)
            trakt_history = _traktapi.sync_history(utils.type_convert(self.params.get('type'), 'trakt'), 'tmdb')
            if trakt_history:
                boolean = 'remove' if details.get('tmdb_id') in trakt_history else 'add'
                item_history = details.copy()
                item_history['label'] = 'Remove from Trakt Watched History' if boolean == 'remove' else 'Add to Trakt Watched History'
                item_history['url'] = {'info': 'details', 'trakt': 'history_{0}'.format(boolean)}
                items.append(item_history)

        # ADD A REFRESH CACHE ITEM
        refresh = details.copy()
        refresh['label'] = 'Refresh Cache'
        refresh['url'] = {'info': 'details', 'refresh': 'True'}
        items.append(refresh)

        # BUILD CONTAINER
        self.dbtype = utils.type_convert(self.params.get('type'), 'dbtype')
        self.plugincategory = details.get('label')
        self.containercontent = utils.type_convert(self.params.get('type'), 'container')
        self.list_items(items)

    def list_search(self):
        if not self.params.get('query'):
            self.params['query'] = xbmcgui.Dialog().input('Enter Search Query', type=xbmcgui.INPUT_ALPHANUM)
        if self.params.get('query'):
            self.list_tmdb(query=self.params.get('query'), year=self.params.get('year'))

    def list_credits(self, key='cast'):
        items = self.tmdb.get_credits_list(self.params.get('type'), self.params.get('tmdb_id'), key)
        self.url_info = 'details'
        self.nexttype = 'person'
        self.plugincategory = key.capitalize()
        self.containercontent = 'actors'
        self.list_items(items)

    def list_getid(self):
        self.params['tmdb_id'] = self.get_tmdb_id(**self.params)

    def list_trakthistory(self):
        _traktapi = traktAPI()
        userslug = _traktapi.get_usernameslug()
        if self.params.get('info') == 'trakt_inprogress':
            trakt_items = _traktapi.get_inprogress(userslug, limit=10)
        if self.params.get('info') == 'trakt_mostwatched':
            trakt_items = _traktapi.get_mostwatched(userslug, utils.type_convert(self.params.get('type'), 'trakt'), limit=10)
        if self.params.get('info') == 'trakt_history':
            trakt_items = _traktapi.get_recentlywatched(userslug, utils.type_convert(self.params.get('type'), 'trakt'), limit=10)
        items = [self.tmdb.get_detailed_item(self.params.get('type'), i[1]) for i in trakt_items]
        if items:
            self.nexttype = self.params.get('type')
            self.dbtype = utils.type_convert(self.nexttype, 'dbtype')
            self.url_info = 'trakt_upnext' if self.params.get('info') == 'trakt_inprogress' else 'details'
            self.plugincategory = utils.type_convert(self.nexttype, 'plural')
            self.containercontent = utils.type_convert(self.nexttype, 'container')
            self.list_items(items)

    def list_traktupnext(self):
        _traktapi = traktAPI()
        imdb_id = self.tmdb.get_item_externalid(itemtype='tv', tmdb_id=self.params.get('tmdb_id'), external_id='imdb_id')
        trakt_items = _traktapi.get_upnext(imdb_id)
        items = [self.tmdb.get_detailed_item(itemtype='tv', tmdb_id=self.params.get('tmdb_id'), season=i[0], episode=i[1]) for i in trakt_items]
        if items:
            itemtype = 'episode'
            self.nexttype = 'episode'
            self.url_info = 'details'
            self.dbtype = utils.type_convert(itemtype, 'dbtype')
            self.plugincategory = utils.type_convert(itemtype, 'plural')
            self.containercontent = utils.type_convert(itemtype, 'container')
            self.list_items(items[:10])

    def list_traktuserlists(self):
        _traktapi = traktAPI()
        path = TRAKT_LISTS.get(self.params.get('info'), {}).get('path', '')
        if '{user_slug}' in path:
            self.params['user_slug'] = self.params.get('user_slug') or _traktapi.get_usernameslug()
        path = path.format(**self.params)
        items = _traktapi.get_listlist(path, 'list')
        icon = '{0}/resources/trakt.png'.format(self.addonpath)
        self.start_container()
        for i in items:
            label = i.get('name')
            label2 = i.get('user', {}).get('name')
            infolabels = {}
            infolabels['plot'] = i.get('description')
            infolabels['rating'] = i.get('likes')
            list_slug = i.get('ids', {}).get('slug')
            user_slug = i.get('user', {}).get('ids', {}).get('slug')
            listitem = ListItem(label=label, label2=label2, icon=icon, thumb=icon, poster=icon, infolabels=infolabels)
            listitem.create_listitem(self.handle, info='trakt_userlist', user_slug=user_slug, list_slug=list_slug, type=self.params.get('type'))
        self.finish_container()

    def list_trakt(self):
        items = []
        if self.params.get('type'):
            _traktapi = traktAPI()
            cat = TRAKT_LISTS.get(self.params.get('info', ''), {})
            if '{user_slug}' in cat.get('path', ''):
                self.params['user_slug'] = self.params.get('user_slug') or _traktapi.get_usernameslug()
            params = self.params.copy()
            itemtype = 'movie' if self.params.get('type') == 'both' else self.params.get('type', '')
            keylist = ['movie', 'show'] if self.params.get('type') == 'both' else [utils.type_convert(itemtype, 'trakt')]
            params['type'] = utils.type_convert(itemtype, 'trakt') + 's'
            path = cat.get('path', '').format(**params)
            trakt_items = _traktapi.get_itemlist(path, keylist=keylist, page=self.params.get('page', 1), limit=10, req_auth=cat.get('req_auth'))
            for i in trakt_items[:11]:
                item = None
                if i[0] == 'imdb':
                    item = self.tmdb.get_externalid_item(i[2], i[1], 'imdb_id')
                if i[0] == 'tvdb':
                    item = self.tmdb.get_externalid_item(i[2], i[1], 'tvdb_id')
                if i[0] == 'next_page':
                    item = {'label': 'Next Page', 'url': self.params.copy()}
                    item['url']['page'] = i[1]
                if item:
                    item['mixed_type'] = i[2]
                    items.append(item)
        if items:
            self.nexttype = itemtype
            self.dbtype = utils.type_convert(itemtype, 'dbtype')
            self.url_info = cat.get('url_info', 'details')
            self.plugincategory = cat.get('name', '').format(utils.type_convert(itemtype, 'plural'))
            self.containercontent = utils.type_convert(itemtype, 'container') or 'movies'
            self.list_items(items)

    def list_basedir(self):
        """
        Creates a listitem for each type of each category in BASEDIR
        """
        basedir = BASEDIR_LISTS.get(self.params.get('info'), {}).get('path') or BASEDIR_MAIN
        self.start_container()
        for i in basedir:
            cat = BASEDIR_LISTS.get(i) or TMDB_LISTS.get(i) or TRAKT_LISTS.get(i) or {}
            icon = cat.get('icon', '').format(self.addonpath)
            for t in cat.get('types', []):
                label = cat.get('name', '').format(utils.type_convert(t, 'plural'))
                listitem = ListItem(label=label, icon=icon, thumb=icon, poster=icon)
                url = {'info': i, 'type': t} if t else {'info': i}
                listitem.create_listitem(self.handle, **url)
        self.finish_container()

    def router(self):
        # FILTERS AND EXCLUSIONS
        self.tmdb.filter_key = self.params.get('filter_key', None)
        self.tmdb.filter_value = utils.split_items(self.params.get('filter_value', None))[0]
        self.tmdb.exclude_key = self.params.get('exclude_key', None)
        self.tmdb.exclude_value = utils.split_items(self.params.get('exclude_value', None))[0]

        # ROUTER LIST FUNCTIONS
        if self.params.get('info') == 'play':
            self.list_getid()
            self.list_play()
        elif self.params.get('info') == 'discover':
            self.translate_discover()
            self.list_tmdb()
        elif self.params.get('info') in ['details', 'refresh']:
            self.list_getid()
            self.list_traktmanagement()
            self.list_details()
        elif self.params.get('info') == 'search':
            self.list_search()
        elif self.params.get('info') == 'cast':
            self.list_getid()
            self.list_credits('cast')
        elif self.params.get('info') == 'crew':
            self.list_getid()
            self.list_credits('crew')
        elif self.params.get('info') == 'textviewer':
            self.textviewer(xbmc.getInfoLabel('ListItem.Label'), xbmc.getInfoLabel('ListItem.Plot'))
        elif self.params.get('info') == 'imageviewer':
            self.imageviewer(self.params.get('image'))
        elif self.params.get('info') in TRAKT_HISTORYLISTS:
            self.list_trakthistory()
        elif self.params.get('info') == 'trakt_upnext':
            self.list_getid()
            self.list_traktupnext()
        elif self.params.get('info') in TRAKT_LISTLISTS:
            self.list_traktuserlists()
        elif self.params.get('info') in TRAKT_LISTS:
            self.list_trakt()
        elif self.params.get('info') in BASEDIR_TMDB:
            self.list_tmdb()
        elif self.params.get('info') in TMDB_LISTS and TMDB_LISTS.get(self.params.get('info'), {}).get('path'):
            self.list_getid()
            self.list_tmdb()
        elif self.params.get('info') in BASEDIR_LISTS:
            self.list_basedir()
        elif not self.params:
            self.list_basedir()
