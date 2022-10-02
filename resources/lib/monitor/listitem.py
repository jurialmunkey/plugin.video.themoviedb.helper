import xbmcgui
from resources.lib.api.kodi.rpc import get_person_stats
from resources.lib.addon.window import get_property, get_current_window
from resources.lib.monitor.common import CommonMonitorFunctions, SETMAIN_ARTWORK, SETPROP_RATINGS
from resources.lib.monitor.images import ImageFunctions
from resources.lib.addon.plugin import convert_media_type, get_setting, get_infolabel, get_condvisibility, get_localized
from resources.lib.addon.logger import kodi_try_except
from resources.lib.files.bcache import BasicCache
from resources.lib.items.listitem import ListItem
from resources.lib.addon.tmdate import convert_timestamp, get_region_date
from resources.lib.api.mapping import get_empty_item
from threading import Thread
from copy import deepcopy
from collections import namedtuple


BASEITEM_PROPERTIES = [
    ('base_label', ('label',)),
    ('base_title', ('title',)),
    ('base_icon', ('icon',)),
    ('base_plot', ('plot', 'Property(artist_description)', 'Property(artist_description)', 'addondescription')),
    ('base_tagline', ('tagline',)),
    ('base_dbtype', ('dbtype',)),
    ('base_poster', ('Art(poster)',)),
    ('base_clearlogo', ('Art(clearlogo)', 'Art(tvshow.clearlogo)', 'Art(artist.clearlogo)')),
    ('base_tvshowtitle', ('tvshowtitle',))]
ItemDetails = namedtuple("ItemDetails", "tmdb_type tmdb_id listitem artwork")

CV_USE_LOCALWIDGETPROP = 'Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer)'
CV_GET_WIDGETCONTAINER = "Skin.HasSetting(TMDbHelper.ForceWidgetContainer)"\
    " | [!Window.IsVisible(DialogPVRInfo.xml)"\
    " + !Window.IsVisible(MyPVRGuide.xml)"\
    " + !Window.IsVisible(movieinformation)]"
CV_MULTITYPE_LOOKUP = "Window.IsVisible(DialogPVRInfo.xml)"\
    " | Window.IsVisible(MyPVRChannels.xml)"\
    " | Window.IsVisible(MyPVRRecordings.xml)"\
    " | Window.IsVisible(MyPVRSearch.xml)"\
    " | Window.IsVisible(MyPVRGuide.xml)"
CV_PVR_LOOKUPS = "!Skin.HasSetting(TMDbHelper.DisablePVR)"
CV_GET_PERSONSTATS = "!Skin.HasSetting(TMDbHelper.DisablePersonStats)"
CV_GET_RATINGS = "!Skin.HasSetting(TMDbHelper.DisableRatings)"
CV_GET_CROPPED = "Skin.HasSetting(TMDbHelper.EnableCrop)"
CV_GET_BLURRED = "Skin.HasSetting(TMDbHelper.EnableBlur)"
CV_GET_DESATURATED = "Skin.HasSetting(TMDbHelper.EnableDesaturate)"
CV_GET_COLORS = "Skin.HasSetting(TMDbHelper.EnableColors)"
CV_GET_ARTWORK = "!Skin.HasSetting(TMDbHelper.DisableArtwork)"
ArtFunc = namedtuple("ArtFunc", "method condition source fallback")
ARTFUNC_CROP = ArtFunc(
    'crop',
    lambda: get_condvisibility(CV_GET_CROPPED),
    lambda: "Art(artist.clearlogo)|Art(tvshow.clearlogo)|Art(clearlogo)",
    lambda: None)
ARTFUNC_BLUR = ArtFunc(
    'blur',
    lambda: get_condvisibility(CV_GET_BLURRED),
    lambda: get_property('Blur.SourceImage'),
    lambda: get_property('Blur.Fallback'))
