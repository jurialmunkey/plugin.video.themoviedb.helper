import sys
import xbmc
import xbmcgui
import xbmcplugin
import datetime
import random
import resources.lib.utils as utils
import resources.lib.constants as constants
from resources.lib.traktapi import TraktAPI
from resources.lib.listitem import ListItem
from resources.lib.plugin import Plugin
try:
    from urllib.parse import parse_qsl  # Py3
except ImportError:
    from urlparse import parse_qsl  # Py2


class Container(Plugin):
    def __init__(self):
        super(Container, self).__init__()
        self.handle = int(sys.argv[1])
        self.paramstring = utils.try_decode_string(sys.argv[2][1:])
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
        self.check_sync = False
        self.randomlist = []
        self.numitems_dbid = 0
        self.numitems_tmdb = 0
        self.trakt_limit = 20 if self.addon.getSettingBool('trakt_extendlimit') else 10

    def start_container(self):
        xbmcplugin.setPluginCategory(self.handle, self.plugincategory)  # Container.PluginCategory
        xbmcplugin.setContent(self.handle, self.containercontent)  # Container.Content

    def finish_container(self):
        if self.params.get('random'):
            return
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_LASTPLAYED)
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_PLAYCOUNT)
        xbmcplugin.endOfDirectory(self.handle, updateListing=self.updatelisting)

    def set_url_params(self, url):
        if self.params.get('widget'):
            url['widget'] = self.params.get('widget')
        if self.params.get('fanarttv'):
            url['fanarttv'] = self.params.get('fanarttv')
        if self.params.get('nextpage'):
            url['nextpage'] = self.params.get('nextpage')
        return url

    def exp_fanarttv(self):
        if self.params.get('fanarttv', '').capitalize() == 'False':
            return False
        if self.params.get('fanarttv', '').capitalize() == 'True':
            return True
        if self.addon.getSettingBool('widget_fanarttv_lookup') and self.params.get('widget', '').capitalize() == 'True':
            return True

    def translate_discover(self):
        lookup_keyword = None if self.params.get('with_id') and self.params.get('with_id') != 'False' else 'keyword'
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

        if self.params.get('with_keywords'):
            self.params['with_keywords'] = self.tmdb.get_translated_list(
                utils.split_items(self.params.get('with_keywords')),
                lookup_keyword,
                separator=self.params.get('with_separator'))

        if self.params.get('without_keywords'):
            self.params['without_keywords'] = self.tmdb.get_translated_list(
                utils.split_items(self.params.get('without_keywords')),
                lookup_keyword,
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

    def get_trakt_watched(self):
        if not self.addon.getSettingBool('trakt_watchedindicators'):
            return
        if self.item_dbtype == 'movie':
            return TraktAPI().get_watched('movie')
        if self.item_dbtype == 'episode':
            return TraktAPI().get_watched('show')

    def get_trakt_unwatched(self):
        if not self.addon.getSettingBool('trakt_unwatchedcounts') or not self.addon.getSettingBool('trakt_watchedindicators') or self.item_dbtype not in ['season', 'tvshow']:
            return -1
        traktapi = TraktAPI(tmdb=self.tmdb)
        self.check_sync = traktapi.sync_activities('shows', 'watched_at')
        if self.item_dbtype == 'season':
            return traktapi.get_unwatched_progress(tmdb_id=self.params.get('tmdb_id'), imdb_id=self.params.get('imdb_id'))
        if self.item_dbtype == 'tvshow':
            return

    def get_sortedlist(self, items):
        if not items:
            return

        added, dbiditems, tmdbitems, lastitems, firstitems, nextpage = [], [], [], [], [], []
        mixed_movies, mixed_tvshows = 0, 0

        if self.item_tmdbtype in ['season', 'episode'] and self.params.get('tmdb_id'):
            if not self.details_tv:
                self.details_tv = self.tmdb.get_detailed_item('tv', self.params.get('tmdb_id'), season=self.params.get('season', None))
            if self.fanarttv and self.details_tv and self.exp_fanarttv():
                tvdb_id = self.tmdb.get_item_externalid('tv', self.params.get('tmdb_id'), 'tvdb_id')
                artwork = self.fanarttv.get_tvshow_allart_lc(tvdb_id)
                self.details_tv['poster'] = artwork.get('poster')
                self.details_tv['clearart'] = artwork.get('clearart')
                self.details_tv['clearlogo'] = artwork.get('clearlogo')
                self.details_tv['landscape'] = artwork.get('landscape')
                self.details_tv['banner'] = artwork.get('banner')
                self.details_tv['fanart'] = self.details_tv.get('fanart') or artwork.get('fanart')

        if self.item_tmdbtype == 'season' and self.details_tv:
            item_upnext = ListItem(library=self.library, **self.details_tv)
            item_upnext.infolabels['season'] = self.addon.getLocalizedString(32043)
            item_upnext.label = self.addon.getLocalizedString(32043)
            item_upnext.url = {'info': 'trakt_upnext', 'type': 'tv'}
            items.append(item_upnext)

        for i in items:
            if i.nextpage:
                i.url = self.params.copy()
                i.url['page'] = i.nextpage
                i.icon = '{0}/resources/icons/tmdb/nextpage.png'.format(self.addonpath)
                if self.params.get('nextpage'):
                    nextpage.append(i)
                continue

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
                i.cast = self.details_tv.get('cast', []) + i.cast
                i.infolabels = utils.merge_two_dicts(self.details_tv.get('infolabels', {}), i.infolabels)
                i.infoproperties = utils.merge_two_dicts(self.details_tv.get('infoproperties', {}), i.infoproperties)
                i.poster = i.poster or self.details_tv.get('poster')
                i.fanart = i.fanart if i.fanart and i.fanart != '{0}/fanart.jpg'.format(self.addonpath) else self.details_tv.get('fanart')
                i.tvshow_clearart = i.tvshow_clearart or self.details_tv.get('clearart')
                i.tvshow_clearlogo = i.tvshow_clearlogo or self.details_tv.get('clearlogo')
                i.tvshow_landscape = i.tvshow_landscape or self.details_tv.get('landscape')
                i.tvshow_banner = i.tvshow_banner or self.details_tv.get('banner')
                i.tvshow_poster = self.details_tv.get('poster') or i.poster
                i.infolabels['season'] = season_num

            # Format label For Future Eps/Movies
            if i.infolabels.get('premiered'):
                # Don't format label for plugin methods specifically about the future or details/seasons
                if self.params.get('info') not in ['details', 'seasons', 'trakt_calendar', 'trakt_myairing', 'trakt_anticipated']:
                    try:
                        if utils.convert_timestamp(i.infolabels.get('premiered'), "%Y-%m-%d", 10) > datetime.datetime.now():
                            i.label = '[COLOR=ffcc0000][I]{}[/I][/COLOR]'.format(i.label)
                            # Don't add if option enabled to hide
                            if self.addon.getSettingBool('hide_unaired'):
                                continue
                    except Exception as exc:
                        utils.kodi_log('Error: {}'.format(exc), 1)

            i.dbid = self.get_db_info(
                info='dbid', tmdbtype=self.item_tmdbtype, imdb_id=i.imdb_id,
                originaltitle=i.infolabels.get('originaltitle'), title=i.infolabels.get('title'), year=i.infolabels.get('year'),
                tvshowtitle=i.infolabels.get('tvshowtitle'), season=i.infolabels.get('season'), episode=i.infolabels.get('episode'))

            i.infoproperties['widget'] = self.plugincategory

            if self.item_tmdbtype == 'season' and i.infolabels.get('season') == 0:
                lastitems.append(i)
            elif self.item_tmdbtype == 'season' and i.infolabels.get('season') == self.addon.getLocalizedString(32043):
                firstitems.append(i)
            elif i.dbid:
                dbiditems.append(i)
            else:
                tmdbitems.append(i)

        if mixed_movies or mixed_tvshows:
            self.mixed_containercontent = 'tvshows' if mixed_tvshows > mixed_movies else 'movies'

        self.numitems_dbid = len(dbiditems) or 0
        self.numitems_tmdb = len(tmdbitems) or 0
        xbmcplugin.setProperty(self.handle, 'NumItems.DBID', str(self.numitems_dbid))
        xbmcplugin.setProperty(self.handle, 'NumItems.TMDB', str(self.numitems_tmdb))

        return firstitems + dbiditems + tmdbitems + lastitems + nextpage

    def get_userdiscover_listitems(self, basedir=False):
        basedir = constants.USER_DISCOVER_LISTITEMS_BASEDIR if basedir else []
        if self.params.get('type') == 'movie':
            return basedir + constants.USER_DISCOVER_LISTITEMS_MOVIES
        return basedir + constants.USER_DISCOVER_LISTITEMS_TVSHOWS

    def get_userdiscover_sortmethods(self):
        if self.params.get('type') == 'movie':
            return constants.USER_DISCOVER_SORTBY_MOVIES
        return constants.USER_DISCOVER_SORTBY_TVSHOWS

    def get_userdiscover_prop(self, name, prefix=None, **kwargs):
        prefix = 'TMDbHelper.UserDiscover.{}'.format(prefix) if prefix else 'TMDbHelper.UserDiscover'
        return utils.get_property(name, prefix=prefix, **kwargs)

    def get_userdiscover_folderpath_url(self):
        url = {'info': 'discover', 'type': self.params.get('type'), 'with_id': 'True'}
        for i in self.get_userdiscover_listitems(basedir=True):
            k = i.get('url', {}).get('method')
            v = self.get_userdiscover_prop(k)
            if not k or not v:
                continue
            url[k] = v
        return url

    def get_userdiscover_url(self, url, label=None):
        if url.get('method') == 'open':
            return self.get_userdiscover_folderpath_url()
        if label:
            url['label'] = label
        url['type'] = self.params.get('type')
        return url

    def clear_userdiscover_properties(self):
        for i in self.get_userdiscover_listitems(basedir=True):
            name = i.get('url', {}).get('method')
            self.get_userdiscover_prop(name, clearproperty=True)
            self.get_userdiscover_prop(name, 'Label', clearproperty=True)

    def add_userdiscover_method_property(self, header, tmdbtype, usedetails, old_label=None, old_value=None):
        if old_label and old_value:
            if xbmcgui.Dialog().yesno(
                    '{} Exists'.format(tmdbtype.capitalize()),
                    'A value has already been set for this parameter:', old_label,
                    'Do you wish to clear the existing items or add more?',
                    yeslabel='Clear Items', nolabel='Add Items'):
                return
            self.new_property_label = old_label
            self.new_property_value = old_value

        new_label = xbmcgui.Dialog().input(header)
        if not new_label:
            return

        new_value = self.tmdb.get_tmdb_id(
            tmdbtype, query=new_label, selectdialog=True, longcache=True, usedetails=usedetails, returntuple=True)
        if not new_value:
            if xbmcgui.Dialog().yesno('No Value Added', 'TMDb ID for {} not found or none selected.\nDo you want to add another value?'.format(new_label)):
                self.add_userdiscover_method_property(header, tmdbtype, usedetails)
            return

        new_value = (utils.try_encode_string(new_value[0]), new_value[1])
        self.new_property_label = '{0} / {1}'.format(self.new_property_label, new_value[0]) if self.new_property_label else new_value[0]
        self.new_property_value = '{0} / {1}'.format(self.new_property_value, new_value[1]) if self.new_property_value else '{}'.format(new_value[1])
        if xbmcgui.Dialog().yesno('Added {}'.format(new_value[0]), '{}\nDo you want to add another value?'.format(self.new_property_label)):
            self.add_userdiscover_method_property(header, tmdbtype, usedetails)

    def set_userdiscover_separator_property(self):
        choice = xbmcgui.Dialog().yesno(
            'Set Match Method',
            'Choose matching method for parameters with multiple values.',
            yeslabel='Match ANY Value', nolabel='Match ALL Values')
        self.new_property_value = 'OR' if choice else 'AND'
        self.new_property_label = 'ANY' if choice else 'ALL'

    def set_userdiscover_genre_property(self):
        genres_list = self.tmdb.get_request_lc('genre', self.params.get('type'), 'list')
        if not genres_list:
            return
        genres_list = genres_list.get('genres', [])
        dialog_list = [i.get('name') for i in genres_list]
        select_list = xbmcgui.Dialog().multiselect('Select Genres', dialog_list)
        if not select_list:
            return
        for i in select_list:
            label = genres_list[i].get('name')
            value = genres_list[i].get('id')
            if not value:
                continue
            self.new_property_label = '{0} / {1}'.format(self.new_property_label, label) if self.new_property_label else label
            self.new_property_value = '{0} / {1}'.format(self.new_property_value, value) if self.new_property_value else '{}'.format(value)

    def set_userdiscover_method_property(self):
        method = self.params.get('method')

        # Set Input Method
        affix = ''
        header = 'Search for '
        usedetails = False
        label = self.params.get('label')
        tmdbtype = self.params.get('type')
        inputtype = xbmcgui.INPUT_ALPHANUM
        if any(i in method for i in ['year', 'vote_', '_runtime', '_networks']):
            header = 'Enter '
            inputtype = xbmcgui.INPUT_NUMERIC
        elif '_date' in method:
            header = 'Enter '
            affix = ' YYYY-MM-DD'
        elif '_genres' in method:
            label = 'Genre'
            tmdbtype = 'genre'
        elif '_companies' in method:
            label = 'Company'
            tmdbtype = 'company'
        elif '_networks' in method:
            label = 'Network'
            tmdbtype = 'company'
        elif '_keywords' in method:
            label = 'Keyword'
            tmdbtype = 'keyword'
        elif any(i in method for i in ['_cast', '_crew', '_people']):
            label = 'Person'
            tmdbtype = 'person'
            usedetails = True
        header = '{0}{1}{2}'.format(header, label, affix)
        old_value = self.get_userdiscover_prop(method) or None
        old_label = self.get_userdiscover_prop(method, 'Label') or None

        # Route Method
        if method == 'with_separator':
            self.set_userdiscover_separator_property()
        elif '_genres' in method:
            self.set_userdiscover_genre_property()
        elif 'with_runtime' not in method and 'with_networks' not in method and any(i in method for i in ['with_', 'without_']):
            self.add_userdiscover_method_property(header, tmdbtype, usedetails, old_label=old_label, old_value=old_value)
        else:
            self.new_property_label = self.new_property_value = xbmcgui.Dialog().input(
                header, type=inputtype, defaultt=old_value)

    def set_userdiscover_sortby_property(self):
        sort_method_list = self.get_userdiscover_sortmethods()
        sort_method = xbmcgui.Dialog().select('Select Sort Method', sort_method_list)
        self.new_property_label = self.new_property_value = sort_method_list[sort_method] if sort_method > -1 else None

    def get_userdiscover_affix(self, method):
        if self.params.get('method') == method:
            return self.new_property_label
        return self.get_userdiscover_prop(method, 'Label')

    def get_userdiscover_label(self, label, method):
        append_label = self.get_userdiscover_affix(method)
        label = label.format(utils.type_convert(self.params.get('type'), 'plural'))
        return '{0}: {1}'.format(label, append_label) if append_label else label

    def list_userdiscover_build(self, items, skipnull=False):
        for i in items:
            i = ListItem(library=self.library, **i)
            i.url = self.get_userdiscover_url(i.url, i.label)
            i.label = self.get_userdiscover_label(i.label, i.url.get('method'))
            i.create_listitem(self.handle, **i.url) if not skipnull or self.get_userdiscover_affix(i.url.get('method')) else None

    def list_userdiscover_dialog(self):
        urls = []
        dialogitems = []
        for i in self.get_userdiscover_listitems():
            i = ListItem(library=self.library, **i)
            i.url = self.get_userdiscover_url(i.url, i.label)
            i.label = self.get_userdiscover_label(i.label, i.url.get('method'))
            urls.append(i.url)
            dialogitems.append(i.set_listitem())
        idx = xbmcgui.Dialog().select('Add Rule', dialogitems)
        if idx == -1:
            return
        self.params = urls[idx]
        self.router()

    def list_userdiscover(self):
        self.updatelisting = True if self.params.get('method') else False
        self.new_property_label = self.new_property_value = None

        # Route Method
        if not self.params.get('method') or self.params.get('method') == 'clear':
            self.clear_userdiscover_properties()
        elif self.params.get('method') == 'sort_by':
            self.set_userdiscover_sortby_property()
        elif self.params.get('method') == 'add_rule':
            return self.list_userdiscover_dialog()
        else:
            self.set_userdiscover_method_property()

        # Set / Clear Property
        if self.new_property_value:
            self.get_userdiscover_prop(self.params.get('method'), setproperty=self.new_property_value)
            self.get_userdiscover_prop(self.params.get('method'), 'Label', setproperty=self.new_property_label)
        else:
            self.get_userdiscover_prop(self.params.get('method'), clearproperty=True)
            self.get_userdiscover_prop(self.params.get('method'), 'Label', clearproperty=True)

        # Build Container
        self.containercontent = 'files'
        self.start_container()
        self.list_userdiscover_build(constants.USER_DISCOVER_LISTITEMS_BASEDIR)
        self.list_userdiscover_build(self.get_userdiscover_listitems(basedir=False), skipnull=True)
        self.list_userdiscover_build(constants.USER_DISCOVER_LISTITEMS_ADDRULE)
        self.finish_container()

    def list_trakthistory(self):
        traktapi = TraktAPI(tmdb=self.tmdb)
        userslug = traktapi.get_usernameslug(login=True)
        self.item_tmdbtype = self.params.get('type')
        if self.params.get('info') == 'trakt_nextepisodes':
            items = traktapi.get_inprogress(userslug, limit=self.trakt_limit, episodes=True)
            self.item_tmdbtype = 'episode'
        elif self.params.get('info') == 'trakt_inprogress':
            items = traktapi.get_inprogress(userslug, limit=self.trakt_limit)
        elif self.params.get('info') == 'trakt_mostwatched':
            items = traktapi.get_mostwatched(userslug, self.params.get('type'), limit=self.trakt_limit)
        elif self.params.get('info') == 'trakt_history':
            items = traktapi.get_recentlywatched(userslug, self.params.get('type'), limit=self.trakt_limit)
        self.list_items(
            items=items, url={
                'info': 'trakt_upnext' if self.params.get('info') == 'trakt_inprogress' else 'details',
                'type': self.item_tmdbtype})

    def list_traktupnext(self):
        self.item_tmdbtype = 'episode'
        self.list_items(
            items=TraktAPI(tmdb=self.tmdb).get_upnext_episodes(tmdb_id=self.params.get('tmdb_id')),
            url_tmdb_id=self.params.get('tmdb_id'),
            url={'info': 'details', 'type': 'episode'})

    def list_traktcalendar_episodes(self):
        self.item_tmdbtype = 'episode'
        self.list_items(
            items=TraktAPI(tmdb=self.tmdb, login=True).get_calendar_episodes(
                days=utils.try_parse_int(self.params.get('days')),
                startdate=utils.try_parse_int(self.params.get('startdate'))),
            url={'info': 'details', 'type': 'episode'})

    def list_traktcalendar(self):
        if self.params.get('type') == 'episode':
            self.list_traktcalendar_episodes()
            return

        icon = '{0}/resources/trakt.png'.format(self.addonpath)
        self.start_container()
        for i in constants.TRAKT_CALENDAR:
            date = datetime.datetime.today() + datetime.timedelta(days=i[1])
            label = i[0].format(date.strftime('%A'))
            listitem = ListItem(label=label, icon=icon)
            url = {'info': 'trakt_calendar', 'type': 'episode', 'startdate': i[1], 'days': i[2]}
            url = self.set_url_params(url)
            listitem.create_listitem(self.handle, **url)
        self.finish_container()

    def list_traktuserlists(self):
        cat = constants.TRAKT_LISTS.get(self.params.get('info'), {})
        path = cat.get('path', '')
        traktapi = TraktAPI(login=cat.get('req_auth', False))
        if '{user_slug}' in path:
            self.params['user_slug'] = self.params.get('user_slug') or traktapi.get_usernameslug()
        path = path.format(**self.params)
        icon = '{0}/resources/trakt.png'.format(self.addonpath)

        self.start_container()
        for i in traktapi.get_response_json(path, limit=250):
            if not i:
                continue
            i = i.get('list') or i
            label = i.get('name')
            label2 = i.get('user', {}).get('name')
            infolabels = {}
            infolabels['plot'] = i.get('description')
            infolabels['rating'] = i.get('likes')
            list_slug = i.get('ids', {}).get('slug')
            user_slug = i.get('user', {}).get('ids', {}).get('slug')
            listitem = ListItem(label=label, label2=label2, icon=icon, thumb=icon, poster=icon, infolabels=infolabels)
            url = {'info': 'trakt_userlist', 'user_slug': user_slug, 'list_slug': list_slug, 'type': self.params.get('type')}
            listitem.url = self.set_url_params(url)
            listitem.create_listitem(self.handle, **listitem.url) if not self.params.get('random') else self.randomlist.append(listitem)
        self.finish_container()

    def list_traktcollection(self):
        items = []
        if self.params.get('type') in ['movie', 'tv']:
            items = TraktAPI(tmdb=self.tmdb, login=True).get_collection(
                self.params.get('type'), utils.try_parse_int(self.params.get('page', 1)))
        self.item_tmdbtype = self.params.get('type')
        self.list_items(items, url={'info': 'details', 'type': self.item_tmdbtype})

    def list_trakt(self):
        if not self.params.get('type'):
            return

        cat = constants.TRAKT_LISTS.get(self.params.get('info', ''), {})
        traktapi = TraktAPI(tmdb=self.tmdb, login=cat.get('req_auth', False))

        if '{user_slug}' in cat.get('path', ''):
            self.params['user_slug'] = self.params.get('user_slug') or traktapi.get_usernameslug(login=True)

        self.item_tmdbtype = 'movie' if self.params.get('type') == 'both' else self.params.get('type', '')

        params = self.params.copy()
        params['type'] = utils.type_convert(self.item_tmdbtype, 'trakt') + 's'

        (limit, rnd_list) = (50, self.trakt_limit) if self.params.pop('random', False) else (self.trakt_limit, None)

        self.list_items(
            items=traktapi.get_itemlist(
                cat.get('path', '').format(**params), page=self.params.get('page', 1), limit=limit, rnd_list=rnd_list, req_auth=cat.get('req_auth'),
                key_list=['movie', 'show'] if self.params.get('type') == 'both' else [utils.type_convert(self.item_tmdbtype, 'trakt')]),
            url={'info': cat.get('url_info', 'details')})

    def list_traktmanagement(self):
        if not self.params.get('trakt') in constants.TRAKT_MANAGEMENT:
            return
        with utils.busy_dialog():
            traktapi = TraktAPI()
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

    def list_becauseyouwatched(self, mostwatched=False):
        traktapi = TraktAPI(tmdb=self.tmdb, login=True)
        userslug = traktapi.get_usernameslug()
        if not userslug:
            return
        func = traktapi.get_mostwatched if mostwatched else traktapi.get_recentlywatched
        recentitems = func(userslug, self.params.get('type'), limit=5, islistitem=False)
        recentitem = recentitems[random.randint(0, len(recentitems) - 1)]
        if not recentitem[1]:
            return
        self.plugincategory = recentitem[2]
        self.params['tmdb_id'] = recentitem[1]
        self.params['info'] = 'recommendations'
        self.list_tmdb()

    def list_getid(self):
        params = self.params.copy()
        if self.params.get('info') == 'play' and self.params.get('type') == 'episode':
            params['type'] = 'tv'
        self.params['tmdb_id'] = self.get_tmdb_id(**params)

    def list_play(self):
        if not self.params.get('type') or not self.params.get('tmdb_id'):
            return
        season, episode = self.params.get('season'), self.params.get('episode')
        command = 'RunScript(plugin.video.themoviedb.helper,play={0},tmdb_id={1}{{0}})'.format(self.params.get('type'), self.params.get('tmdb_id'))
        command = command.format(',season={0},episode={1}'.format(season, episode) if season and episode else '')
        xbmc.executebuiltin(command)
        if not self.params.get('widget') and not self.params.get('nextpage'):
            xbmcplugin.setResolvedUrl(self.handle, True, ListItem().set_listitem())

    def list_search(self):
        if not self.params.get('query'):
            self.params['query'] = xbmcgui.Dialog().input(self.addon.getLocalizedString(32044), type=xbmcgui.INPUT_ALPHANUM)
        if self.params.get('query'):
            self.list_tmdb(query=self.params.get('query'), year=self.params.get('year'))

    def list_items(self, items=None, url=None, url_tmdb_id=None):
        """
        Sort listitems and then display
        url= for listitem base folderpath url params
        url_tmdb_id= for listitem tmdb_id used in url
        """
        items = self.get_sortedlist(items)

        if not items:
            return

        self.item_dbtype = utils.type_convert(self.item_tmdbtype, 'dbtype')
        self.containercontent = self.mixed_containercontent or utils.type_convert(self.item_tmdbtype, 'container')

        trakt_watched = self.get_trakt_watched()
        trakt_unwatched = self.get_trakt_unwatched()

        x = 0
        self.start_container()
        for i in items:
            i.label2 = i.infoproperties.get('role') or i.label2
            i.infoproperties['numitems.dbid'] = self.numitems_dbid
            i.infoproperties['numitems.tmdb'] = self.numitems_tmdb
            i.get_details(self.item_dbtype, self.tmdb, self.omdb, self.params.get('localdb'))
            i.get_url(url, url_tmdb_id, self.params.get('widget'), self.params.get('fanarttv'), self.params.get('nextpage'), self.params.get('extended'))
            i.get_extra_artwork(self.tmdb, self.fanarttv) if len(items) < 22 and self.exp_fanarttv() else None
            i.get_trakt_watched(trakt_watched) if x == 0 or self.params.get('info') != 'details' else None
            i.get_trakt_unwatched(trakt=TraktAPI(tmdb=self.tmdb), request=trakt_unwatched, check_sync=self.check_sync) if x == 0 or self.params.get('info') != 'details' else None
            i.create_listitem(self.handle, **i.url) if not self.params.get('random') else self.randomlist.append(i)
            x += 1
        self.finish_container()

    def list_tmdb(self, *args, **kwargs):
        if not self.params.get('type'):
            return

        # Construct request
        cat = constants.TMDB_LISTS.get(self.params.get('info'), {})
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
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(32045), self.addon.getLocalizedString(32046))
            self.updatelisting = True

        # Get details of item and return if nothing found
        details = self.tmdb.get_detailed_item(*d_args)
        if not details:
            return

        # Merge OMDb rating details for movies
        if self.params.get('type') == 'movie':
            details = self.get_omdb_ratings(details, cache_only=False)

        # Merge library stats for person
        if self.params.get('type') == 'person':
            details = self.get_kodi_person_stats(details)

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
        for i in constants.DETAILED_CATEGORIES:
            if self.params.get('type') in i.get('types'):
                item = ListItem(library=self.library, **details)
                item.label = i.get('name')
                item.url = {'info': i.get('info'), 'type': self.params.get('type')}
                if i.get('url_key') and details.get(i.get('url_key')):
                    item.url[i.get('url_key')] = details.get(i.get('url_key'))
                if i.get('icon'):
                    item.poster = item.icon = i.get('icon', '').format(self.addonpath)
                items.append(item)

        # Add trakt management items if &amp;manage=True
        if self.addon.getSettingBool('trakt_management'):
            traktapi = TraktAPI()
            trakt_collection = traktapi.sync_collection(utils.type_convert(self.params.get('type'), 'trakt'), 'tmdb')
            if trakt_collection:
                boolean = 'remove' if details.get('tmdb_id') in trakt_collection else 'add'
                item_collection = ListItem(library=self.library, **details)
                item_collection.label = self.addon.getLocalizedString(32047) if boolean == 'remove' else self.addon.getLocalizedString(32048)
                item_collection.url = {'info': 'details', 'trakt': 'collection_{0}'.format(boolean), 'type': self.params.get('type')}
                items.append(item_collection)
            trakt_watchlist = traktapi.sync_watchlist(utils.type_convert(self.params.get('type'), 'trakt'), 'tmdb')
            if trakt_watchlist:
                boolean = 'remove' if details.get('tmdb_id') in trakt_watchlist else 'add'
                item_watchlist = ListItem(library=self.library, **details)
                item_watchlist.label = self.addon.getLocalizedString(32049) if boolean == 'remove' else self.addon.getLocalizedString(32050)
                item_watchlist.url = {'info': 'details', 'trakt': 'watchlist_{0}'.format(boolean), 'type': self.params.get('type')}
                items.append(item_watchlist)
            trakt_history = traktapi.sync_history(utils.type_convert(self.params.get('type'), 'trakt'), 'tmdb')
            if trakt_history:
                boolean = 'remove' if details.get('tmdb_id') in trakt_history else 'add'
                item_history = ListItem(library=self.library, **details)
                item_history.label = self.addon.getLocalizedString(32051) if boolean == 'remove' else self.addon.getLocalizedString(32052)
                item_history.url = {'info': 'details', 'trakt': 'history_{0}'.format(boolean), 'type': self.params.get('type')}
                items.append(item_history)

        # Add refresh cache item
        refresh = ListItem(library=self.library, **details)
        refresh.label = self.addon.getLocalizedString(32053)
        refresh.url = {'info': 'details', 'refresh': 'True', 'type': self.params.get('type')}
        refresh.poster = refresh.icon = '{0}/resources/icons/tmdb/refresh.png'.format(self.addonpath)
        items.append(refresh)

        # Build our container
        self.item_tmdbtype = self.params.get('type')
        self.list_items(items=items, url_tmdb_id=self.params.get('tmdb_id'))

    def list_traktrandom(self):
        self.params['info'] = constants.RANDOM_TRAKT.get(self.params.get('info'), {})
        self.params['random'] = True
        self.router()

    def list_random(self):
        self.params['info'] = constants.RANDOM_LISTS.get(self.params.get('info'), {})
        self.params['random'] = True
        self.router()
        if not self.randomlist:
            return
        index = 0
        if len(self.randomlist) > 1:
            index = random.randint(0, len(self.randomlist) - 1)
        item = self.randomlist[index]
        self.plugincategory = item.label
        self.params = item.url
        self.router()

    def list_basedir(self):
        cat = constants.BASEDIR_PATH.get(self.params.get('info'), {})
        basedir = cat.get('folders', [constants.BASEDIR_MAIN])
        types = cat.get('types', [None])
        self.start_container()
        for folder in basedir:
            for i in folder:
                for t in types:
                    if t not in i.get('types', [None]):
                        continue
                    url = {'info': i.get('info'), 'type': t} if t else {'info': i.get('info')}

                    if not xbmc.getCondVisibility("Window.IsMedia"):
                        url['widget'] = 'True'

                    if self.fanarttv and xbmc.getCondVisibility("Window.IsMedia"):
                        url['fanarttv'] = 'True'

                    if xbmc.getCondVisibility("Window.IsMedia"):
                        url['nextpage'] = 'True'

                    label = i.get('name').format('', '') if self.params.get('info') in ['dir_movie', 'dir_tv', 'dir_person'] else i.get('name').format(utils.type_convert(t, 'plural'), ' ')

                    listitem = ListItem(label=label, icon=i.get('icon', '').format(self.addonpath))
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
        elif self.params.get('info') in constants.RANDOM_LISTS:
            self.list_random()
        elif self.params.get('info') in constants.RANDOM_TRAKT:
            self.list_traktrandom()
        elif self.params.get('info') == 'user_discover':
            self.list_userdiscover()
        elif self.params.get('info') == 'discover':
            self.translate_discover()
            self.list_tmdb()
        elif self.params.get('info') in ['cast', 'crew']:
            self.list_getid()
            self.list_credits(self.params.get('info'))
        elif self.params.get('info') == 'search':
            self.list_search()
        elif self.params.get('info') == 'trakt_becauseyouwatched':
            self.list_becauseyouwatched()
        elif self.params.get('info') == 'trakt_becausemostwatched':
            self.list_becauseyouwatched(mostwatched=True)
        elif self.params.get('info') in constants.TMDB_LISTS:
            self.list_getid()
            self.list_tmdb()
        elif self.params.get('info') in constants.TRAKT_HISTORY:
            self.list_trakthistory()
        elif self.params.get('info') == 'trakt_upnext':
            self.list_getid()
            self.list_traktupnext()
        elif self.params.get('info') == 'trakt_calendar':
            self.list_traktcalendar()
        elif self.params.get('info') == 'trakt_collection':
            self.list_traktcollection()
        elif self.params.get('info') in constants.TRAKT_USERLISTS:
            self.list_traktuserlists()
        elif self.params.get('info') in constants.TRAKT_LISTS:
            self.list_trakt()
        elif not self.params or self.params.get('info') in constants.BASEDIR_PATH:
            self.list_basedir()
