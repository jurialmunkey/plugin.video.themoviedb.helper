import xbmcgui
from resources.lib.api.kodi.rpc import get_person_stats
from resources.lib.addon.window import get_property
from resources.lib.monitor.common import CommonMonitorFunctions, SETMAIN_ARTWORK, SETPROP_RATINGS
from resources.lib.monitor.images import ImageFunctions
from resources.lib.addon.plugin import convert_media_type, convert_type, get_setting, get_infolabel, get_condvisibility, get_localized
from resources.lib.addon.logger import kodi_try_except
from resources.lib.files.bcache import BasicCache
from resources.lib.items.listitem import ListItem
from resources.lib.addon.tmdate import convert_timestamp, get_region_date
from threading import Thread
from copy import deepcopy
from collections import namedtuple


DIALOG_ID_EXCLUDELIST = [9999]


class ListItemMonitor(CommonMonitorFunctions):
    def __init__(self):
        super(ListItemMonitor, self).__init__()
        self.cur_item = 0
        self.pre_item = 1
        self.cur_folder = None
        self.pre_folder = None
        self.cur_window = 0
        self.pre_window = 1
        self.property_prefix = 'ListItem'
        self._last_blur_fallback = False
        self._cache = BasicCache(filename=f'QuickService.db')
        self._ignored_labels = ['..', get_localized(33078)]
        self._listcontainer = None
        self._listcache = {}
        self._itemcache = {}

    def get_container(self):

        def _get_container():
            widget_id = get_property('WidgetContainer', is_type=int)
            if widget_id:
                return f'Container({widget_id}).'
            return 'Container.'

        def _get_container_item():
            if get_condvisibility(
                    "[Window.IsVisible(DialogPVRInfo.xml)"
                    " | Window.IsVisible(MyPVRGuide.xml)"
                    " | Window.IsVisible(movieinformation)] + "
                    "!Skin.HasSetting(TMDbHelper.ForceWidgetContainer)"):
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
        imdb_id = self.get_infolabel('IMDBNumber') or ''
        if imdb_id.startswith('tt'):
            return imdb_id
        return ''

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
        if get_condvisibility(
                "Window.IsVisible(DialogPVRInfo.xml) | "
                "Window.IsVisible(MyPVRChannels.xml) | "
                "Window.IsVisible(MyPVRRecordings.xml) | "
                "Window.IsVisible(MyPVRSearch.xml) | "
                "Window.IsVisible(MyPVRGuide.xml)"):
            return 'multi' if get_condvisibility("!Skin.HasSetting(TMDbHelper.DisablePVR)") else ''
        if self.container == 'Container.':
            return get_infolabel('Container.Content()') or ''
        return ''

    def get_tmdb_type(self, dbtype=None):
        dbtype = dbtype or self.dbtype
        if dbtype == 'multi':
            return 'multi'
        return convert_media_type(dbtype, 'tmdb', strip_plural=True, parent_type=True)

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
        self.cur_item = self.get_cur_item()
        if self.cur_item == self.pre_item:
            return self.cur_item
        if update:
            self.pre_item = self.cur_item

    def get_cur_folder(self):
        return ('current_folder', self.container, get_infolabel('Container.Content()'), self.get_numitems(),)

    def clear_properties(self, ignore_keys=None):
        if not self.get_artwork(source="Art(artist.clearlogo)|Art(tvshow.clearlogo)|Art(clearlogo)"):
            self.properties.update({'CropImage', 'CropImage.Original'})
        super().clear_properties(ignore_keys=ignore_keys)

    @kodi_try_except('lib.monitor.listitem.is_same_folder')
    def is_same_folder(self, update=True):
        self.cur_folder = self.get_cur_folder()
        if self.cur_folder == self.pre_folder:
            return self.cur_folder
        if update:
            self.pre_folder = self.cur_folder

    @kodi_try_except('lib.monitor.listitem.process_artwork')
    def process_artwork(self, artwork, tmdb_type):
        self.clear_property_list(SETMAIN_ARTWORK)
        if not self.is_same_item():
            return
        artwork = self.ib.get_item_artwork(artwork, is_season=True if self.season else False)
        self.set_iter_properties(artwork, SETMAIN_ARTWORK)

        # Crop Image
        if get_condvisibility("Skin.HasSetting(TMDbHelper.EnableCrop)"):
            if self.get_artwork(source="Art(artist.clearlogo)|Art(tvshow.clearlogo)|Art(clearlogo)"):
                return  # We already cropped listitem artwork so we only crop here if it didn't have a clearlogo and we need to look it up
            ImageFunctions(method='crop', is_thread=False, artwork=artwork.get('clearlogo')).run()

    @kodi_try_except('lib.monitor.listitem.process_ratings')
    def process_ratings(self, details, tmdb_type, tmdb_id, listitem=None):
        self.clear_property_list(SETPROP_RATINGS)
        try:
            trakt_type = {'movie': 'movie', 'tv': 'show'}[tmdb_type]
        except KeyError:
            return  # Only lookup ratings for movie or tvshow
        get_property('IsUpdatingRatings', 'True')
        if not listitem:
            details = deepcopy(details)  # Avoid race conditions with main thread while iterating over dictionary
        details = self.get_omdb_ratings(details)
        details = self.get_imdb_top250_rank(details, trakt_type=trakt_type)
        details = self.get_trakt_ratings(details, trakt_type, season=self.season, episode=self.episode)
        details = self.get_tvdb_awards(details, tmdb_type, tmdb_id)
        if not self.is_same_item():
            get_property('IsUpdatingRatings', clear_property=True)
            return
        if not listitem:
            self.set_iter_properties(details.get('infoproperties', {}), SETPROP_RATINGS)
        else:
            if tmdb_type == 'tv':
                nextaired = self.tmdb_api.get_tvshow_nextaired(tmdb_id)
                details['infoproperties'].update(nextaired)
            listitem.setProperties(details.get('infoproperties', {}))
        get_property('IsUpdatingRatings', clear_property=True)
        return details

    @kodi_try_except('lib.monitor.listitem.clear_on_scroll')
    def clear_on_scroll(self):
        self.cur_window = self.get_window_id()
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
        if self._last_blur_fallback:
            return
        fallback = get_property('Blur.Fallback')
        if not fallback:
            return
        if get_condvisibility("Skin.HasSetting(TMDbHelper.EnableBlur)"):
            self.blur_img = ImageFunctions(method='blur', artwork=fallback)
            self.blur_img.setName('blur_img')
            self.blur_img.start()
            self._last_blur_fallback = True

    def run_imagefuncs(self, itemdetails=None, listitem=None):
        if listitem:
            images = {}

        # Cropping
        if get_condvisibility("Skin.HasSetting(TMDbHelper.EnableCrop)"):
            artwork = self.get_artwork(source="Art(artist.clearlogo)|Art(tvshow.clearlogo)|Art(clearlogo)")
            if not artwork and listitem and itemdetails:
                artwork = self.ib.get_item_artwork(itemdetails.artwork, is_season=True if self.season else False)
                artwork = artwork.get('clearlogo') or artwork.get('tvshow.clearlogo')
            imgfunc = ImageFunctions(method='crop', is_thread=False, artwork=artwork)
            if not listitem:
                imgfunc.run()
            else:
                images['cropimage'] = imgfunc.func(imgfunc.image)
                images['cropimage.original'] = imgfunc.image

        # Blur Image
        if get_condvisibility("Skin.HasSetting(TMDbHelper.EnableBlur)"):
            imgfunc = ImageFunctions(method='blur', is_thread=False, artwork=self.get_artwork(
                source=get_property('Blur.SourceImage'),
                fallback=get_property('Blur.Fallback')))
            self._last_blur_fallback = False
            if not listitem:
                imgfunc.run()
            else:
                images['blurimage'] = imgfunc.func(imgfunc.image)
                images['blurimage.original'] = imgfunc.image

        # Desaturate Image
        if get_condvisibility("Skin.HasSetting(TMDbHelper.EnableDesaturate)"):
            imgfunc = ImageFunctions(method='desaturate', is_thread=False, artwork=self.get_artwork(
                source=get_property('Desaturate.SourceImage'),
                fallback=get_property('Desaturate.Fallback')))
            if not listitem:
                imgfunc.run()
            else:
                images['desaturateimage'] = imgfunc.func(imgfunc.image)
                images['desaturateimage.original'] = imgfunc.image

        # CompColors
        if get_condvisibility("Skin.HasSetting(TMDbHelper.EnableColors)"):
            imgfunc = ImageFunctions(method='colors', is_thread=False, artwork=self.get_artwork(
                source=get_property('Colors.SourceImage'),
                fallback=get_property('Colors.Fallback')))
            if not listitem:
                imgfunc.run()
            else:
                images['colors'] = imgfunc.func(imgfunc.image)
                images['colors.original'] = imgfunc.image

        if listitem and images:
            artwork = self.ib.get_item_artwork(itemdetails.artwork, is_season=True if self.season else False)
            artwork.update(images)
            listitem.setArt(artwork)
            return images

    def get_itemtypeid(self, tmdb_type):
        imdb_id = self.imdb_id if not self.season else None  # Cant tell if IMDb ID is show or season/episode so skip
        li_year = self.year if tmdb_type == 'movie' else None
        ep_year = self.year if tmdb_type == 'tv' else None

        if tmdb_type == 'multi':
            tmdb_id, tmdb_type = self.get_tmdb_id_multi(
                media_type='tv' if self.get_infolabel('episode') or self.get_infolabel('season') else None,
                query=self.query, imdb_id=imdb_id, year=li_year, episode_year=ep_year)
            self.dbtype = convert_type(tmdb_type, 'dbtype')
            return (tmdb_type, tmdb_id)

        tmdb_id = self.get_tmdb_id(tmdb_type=tmdb_type, query=self.query, imdb_id=imdb_id, year=li_year, episode_year=ep_year)
        return (tmdb_type, tmdb_id)

    def get_itemdetails_quick(self, tmdb_type=None, tmdb_id=None, season=None, episode=None):
        ItemDetails = namedtuple("ItemDetails", "tmdb_type tmdb_id listitem artwork")
        if not tmdb_type or not tmdb_id:
            return
        cache_name = f'{tmdb_type}.{tmdb_id}.{season}.{episode}'
        cache_item = self._itemcache.get(cache_name)
        if cache_item:
            return cache_item
        details = self.ib.get_item(tmdb_type, tmdb_id, season, episode)
        if not details:
            return
        try:
            itemdetails = ItemDetails(tmdb_type, tmdb_id, details['listitem'], details['artwork'])
        except (KeyError, AttributeError, TypeError):
            return
        self._itemcache[cache_name] = itemdetails
        return itemdetails

    def get_itemdetails(self):
        """ Returns a named tuple of tmdb_type, tmdb_id, listitem, artwork """
        tmdb_type = self.get_tmdb_type()
        if not tmdb_type:
            return

        # Check TMDb ID in cache
        cache_name = str(self.cur_item)
        cache_item = self._cache.get_cache(cache_name) or {}
        itemdetails = self.get_itemdetails_quick(**cache_item)

        if not itemdetails:
            # Item not cached so clear previous item details now
            ignore_keys = SETMAIN_ARTWORK if self.dbtype in ['episodes', 'seasons'] else None
            self.clear_properties(ignore_keys=ignore_keys)

            # Lookup new item details and cache them
            tmdb_type, tmdb_id = self.get_itemtypeid(tmdb_type)
            itemdetails = self.get_itemdetails_quick(tmdb_type, tmdb_id, self.season, self.episode)
            if not itemdetails:
                return
            self._cache.set_cache({'tmdb_type': tmdb_type, 'tmdb_id': tmdb_id}, cache_name)

        return itemdetails

    def get_window_id(self):
        try:
            _id_dialog = xbmcgui.getCurrentWindowDialogId()
            return _id_dialog if _id_dialog not in DIALOG_ID_EXCLUDELIST else xbmcgui.getCurrentWindowId()
        except Exception:
            return

    def on_exit(self, keep_tv_artwork=False, clear_properties=True):
        if self._listcontainer:
            try:
                _win = xbmcgui.Window(self.cur_window)  # Note get _win separate from _lst
                _lst = _win.getControl(self._listcontainer)  # Note must get _lst in same func as addItem else Kodi crashes
                _lst.addItem(ListItem().get_listitem())
            except Exception:
                return
            return
        ignore_keys = SETMAIN_ARTWORK if keep_tv_artwork and self.dbtype in ['episodes', 'seasons'] else None
        self.clear_properties(ignore_keys=ignore_keys)
        return get_property('IsUpdating', clear_property=True)

    def get_listcontainer(self):
        container_id = int(get_infolabel('Skin.String(TMDbHelper.MonitorContainer)') or 0)
        if not self.cur_window or not container_id:
            return
        if not get_condvisibility(f'Control.IsVisible({container_id}'):
            return -1
        return container_id

    def get_builtitem(self, itemdetails):
        if not itemdetails:
            return

        def set_time_properties(duration):
            minutes = duration // 60 % 60
            hours = duration // 60 // 60
            itemdetails.listitem['infoproperties']['Duration'] = duration // 60
            itemdetails.listitem['infoproperties']['Duration_H'] = hours
            itemdetails.listitem['infoproperties']['Duration_M'] = minutes
            itemdetails.listitem['infoproperties']['Duration_HHMM'] = f'{hours:02d}:{minutes:02d}'

        def set_date_properties(premiered):
            date_obj = convert_timestamp(premiered, time_fmt="%Y-%m-%d", time_lim=10)
            if not date_obj:
                return
            itemdetails.listitem['infoproperties']['Premiered'] = get_region_date(date_obj, 'dateshort')
            itemdetails.listitem['infoproperties']['Premiered_Long'] = get_region_date(date_obj, 'datelong')
            itemdetails.listitem['infoproperties']['Premiered_Custom'] = date_obj.strftime(get_infolabel('Skin.String(TMDbHelper.Date.Format)') or '%d %b %Y')

        set_time_properties(itemdetails.listitem['infolabels'].get('duration', 0))
        set_date_properties(itemdetails.listitem['infolabels'].get('premiered'))

        li = ListItem(**itemdetails.listitem)
        li.art = self.ib.get_item_artwork(itemdetails.artwork, is_season=True if self.season else False)
        return li.get_listitem()

    def on_finished(self, itemdetails, prev_properties):
        if self._listcontainer == -1:
            return

        if self._listcontainer:
            try:
                _win = xbmcgui.Window(self.cur_window)  # Note get _win separate from _lst
                _lst = _win.getControl(self._listcontainer)  # Note must get _lst in same func as addItem else Kodi crashes
            except Exception:
                _lst = None
        else:
            _lst = None

        if _lst:
            # Add main item to our container
            listitem = self.get_builtitem(itemdetails)
            _lst.addItem(listitem)

            # Process images and ratings in threads
            Thread(target=self.run_imagefuncs, args=[
                itemdetails, listitem]).start()
            Thread(target=self.process_ratings, args=[
                itemdetails.listitem, itemdetails.tmdb_type, itemdetails.tmdb_id, listitem]).start()

        else:
            self.set_properties(itemdetails.listitem)
            ignore_keys = prev_properties.intersection(self.properties)
            ignore_keys.update(SETPROP_RATINGS)
            ignore_keys.update(SETMAIN_ARTWORK)
            for k in prev_properties - ignore_keys:
                self.clear_property(k)

        get_property('IsUpdating', clear_property=True)

    @kodi_try_except('lib.monitor.listitem.get_listitem')
    def get_listitem(self):
        self.get_container()
        self.cur_window = self.get_window_id()
        self._listcontainer = self.get_listcontainer()

        # We want to set a special container but it doesn't exist so exit
        if self._listcontainer == -1:
            return self.on_exit()

        # Check if the item has changed before retrieving details again
        if self.cur_window == self.pre_window and self.is_same_item(update=True):
            return

        self.pre_window = self.cur_window

        # Ignore some special folders like next page and parent folder
        if self.get_infolabel('Label') in self._ignored_labels:
            return self.on_exit()

        # Set a property for skins to check if item details are updating
        get_property('IsUpdating', 'True')

        # Clear properties for clean slate if user opened a new directory
        if not self.is_same_folder(update=True):
            self.clear_properties()

        # Get the current listitem details for the details lookup
        self.set_cur_item()

        # Thread image functions to prevent blocking details lookup
        if not self._listcontainer:
            Thread(target=self.run_imagefuncs).start()

        # Allow early exit if the skin only needs image manipulations
        if get_condvisibility("!Skin.HasSetting(TMDbHelper.Service)"):
            return get_property('IsUpdating', clear_property=True)

        # Check ftv setting so item builder can skip artwork lookups if unneeded
        self.ib.ftv_api = self.ftv_api if get_setting('service_fanarttv_lookup') else None

        # Lookup item and exit early if failed
        itemdetails = self.get_itemdetails()
        if not itemdetails or not itemdetails.tmdb_type or not itemdetails.listitem:
            return self.on_exit()

        # Item changed whilst retrieving details so clear and get next item
        if not self.is_same_item():
            return self.on_exit(keep_tv_artwork=True)

        # Get item folderpath and filenameandpath for comparison
        itemdetails.listitem['folderpath'] = itemdetails.listitem['infoproperties']['folderpath'] = self.get_infolabel('folderpath')
        itemdetails.listitem['filenameandpath'] = itemdetails.listitem['infoproperties']['filenameandpath'] = self.get_infolabel('filenameandpath')

        # Copy previous properties
        prev_properties = self.properties.copy()
        self.properties = set()

        # Need to update Next Aired with a shorter cache time than details
        if not self._listcontainer and itemdetails.tmdb_type == 'tv':
            nextaired = self.tmdb_api.get_tvshow_nextaired(itemdetails.tmdb_id)
            itemdetails.listitem['infoproperties'].update(nextaired)

        # Get our artwork properties
        if not self._listcontainer and get_condvisibility("!Skin.HasSetting(TMDbHelper.DisableArtwork)"):
            thread_artwork = Thread(target=self.process_artwork, args=[itemdetails.artwork, itemdetails.tmdb_type])
            thread_artwork.start()

        # Get person library statistics
        if itemdetails.tmdb_type == 'person' and itemdetails.listitem.get('infolabels', {}).get('title'):
            if get_condvisibility("!Skin.HasSetting(TMDbHelper.DisablePersonStats)"):
                itemdetails.listitem.setdefault('infoproperties', {}).update(
                    get_person_stats(itemdetails.listitem['infolabels']['title']) or {})

        # Get our item ratings
        if not self._listcontainer and get_condvisibility("!Skin.HasSetting(TMDbHelper.DisableRatings)"):
            thread_ratings = Thread(target=self.process_ratings, args=[itemdetails.listitem, itemdetails.tmdb_type, itemdetails.tmdb_id])
            thread_ratings.start()

        self.on_finished(itemdetails, prev_properties)