ARTFUNC_DESATURATE = ArtFunc(
    'desaturate',
    lambda: get_condvisibility(CV_GET_DESATURATED),
    lambda: get_property('Desaturate.SourceImage'),
    lambda: get_property('Desaturate.Fallback'))
ARTFUNC_COLORS = ArtFunc(
    'colors',
    lambda: get_condvisibility(CV_GET_COLORS),
    lambda: get_property('Colors.SourceImage'),
    lambda: get_property('Colors.Fallback'))
ARTWORK_FUNCTIONS = (
    ARTFUNC_CROP,
    ARTFUNC_BLUR,
    ARTFUNC_DESATURATE,
    ARTFUNC_COLORS)

LISTITEM_READAHEAD = [1, -1, 2, 3, 4, 5, 6]


class ListItemLookup():
    def __init__(self, parent, dbtype, query, season=None, episode=None, imdb_id=None, year=None):
        self._parent = parent
        self._dbtype = dbtype
        self._query = query
        self._season = season
        self._episode = episode
        self._imdb_id = imdb_id if not season and not episode else None  # Difficult to determine if IMDb ID is show or season/episode
        self._year = year
        self._tmdb_id = None
        self._tmdb_type = self.get_tmdb_type()
        self._tmdb_id = self.get_tmdb_id()
        self._itemdetails = ItemDetails(None, None, get_empty_item(), {})
        self._parent.ib.ftv_api = self._parent.ftv_api if get_setting('service_fanarttv_lookup') else None

    @kodi_try_except('lib.monitor.listitem.get_tmdb_type')
    def get_tmdb_type(self):
        if self._dbtype == 'multi':
            return self.get_tmdb_multi()
        return convert_media_type(self._dbtype, 'tmdb', strip_plural=True, parent_type=True)

    @kodi_try_except('lib.monitor.listitem.get_tmdb_multi')
    def get_tmdb_multi(self):
        self._season = self._parent.get_infolabel('season')
        self._episode = self._parent.get_infolabel('episode')
        media_type = 'tv' if self._episode or self._season else None
        multi_item = self._parent.tmdb_api.get_tmdb_multisearch(query=self._query, media_type=media_type)
        if not multi_item or not multi_item.get('id') or not multi_item.get('media_type'):
            return
        self._tmdb_type = multi_item['media_type']
        self._tmdb_id = multi_item['id']
        return self._tmdb_type

    @kodi_try_except('lib.monitor.listitem.get_tmdb_id')
    def get_tmdb_id(self):
        return self._tmdb_id or self._parent.get_tmdb_id(
            tmdb_type=self._tmdb_type,
            query=self._query,
            imdb_id=self._imdb_id,
            year=self._year if self._tmdb_type == 'movie' else None,
            episode_year=self._year if self._tmdb_type == 'tv' else None)

    @kodi_try_except('lib.monitor.listitem.get_artwork')
    def get_artwork(self):
        return self._parent.ib.get_item_artwork(self._itemdetails.artwork, is_season=True if self._season else False)

    @kodi_try_except('lib.monitor.listitem.get_itemdetails')
    def get_itemdetails(self):
        if not self._tmdb_type or not self._tmdb_id:
            return self._itemdetails
        cache_name = f'itemdetails.{self._tmdb_type}.{self._tmdb_id}.{self._season}.{self._episode}'
        self._itemdetails = self._parent._itemcache.get(cache_name) or self._itemdetails
        if self._itemdetails.tmdb_id:
            return self._itemdetails
        details = self._parent.ib.get_item(self._tmdb_type, self._tmdb_id, self._season, self._episode)
        if not details:
            return self._itemdetails
        try:
            self._itemdetails = ItemDetails(self._tmdb_type, self._tmdb_id, details['listitem'], details['artwork'])
        except (KeyError, AttributeError, TypeError):
            return self._itemdetails
        self._parent._itemcache[cache_name] = self._itemdetails
        return self._itemdetails

    @kodi_try_except('lib.monitor.listitem.get_builtitem')
    def get_builtitem(self):
        if not self._itemdetails:
            return

        def set_time_properties(duration):
            minutes = duration // 60 % 60
            hours = duration // 60 // 60
            self._itemdetails.listitem['infoproperties']['Duration'] = duration // 60
            self._itemdetails.listitem['infoproperties']['Duration_H'] = hours
            self._itemdetails.listitem['infoproperties']['Duration_M'] = minutes
            self._itemdetails.listitem['infoproperties']['Duration_HHMM'] = f'{hours:02d}:{minutes:02d}'

        def set_date_properties(premiered):
            date_obj = convert_timestamp(premiered, time_fmt="%Y-%m-%d", time_lim=10)
            if not date_obj:
                return
            self._itemdetails.listitem['infoproperties']['Premiered'] = get_region_date(date_obj, 'dateshort')
            self._itemdetails.listitem['infoproperties']['Premiered_Long'] = get_region_date(date_obj, 'datelong')
            self._itemdetails.listitem['infoproperties']['Premiered_Custom'] = date_obj.strftime(get_infolabel('Skin.String(TMDbHelper.Date.Format)') or '%d %b %Y')

        set_time_properties(self._itemdetails.listitem['infolabels'].get('duration', 0))
        set_date_properties(self._itemdetails.listitem['infolabels'].get('premiered'))

        li = ListItem(**self._itemdetails.listitem)
        li.art = self.get_artwork()
        return li.get_listitem()

    @kodi_try_except('lib.monitor.listitem.get_ratings')
    def get_ratings(self, threaded=False):
        try:
            trakt_type = {'movie': 'movie', 'tv': 'show'}[self._tmdb_type]
        except KeyError:
            return  # Only lookup ratings for movie or tvshow
        cache_name = f'ratings.{self._tmdb_type}.{self._tmdb_id}.{self._season}.{self._episode}'
        details = self._parent._itemcache.get(cache_name)
        if details:
            return details
        details = self._itemdetails.listitem if not threaded else deepcopy(self._itemdetails.listitem)
        details = self._parent.get_omdb_ratings(details)
        details = self._parent.get_imdb_top250_rank(details, trakt_type=trakt_type)
        details = self._parent.get_trakt_ratings(details, trakt_type, season=self._season, episode=self._episode)
        details = self._parent.get_tvdb_awards(details, self._tmdb_type, self._tmdb_id)
        self._parent._itemcache[cache_name] = details
        return details

    @kodi_try_except('lib.monitor.listitem.get_nextaired')
    def get_nextaired(self):
        if self._tmdb_type == 'tv':
            nextaired = self._parent.tmdb_api.get_tvshow_nextaired(self._tmdb_id)
            self._itemdetails.listitem['infoproperties'].update(nextaired)
            return nextaired


