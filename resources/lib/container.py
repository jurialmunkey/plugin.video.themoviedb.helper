import sys
import xbmc
import xbmcgui
import xbmcplugin
import datetime
import resources.lib.utils as utils
from resources.lib.traktapi import traktAPI
from resources.lib.listitem import ListItem
from resources.lib.player import Player
from resources.lib.plugin import Plugin
from resources.lib.globals import BASEDIR_MAIN, BASEDIR_PATH, DETAILED_CATEGORIES, TMDB_LISTS, TRAKT_LISTS, TRAKT_CALENDAR
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
        self.item_tmdbtype = None
        self.item_dbtype = None
        self.url = {}
        self.details_tv = None
        self.plugincategory = 'TMDb Helper'
        self.containercontent = ''
        self.mixed_containercontent = ''
        self.library = 'video'
        self.updatelisting = False
        self.trakt_management = self.addon.getSettingBool('trakt_management')

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

    def get_sortedlist(self, items):
        if not items:
            return

        added, dbiditems, tmdbitems, lastitems, firstitems = [], [], [], [], []
        mixed_movies, mixed_tvshows = 0, 0

        if self.item_tmdbtype in ['season', 'episode']:
            if not self.details_tv:
                self.details_tv = self.tmdb.get_detailed_item('tv', self.params.get('tmdb_id'), season=self.params.get('season', None))

        if self.item_tmdbtype == 'season' and self.details_tv and self.addon.getSetting('trakt_token'):
            item_upnext = ListItem(library=self.library, **self.details_tv)
            item_upnext.infolabels['season'] = 'Up Next'
            item_upnext.label = 'Up Next'
            item_upnext.url = {'info': 'trakt_upnext', 'type': 'tv'}
            items.append(item_upnext)

        for i in items:
            name = u'{0}{1}'.format(i.label, i.imdb_id or i.tmdb_id or i.poster)
            if name in added:
                continue
            added.append(name)

            if i.mixed_type == 'tv':
                mixed_tvshows += 1
            elif i.mixed_type == 'movie':
                mixed_movies += 1

            if self.details_tv:
                season_num = i.infolabels.get('season')
                i.infolabels = utils.merge_two_dicts(self.details_tv.get('infolabels', {}), utils.del_empty_keys(i.infolabels))
                i.infoproperties = utils.merge_two_dicts(self.details_tv.get('infoproperties', {}), utils.del_empty_keys(i.infoproperties))
                i.poster = i.poster or self.details_tv.get('poster')
                i.fanart = i.fanart if i.fanart and i.fanart != '{0}/fanart.jpg'.format(self.addonpath) else self.details_tv.get('fanart')
                i.infolabels['season'] = season_num

            i.dbid = self.get_db_info(
                i, info='dbid', tmdbtype=self.item_tmdbtype, imdb_id=i.imdb_id,
                originaltitle=i.infolabels.get('originaltitle'), title=i.infolabels.get('title'), year=i.infolabels.get('year'))

            if self.item_tmdbtype == 'season' and i.infolabels.get('season') == 0:
                lastitems.append(i)
            elif self.item_tmdbtype == 'season' and i.infolabels.get('season') == 'Up Next':
                firstitems.append(i)
            elif i.dbid:
                dbiditems.append(i)
            else:
                tmdbitems.append(i)

        if mixed_movies or mixed_tvshows:
            self.mixed_containercontent = 'tvshows' if mixed_tvshows > mixed_movies else 'movies'

        return firstitems + dbiditems + tmdbitems + lastitems

    def list_trakthistory(self):
        traktapi = traktAPI()
        userslug = traktapi.get_usernameslug()
        if self.params.get('info') == 'trakt_inprogress':
            trakt_items = traktapi.get_inprogress(userslug, limit=10)
        if self.params.get('info') == 'trakt_mostwatched':
            trakt_items = traktapi.get_mostwatched(userslug, utils.type_convert(self.params.get('type'), 'trakt'), limit=10)
        if self.params.get('info') == 'trakt_history':
            trakt_items = traktapi.get_recentlywatched(userslug, utils.type_convert(self.params.get('type'), 'trakt'), limit=10)
        items = [ListItem(library=self.library, **self.tmdb.get_detailed_item(self.params.get('type'), i[1])) for i in trakt_items]
        self.item_tmdbtype = self.params.get('type')
        self.list_items(
            items=items, url={
                'info': 'trakt_upnext' if self.params.get('info') == 'trakt_inprogress' else 'details',
                'type': self.params.get('type')})

    def list_traktupnext(self):
        traktapi = traktAPI()
        imdb_id = self.tmdb.get_item_externalid(itemtype='tv', tmdb_id=self.params.get('tmdb_id'), external_id='imdb_id')
        trakt_items = traktapi.get_upnext(imdb_id)
        items = [ListItem(library=self.library, **self.tmdb.get_detailed_item(
            itemtype='tv', tmdb_id=self.params.get('tmdb_id'), season=i[0], episode=i[1])) for i in trakt_items[:10]]
        self.item_tmdbtype = 'episode'
        self.list_items(items=items, url_tmdb_id=self.params.get('tmdb_id'), url={'info': 'details', 'type': 'episode'})

    def list_traktcalendar_episodes(self):
        date = datetime.datetime.today() + datetime.timedelta(days=utils.try_parse_int(self.params.get('startdate')))
        days = utils.try_parse_int(self.params.get('days'))
        response = traktAPI().get_calendar('shows', True, start_date=date.strftime('%Y-%m-%d'), days=days)
        items = []
        for i in response[-25:]:
            episode = i.get('episode', {}).get('number')
            season = i.get('episode', {}).get('season')
            tmdb_id = i.get('show', {}).get('ids', {}).get('tmdb')
            item = ListItem(library=self.library, **self.tmdb.get_detailed_item(
                itemtype='tv', tmdb_id=tmdb_id, season=season, episode=episode))
            item.tmdb_id, item.season, item.episode = tmdb_id, season, episode
            item.infolabels['title'] = item.label = i.get('episode', {}).get('title')
            air_date = utils.convert_timestamp(i.get('first_aired', '')) + datetime.timedelta(hours=self.utc_offset)
            item.infolabels['premiered'] = air_date.strftime('%Y-%m-%d')
            item.infolabels['year'] = air_date.strftime('%Y')
            item.infoproperties['air_time'] = air_date.strftime('%I:%M %p')
            items.append(item)
        self.item_tmdbtype = 'episode'
        self.list_items(items=items, url={'info': 'details', 'type': 'episode'})

    def list_traktcalendar(self):
        if self.params.get('type') == 'episode':
            self.list_traktcalendar_episodes()
            return
        icon = '{0}/resources/trakt.png'.format(self.addonpath)
        today = datetime.datetime.today() + datetime.timedelta(hours=self.utc_offset)
        self.start_container()
        for i in TRAKT_CALENDAR:
            date = today + datetime.timedelta(days=i[1])
            label = i[0].format(date.strftime('%A'))
            listitem = ListItem(label=label, icon=icon)
            url = {'info': 'trakt_calendar', 'type': 'episode', 'startdate': i[1], 'days': i[2]}
            listitem.create_listitem(self.handle, **url)
        self.finish_container()

    def list_traktuserlists(self):
        traktapi = traktAPI()
        path = TRAKT_LISTS.get(self.params.get('info'), {}).get('path', '')
        if '{user_slug}' in path:
            self.params['user_slug'] = self.params.get('user_slug') or traktapi.get_usernameslug()
        path = path.format(**self.params)
        items = traktapi.get_listlist(path, 'list')
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
        if not self.params.get('type'):
            return
        traktapi = traktAPI()
        cat = TRAKT_LISTS.get(self.params.get('info', ''), {})

        if '{user_slug}' in cat.get('path', ''):
            self.params['user_slug'] = self.params.get('user_slug') or traktapi.get_usernameslug()

        self.item_tmdbtype = 'movie' if self.params.get('type') == 'both' else self.params.get('type', '')

        params = self.params.copy()
        params['type'] = utils.type_convert(self.item_tmdbtype, 'trakt') + 's'
        response = traktapi.get_itemlist(
            cat.get('path', '').format(**params), page=self.params.get('page', 1), limit=10, req_auth=cat.get('req_auth'),
            keylist=['movie', 'show'] if self.params.get('type') == 'both' else [utils.type_convert(self.item_tmdbtype, 'trakt')])

        items = []
        for i in response[:11]:
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
                items.append(ListItem(library=self.library, **item))
        self.list_items(items=items, url={'info': cat.get('url_info', 'details')})

    def list_traktmanagement(self):
        if not self.params.get('trakt') in ['collection_add', 'collection_remove', 'watchlist_add', 'watchlist_remove', 'history_add', 'history_remove']:
            return
        with utils.busy_dialog():
            traktapi = traktAPI()
            slug_type = 'show' if self.params.get('type') == 'episode' else utils.type_convert(self.params.get('type'), 'trakt')
            trakt_type = utils.type_convert(self.params.get('type'), 'trakt')
            slug = traktapi.get_traktslug(slug_type, 'tmdb', self.params.get('tmdb_id'))
            item = traktapi.get_details(slug_type, slug, season=self.params.get('season', None), episode=self.params.get('episode', None))
            items = {trakt_type + 's': [item]}
            if self.params.get('trakt') == 'watchlist_add':
                traktapi.sync_watchlist(slug_type, mode='add', items=items)
            if self.params.get('trakt') == 'history_add':
                traktapi.sync_history(slug_type, mode='add', items=items)
            if self.params.get('trakt') == 'collection_add':
                traktapi.sync_collection(slug_type, mode='add', items=items)
            if self.params.get('trakt') == 'watchlist_remove':
                traktapi.sync_watchlist(slug_type, mode='remove', items=items)
            if self.params.get('trakt') == 'history_remove':
                traktapi.sync_history(slug_type, mode='remove', items=items)
            if self.params.get('trakt') == 'collection_remove':
                traktapi.sync_collection(slug_type, mode='remove', items=items)
            # TODO: Check status response and add dialog
        self.updatelisting = True

    def list_getid(self):
        self.params['tmdb_id'] = self.get_tmdb_id(**self.params)

    def list_play(self):
        Player().play(
            itemtype=self.params.get('type'), tmdb_id=self.params.get('tmdb_id'),
            season=self.params.get('season'), episode=self.params.get('episode'))

    def list_search(self):
        if not self.params.get('query'):
            self.params['query'] = xbmcgui.Dialog().input('Enter Search Query', type=xbmcgui.INPUT_ALPHANUM)
        if self.params.get('query'):
            self.list_tmdb(query=self.params.get('query'), year=self.params.get('year'))

    def list_items(self, items=None, url=None, url_tmdb_id=None):
        items = self.get_sortedlist(items)

        if not items:
            return

        self.item_dbtype = utils.type_convert(self.item_tmdbtype, 'dbtype')
        self.containercontent = self.mixed_containercontent or utils.type_convert(self.item_tmdbtype, 'container')
        self.start_container()
        for i in items:
            i.get_details(self.item_dbtype, self.tmdb, self.omdb)
            i.get_url(url, url_tmdb_id, self.params.get('widget'))
            i.create_listitem(self.handle, **i.url)
        self.finish_container()

    def list_tmdb(self, *args, **kwargs):
        if not self.params.get('type'):
            return

        # Construct request
        cat = TMDB_LISTS.get(self.params.get('info'), {})
        kwparams = utils.merge_two_dicts(utils.make_kwparams(self.params), kwargs)
        kwparams = utils.merge_two_dicts(kwparams, dict(parse_qsl(cat.get('url_ext', '').format(**self.params))))
        kwparams.setdefault('key', cat.get('key'))
        path = cat.get('path', '').format(**self.params)

        self.item_tmdbtype = cat.get('item_tmdbtype', '').format(**self.params)
        self.list_items(
            items=self.tmdb.get_list(path, *args, **kwparams),
            url_tmdb_id=cat.get('url_tmdb_id', '').format(**self.params),
            url={
                'info': cat.get('url_info', ''),
                'type': cat.get('url_type', '').format(**self.params) or self.item_tmdbtype})

    def list_credits(self, key='cast'):
        self.item_tmdbtype = 'person'
        self.plugincategory = key.capitalize()
        self.list_items(
            items=self.tmdb.get_credits_list(self.params.get('type'), self.params.get('tmdb_id'), key),
            url={'info': 'details', 'type': 'person'})

    def list_details(self):
        # Build empty container if no tmdb_id
        if not self.params.get('tmdb_id'):
            self.start_container()
            self.finish_container()
            return

        # Set detailed item arguments
        d_args = (
            ('tv', self.params.get('tmdb_id'), self.params.get('season'), self.params.get('episode'))
            if self.params.get('type') == 'episode' else (self.params.get('type'), self.params.get('tmdb_id')))

        # Check if we want to refresh cache with &amp;refresh=True
        if self.params.get('refresh') == 'True':
            with utils.busy_dialog():
                self.tmdb.get_detailed_item(*d_args, cache_refresh=True)
            xbmc.executebuiltin('Container.Refresh')
            xbmcgui.Dialog().ok('Cache Refresh', 'Cached details were refreshed')
            self.updatelisting = True

        # Get details of item and return if nothing found
        details = self.tmdb.get_detailed_item(*d_args)
        if not details:
            return

        # Merge OMDb rating details for movies
        if self.params.get('type') == 'movie':
            details = self.get_omdb_ratings(details, cache_only=False)

        # Create first item
        firstitem = ListItem(library=self.library, **details)
        if self.params.get('type') == 'movie':
            firstitem.url = {'info': 'play', 'type': self.params.get('type')}
        elif self.params.get('type') == 'tv':
            firstitem.url = {'info': 'seasons', 'type': self.params.get('type')}
        elif self.params.get('type') == 'episode':
            firstitem.url = {'info': 'play', 'type': self.params.get('type')}
        else:
            firstitem.url = {'info': 'details', 'type': self.params.get('type')}
        items = [firstitem]

        # Build categories
        for i in DETAILED_CATEGORIES:
            if self.params.get('type') in i.get('types'):
                item = ListItem(library=self.library, **details)
                item.label = i.get('name')
                item.url = {'info': i.get('info'), 'type': self.params.get('type')}
                if i.get('url_key') and details.get(i.get('url_key')):
                    item.url[i.get('url_key')] = details.get(i.get('url_key'))
                items.append(item)

        # Add trakt management items if &amp;manage=True
        if self.addon.getSetting('trakt_token') and self.params.get('manage') == 'True':
            traktapi = traktAPI()
            trakt_collection = traktapi.sync_collection(utils.type_convert(self.params.get('type'), 'trakt'), 'tmdb')
            if trakt_collection:
                boolean = 'remove' if details.get('tmdb_id') in trakt_collection else 'add'
                item_collection = ListItem(library=self.library, **details)
                item_collection.label = 'Remove from Trakt Collection' if boolean == 'remove' else 'Add to Trakt Collection'
                item_collection.url = {'info': 'details', 'trakt': 'collection_{0}'.format(boolean), 'type': self.params.get('type')}
                items.append(item_collection)
            trakt_watchlist = traktapi.sync_watchlist(utils.type_convert(self.params.get('type'), 'trakt'), 'tmdb')
            if trakt_watchlist:
                boolean = 'remove' if details.get('tmdb_id') in trakt_watchlist else 'add'
                item_watchlist = ListItem(library=self.library, **details)
                item_watchlist.label = 'Remove from Trakt Watchlist' if boolean == 'remove' else 'Add to Trakt Watchlist'
                item_watchlist.url = {'info': 'details', 'trakt': 'watchlist_{0}'.format(boolean), 'type': self.params.get('type')}
                items.append(item_watchlist)
            trakt_history = traktapi.sync_history(utils.type_convert(self.params.get('type'), 'trakt'), 'tmdb')
            if trakt_history:
                boolean = 'remove' if details.get('tmdb_id') in trakt_history else 'add'
                item_history = ListItem(library=self.library, **details)
                item_history.label = 'Remove from Trakt Watched History' if boolean == 'remove' else 'Add to Trakt Watched History'
                item_history.url = {'info': 'details', 'trakt': 'history_{0}'.format(boolean), 'type': self.params.get('type')}
                items.append(item_history)

        # Add refresh cache item
        refresh = ListItem(library=self.library, **details)
        refresh.label = 'Refresh Cache'
        refresh.url = {'info': 'details', 'refresh': 'True', 'type': self.params.get('type')}
        items.append(refresh)

        # Build our container
        self.item_tmdbtype = self.params.get('type')
        self.list_items(items=items, url_tmdb_id=self.params.get('tmdb_id'))

    def list_basedir(self):
        basedir = BASEDIR_PATH.get(self.params.get('info', '')) or BASEDIR_MAIN
        self.start_container()
        for i in basedir:
            for t in i.get('types'):
                url = {'info': i.get('info'), 'type': t} if t else {'info': i.get('info')}
                if not xbmc.getCondVisibility("Window.IsMedia"):
                    url['widget'] = 'True'
                listitem = ListItem(label=i.get('name').format(utils.type_convert(t, 'plural')), icon=i.get('icon', '').format(self.addonpath))
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
        elif self.params.get('info') == 'textviewer':
            self.textviewer(xbmc.getInfoLabel('ListItem.Label'), xbmc.getInfoLabel('ListItem.Plot'))
        elif self.params.get('info') == 'imageviewer':
            self.imageviewer(xbmc.getInfoLabel('ListItem.Icon'))
        elif self.params.get('info') in ['details', 'refresh']:
            self.list_getid()
            self.list_traktmanagement()
            self.list_details()
        elif self.params.get('info') == 'discover':
            self.translate_discover()
            self.list_tmdb()
        elif self.params.get('info') in ['cast', 'crew']:
            self.list_getid()
            self.list_credits(self.params.get('info'))
        elif self.params.get('info') == 'search':
            self.list_search()
        elif self.params.get('info') in TMDB_LISTS:
            self.list_getid()
            self.list_tmdb()
        elif self.params.get('info') in ['trakt_inprogress', 'trakt_history', 'trakt_mostwatched']:
            self.list_trakthistory()
        elif self.params.get('info') == 'trakt_upnext':
            self.list_getid()
            self.list_traktupnext()
        elif self.params.get('info') == 'trakt_calendar':
            self.list_traktcalendar()
        elif self.params.get('info') in ['trakt_mylists', 'trakt_trendinglists', 'trakt_popularlists', 'trakt_likedlists', 'trakt_inlists']:
            self.list_traktuserlists()
        elif self.params.get('info') in TRAKT_LISTS:
            self.list_trakt()
        elif not self.params or self.params.get('info') in BASEDIR_PATH:
            self.list_basedir()