class ListItemMonitor(CommonMonitorFunctions):
    def __init__(self):
        super(ListItemMonitor, self).__init__()
        self.property_prefix = 'ListItem'
        self._cur_item = 0
        self._pre_item = 1
        self._cur_folder = None
        self._pre_folder = None
        self._cur_window = 0
        self._pre_window = 1
        self._ignored_labels = ['..', get_localized(33078)]
        self._listcontainer = None
        self._last_listitem = None
        self._readcache = {}
        self._itemcache = {}
        self._cache = BasicCache(filename=f'QuickService.db')

    def get_container(self):

        def _get_container():
            window_id = get_current_window() if get_condvisibility(CV_USE_LOCALWIDGETPROP) else None
            widget_id = get_property('WidgetContainer', window_id=window_id, is_type=int)
            return f'Container({widget_id}).' if widget_id else 'Container.'

        def _get_container_item():
            if not get_condvisibility(CV_GET_WIDGETCONTAINER):
                return 'ListItem.'
            return f'{self.container}ListItem.'

        self.container = _get_container()
        self.container_item = _get_container_item()

    def get_infolabel(self, infolabel):
        return get_infolabel(f'{self.container_item}{infolabel}')

    def get_position(self):
        return get_infolabel(f'{self.container}CurrentItem')

    def get_numitems(self):
        return get_infolabel(f'{self.container}NumItems')

    def get_imdb_id(self):
        imdb_id = self.get_infolabel('UniqueID(imdb)') or self.get_infolabel('IMDBNumber') or ''
        return imdb_id if imdb_id.startswith('tt') else ''

    def get_query(self):
        if self.get_infolabel('TvShowTitle'):
            return self.get_infolabel('TvShowTitle')
        if self.get_infolabel('Title'):
            return self.get_infolabel('Title')
        if self.get_infolabel('Label'):
            return self.get_infolabel('Label')

    def get_season(self):
        if self.dbtype == 'episodes':
            return self.get_infolabel('Season')

    def get_episode(self):
        if self.dbtype == 'episodes':
            return self.get_infolabel('Episode')

    def get_dbtype(self):
        if self.get_infolabel('Property(tmdb_type)') == 'person':
            return 'actors'
        dbtype = self.get_infolabel('dbtype')
        if dbtype:
            return f'{dbtype}s'
        if get_condvisibility(CV_MULTITYPE_LOOKUP):
            return 'multi' if get_condvisibility(CV_PVR_LOOKUPS) else ''
        if self.container == 'Container.':
            return get_infolabel('Container.Content()') or ''
        return ''

    def set_cur_item(self):
        self.dbtype = self.get_dbtype()
        self.dbid = self.get_infolabel('dbid')
        self.imdb_id = self.get_imdb_id()
        self.query = self.get_query()
        self.year = self.get_infolabel('year')
        self.season = self.get_season()
        self.episode = self.get_episode()

    def get_cur_item(self):
        return (
            'current_item',
            self.get_infolabel('dbtype'),
            self.get_infolabel('dbid'),
            self.get_infolabel('IMDBNumber'),
            self.get_infolabel('label'),
            self.get_infolabel('tvshowtitle'),
            self.get_infolabel('year'),
            self.get_infolabel('season'),
            self.get_infolabel('episode'),)

    def is_same_item(self, update=False):
        self._cur_item = self.get_cur_item()
        if self._cur_item == self._pre_item:
            return self._cur_item
        if update:
            self._pre_item = self._cur_item

    def get_cur_folder(self):
        return ('current_folder', self.container, get_infolabel('Container.Content()'), self.get_numitems(),)

    @kodi_try_except('lib.monitor.listitem.is_same_folder')
    def is_same_folder(self, update=True):
        self._cur_folder = self.get_cur_folder()
        if self._cur_folder == self._pre_folder:
            return self._cur_folder
        if update:
            self._pre_folder = self._cur_folder

    @kodi_try_except('lib.monitor.listitem.clear_properties')
    def clear_properties(self, ignore_keys=None):
        if not self.get_artwork(source="Art(artist.clearlogo)|Art(tvshow.clearlogo)|Art(clearlogo)"):
            self.properties.update({'CropImage', 'CropImage.Original'})
        super().clear_properties(ignore_keys=ignore_keys)

    @kodi_try_except('lib.monitor.listitem.clear_on_scroll')
    def clear_on_scroll(self):
        self._cur_window = get_current_window()
        self._listcontainer = self.get_listcontainer()
        if self._listcontainer:
            return self.get_listitem()

        if not self.properties and not self.index_properties:
            return
        if self.is_same_item():
            return
        ignore_keys = None
        if self.dbtype in ['episodes', 'seasons']:
            ignore_keys = SETMAIN_ARTWORK
        self.clear_properties(ignore_keys=ignore_keys)

    @kodi_try_except('lib.monitor.listitem.get_artwork')
    def get_artwork(self, source='', fallback=''):
        source = source.lower()
        lookup = {
            'poster': ['Art(tvshow.poster)', 'Art(poster)', 'Art(thumb)'],
            'fanart': ['Art(fanart)', 'Art(thumb)'],
            'landscape': ['Art(landscape)', 'Art(fanart)', 'Art(thumb)'],
            'thumb': ['Art(thumb)']}
        infolabels = lookup.get(source, source.split("|") if source else lookup.get('thumb'))
        for i in infolabels:
            artwork = self.get_infolabel(i)
            if artwork:
                return artwork
        return fallback

    @kodi_try_except('lib.monitor.listitem.blur_fallback')
    def blur_fallback(self):
        fallback = get_property('Blur.Fallback')
        if not fallback:
            return
        if get_property('BlurImage.Original') == fallback:
            return
        if get_condvisibility(CV_GET_BLURRED):
            self.blur_img = ImageFunctions(method='blur', artwork=fallback)
            self.blur_img.setName('blur_img')
            self.blur_img.start()

    @kodi_try_except('lib.monitor.listitem.run_imagefuncs')
    def run_imagefuncs(self):
        for i in ARTWORK_FUNCTIONS:
            if not i.condition():
                continue
            artwork = self.get_artwork(source=i.source(), fallback=i.fallback())
            imgfunc = ImageFunctions(method=i.method, is_thread=False, artwork=artwork)
            imgfunc.run()

    @kodi_try_except('lib.monitor.listitem.on_exit')
    def on_exit(self, keep_tv_artwork=False, clear_properties=True, is_done=True):
        if self._listcontainer:
            try:
                _win = xbmcgui.Window(self._cur_window)  # Note get _win separate from _lst
                _lst = _win.getControl(self._listcontainer)  # Note must get _lst in same func as addItem else Kodi crashes
                _lst.addItem(ListItem().get_listitem())
            except Exception:
                return
            return
        ignore_keys = SETMAIN_ARTWORK if keep_tv_artwork and self.dbtype in ['episodes', 'seasons'] else None
        self.clear_properties(ignore_keys=ignore_keys)
        return get_property('IsUpdating', clear_property=True) if is_done else None

    @kodi_try_except('lib.monitor.listitem.get_listcontainer')
    def get_listcontainer(self, window_id=None, container_id=None):
        window_id = window_id or self._cur_window
        container_id = container_id or int(get_infolabel('Skin.String(TMDbHelper.MonitorContainer)') or 0)
        if not window_id or not container_id:
            return
        if not get_condvisibility(f'Control.IsVisible({container_id})'):
            return -1
        return container_id

    @kodi_try_except('lib.monitor.listitem.get_context_listitem')
    def get_context_listitem(self):
        if not self._last_listitem:
            return
        _id_dialog = xbmcgui.getCurrentWindowDialogId()
        _id_d_list = self.get_listcontainer(_id_dialog)
        if not _id_d_list or _id_d_list == -1:
            return
        _id_window = xbmcgui.getCurrentWindowId()
        _id_w_list = self.get_listcontainer(_id_window)
        if not _id_w_list or _id_w_list == -1:
            return
        _win = xbmcgui.Window(_id_dialog)
        _lst = _win.getControl(_id_d_list)
        _lst.addItem(self._last_listitem)

    @kodi_try_except('lib.monitor.listitem.get_additional_properties')
    def get_additional_properties(self, itemdetails):

        # Get folder and filenamepath for comparison purposes
        itemdetails.listitem['folderpath'] = itemdetails.listitem['infoproperties']['folderpath'] = self.get_infolabel('folderpath')
        itemdetails.listitem['filenameandpath'] = itemdetails.listitem['infoproperties']['filenameandpath'] = self.get_infolabel('filenameandpath')

        # Add some additional properties from the base item
        for k, v in BASEITEM_PROPERTIES:
            try:
                itemdetails.listitem['infoproperties'][k] = next(j for j in (self.get_infolabel(i) for i in v) if j)
            except StopIteration:
                itemdetails.listitem['infoproperties'][k] = None

    @kodi_try_except('lib.monitor.listitem.get_next_listitem')
    def get_next_listitem(self):
        container_item = self.container_item
        container_item_template = container_item.replace('ListItem.', 'ListItem({}).')
        for x in LISTITEM_READAHEAD:
            self.container_item = container_item
            if not self.is_same_item():
                break
            self.container_item = container_item_template.format(x)
            cur_item = str(self.get_cur_item())
            if self.get_infolabel('Label') in self._ignored_labels:
                continue
            if cur_item in self._readcache:
                continue
            self.set_cur_item()
            li_lookup = ListItemLookup(
                self, dbtype=self.dbtype, query=self.query, season=self.season, episode=self.episode,
                year=self.year, imdb_id=self.imdb_id)
            itemdetails = self._readcache[cur_item] = li_lookup.get_itemdetails()
            if not itemdetails.tmdb_id:
                continue
            li_lookup.get_ratings()
            li_lookup.get_nextaired()
            self.li_process_artwork(li_lookup)

    def li_process_artwork(self, li_lookup):
        images = {}

        for i in ARTWORK_FUNCTIONS:
            if not i.condition():
                continue
            artwork = self.get_artwork(source=i.source(), fallback=i.fallback())
            imgfunc = ImageFunctions(method=i.method, is_thread=False, artwork=artwork)
            images[f'{i.method}image'] = imgfunc.func(imgfunc.image)
            images[f'{i.method}image.original'] = imgfunc.image

        if ARTFUNC_CROP.condition() and not images.get(f'{ARTFUNC_CROP.method}image'):
            artwork = li_lookup.get_artwork()
            artwork = artwork.get('clearlogo') or artwork.get('tvshow.clearlogo')
            imgfunc = ImageFunctions(method=ARTFUNC_CROP.method, is_thread=False, artwork=artwork)
            images[f'{ARTFUNC_CROP.method}image'] = imgfunc.func(imgfunc.image)
            images[f'{ARTFUNC_CROP.method}image.original'] = imgfunc.image

        li_artwork = li_lookup.get_artwork()
        li_artwork.update(images)

        return li_artwork

    @kodi_try_except('lib.monitor.listitem.on_finish_listcontainer')
    def on_finish_listcontainer(self, li_lookup, itemdetails):
        if self._listcontainer == -1:
            return
        try:
            _win = xbmcgui.Window(self._cur_window)  # Note get _win separate from _lst
            _lst = _win.getControl(self._listcontainer)  # Note must get _lst in same func as addItem else Kodi crashes
        except Exception:
            _lst = None
        if not _lst:
            return

        def _li_process_artwork(li_lookup, listitem):
            listitem.setArt(self.li_process_artwork(li_lookup))

        def _li_process_ratings(li_lookup, listitem):
            li_lookup.get_ratings()
            li_lookup.get_nextaired()
            listitem.setProperties(li_lookup._itemdetails.listitem['infoproperties'])

        # Add main item to our container
        listitem = self._last_listitem = li_lookup.get_builtitem()
        _lst.addItem(listitem)

        # Process images and ratings in threads
        Thread(target=_li_process_artwork, args=[li_lookup, listitem]).start()
        Thread(target=_li_process_ratings, args=[li_lookup, listitem]).start()

    @kodi_try_except('lib.monitor.listitem.on_finish_winproperties')
    def on_finish_winproperties(self, li_lookup, itemdetails, prev_properties):
        # Update next aired details on a shorter cache
        li_lookup.get_nextaired()

        def _li_process_ratings(li_lookup):
            get_property('IsUpdatingRatings', 'True')
            self.clear_property_list(SETPROP_RATINGS)
            details = li_lookup.get_ratings(threaded=True)
            if self.is_same_item():
                self.set_iter_properties(details.get('infoproperties', {}), SETPROP_RATINGS)
            get_property('IsUpdatingRatings', clear_property=True)

        def _li_process_artwork(li_lookup):
            self.clear_property_list(SETMAIN_ARTWORK)
            artwork = li_lookup.get_artwork()
            if not self.is_same_item():
                return
            self.set_iter_properties(artwork, SETMAIN_ARTWORK)
            # Crop clearlogo from artwork dictionary if item didn't have one
            if ARTFUNC_CROP.condition() and not self.get_artwork(source=ARTFUNC_CROP.source()):
                ImageFunctions(method=ARTFUNC_CROP.method, is_thread=False, artwork=artwork.get('clearlogo')).run()

        # Thread artwork and ratings to avoid delaying main details
        if get_condvisibility(CV_GET_ARTWORK):
            thread_artwork = Thread(target=_li_process_artwork, args=[li_lookup])
            thread_artwork.start()

        if get_condvisibility(CV_GET_RATINGS):
            thread_ratings = Thread(target=_li_process_ratings, args=[li_lookup])
            thread_ratings.start()

        self.set_properties(itemdetails.listitem)
        ignore_keys = prev_properties.intersection(self.properties)
        ignore_keys.update(SETPROP_RATINGS)
        ignore_keys.update(SETMAIN_ARTWORK)
        for k in prev_properties - ignore_keys:
            self.clear_property(k)

    @kodi_try_except('lib.monitor.listitem.on_finish')
    def on_finish(self, li_lookup, itemdetails, prev_properties):
        if self._listcontainer:
            self.on_finish_listcontainer(li_lookup, itemdetails)
        else:
            self.on_finish_winproperties(li_lookup, itemdetails, prev_properties)
        get_property('IsUpdating', clear_property=True)

    @kodi_try_except('lib.monitor.listitem.get_listitem')
    def get_listitem(self):
        # Do some setup of which containers / items / windows we're going to use
        self.get_container()
        self._cur_window = get_current_window()
        self._listcontainer = self.get_listcontainer()

        # We want to set a special container but it doesn't exist so exit
        if self._listcontainer == -1:
            return self.on_exit()

        # Avoid relookups of same item if user is idling and do some readahead instead
        if self._cur_window == self._pre_window and self.is_same_item(update=True):
            return self.get_next_listitem()
        self._pre_window = self._cur_window

        # Ignore special folders like next-page/parent-folder and clear instead
        if self.get_infolabel('Label') in self._ignored_labels:
            return self.on_exit()

        # Clear properties for clean slate if user opened a new directory
        if not self.is_same_folder(update=True) and not self._listcontainer:
            self.on_exit(is_done=False)

        # Grab listitem details for lookup and set a property for skins to check status
        get_property('IsUpdating', 'True')
        self.set_cur_item()

        # Allow early exit if only using imagefunctions
        if not self._listcontainer:
            Thread(target=self.run_imagefuncs).start()
        if get_condvisibility("!Skin.HasSetting(TMDbHelper.Service)"):
            return get_property('IsUpdating', clear_property=True)

        # Lookup item details and early exit for window properties if failed
        li_lookup = ListItemLookup(
            self, dbtype=self.dbtype, query=self.query, season=self.season, episode=self.episode,
            year=self.year, imdb_id=self.imdb_id)
        itemdetails = self._readcache[str(self._cur_item)] = li_lookup.get_itemdetails()
        if not itemdetails.tmdb_id and not self._listcontainer:
            return self.on_exit()
        self.get_additional_properties(itemdetails)

        # Item changed whilst retrieving details so clear and get next item
        if not self.is_same_item():
            self._last_listitem = li_lookup.get_builtitem()  # For passing to context menu modals
            return self.on_exit(keep_tv_artwork=True)

        # Copy previous properties for clearing intersection
        prev_properties = self.properties.copy()
        self.properties = set()

        # Get person library statistics
        if itemdetails.tmdb_type == 'person' and get_condvisibility(CV_GET_PERSONSTATS):
            itemdetails.listitem.setdefault('infoproperties', {}).update(
                get_person_stats(itemdetails.listitem['infolabels'].get('title')) or {})

        self.on_finish(li_lookup, itemdetails, prev_properties)
