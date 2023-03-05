from tmdbhelper.lib.addon.plugin import get_condvisibility, get_infolabel, convert_media_type, convert_type
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_region_date
from tmdbhelper.lib.addon.window import get_property
from tmdbhelper.lib.monitor.images import ImageFunctions
from tmdbhelper.lib.items.listitem import ListItem
from copy import deepcopy


BASEITEM_PROPERTIES = [
    ('base_label', ('label',)),
    ('base_title', ('title',)),
    ('base_icon', ('icon',)),
    ('base_plot', ('plot', 'Property(artist_description)', 'Property(artist_description)', 'addondescription')),
    ('base_tagline', ('tagline',)),
    ('base_dbtype', ('dbtype',)),
    ('base_poster', ('Art(poster)',)),
    ('base_fanart', ('Art(fanart)',)),
    ('base_clearlogo', ('Art(clearlogo)', 'Art(tvshow.clearlogo)', 'Art(artist.clearlogo)')),
    ('base_tvshowtitle', ('tvshowtitle',))]

CV_USE_MULTI_TYPE = ""\
    "Window.IsVisible(DialogPVRInfo.xml) | "\
    "Window.IsVisible(MyPVRChannels.xml) | " \
    "Window.IsVisible(MyPVRRecordings.xml) | "\
    "Window.IsVisible(MyPVRSearch.xml) | "\
    "Window.IsVisible(MyPVRGuide.xml)"

ARTWORK_LOOKUP_TABLE = {
    'poster': ['Art(tvshow.poster)', 'Art(poster)', 'Art(thumb)'],
    'fanart': ['Art(fanart)', 'Art(thumb)'],
    'landscape': ['Art(landscape)', 'Art(fanart)', 'Art(thumb)'],
    'thumb': ['Art(thumb)']}


CROPIMAGE_SOURCE = "Art(artist.clearlogo)|Art(tvshow.clearlogo)|Art(clearlogo)"


class ListItemDetails():
    def __init__(self, parent, position=0):
        self._parent = parent
        self._position = position
        self._season = None
        self._episode = None
        self._itemdetails = None
        self._cache = parent._cache

    def get_infolabel(self, info):
        return self._parent.get_infolabel(info, self._position)

    def setup_current_listitem(self):
        self._dbtype = self.get_listitem_dbtype()
        self._query = self.get_listitem_query()
        self._year = self.get_infolabel('year')
        if self._dbtype in ['episodes', 'multi']:
            self._season = self.get_infolabel('Season') or None
            self._episode = self.get_infolabel('Episode') or None
        self._imdb_id = self.get_listitem_imdb_id()
        self._tmdb_id = self.get_listitem_tmdb_id()

    def get_listitem_imdb_id(self):
        if self._season or self._dbtype not in ['movies', 'tvshows']:
            return
        imdb_id = self.get_infolabel('UniqueId(imdb)') or self.get_infolabel('IMDBNumber') or ''
        return imdb_id if imdb_id.startswith('tt') else ''

    def get_listitem_tmdb_id(self):
        if self._dbtype not in ['movies', 'tvshows', 'seasons', 'episodes']:
            return
        tmdb_id = self.get_infolabel('UniqueId(tmdb)')
        if self._dbtype == 'episodes':
            show_tmdb_id = self.get_infolabel('UniqueId(tvshow.tmdb)')
            return show_tmdb_id if show_tmdb_id else self._parent.get_tmdb_id_parent(tmdb_id, 'episode')
        return tmdb_id

    def get_listitem_query(self):
        query = self.get_infolabel('TvShowTitle')
        if not query and self._dbtype in ['movies', 'tvshows', 'actors', 'multi']:
            query = self.get_infolabel('Title') or self.get_infolabel('Label')
        return query

    def get_listitem_dbtype(self):
        if self.get_infolabel('Property(tmdb_type)') == 'person':
            return 'actors'
        dbtype = self.get_infolabel('dbtype')
        if dbtype:
            return f'{dbtype}s'
        if get_condvisibility(CV_USE_MULTI_TYPE):
            return 'multi' if get_condvisibility("!Skin.HasSetting(TMDbHelper.DisablePVR)") else ''
        return get_infolabel('Container.Content()') or '' if self._parent.container == 'Container.' else ''

    def get_tmdb_type(self):
        return 'multi' if self._dbtype == 'multi' else convert_media_type(self._dbtype, 'tmdb', strip_plural=True, parent_type=True)

    def get_artwork(self, source='', build_fallback=False, built_artwork=None):
        source = source.lower()
        infolabels = ARTWORK_LOOKUP_TABLE.get(source, source.split("|") if source else ARTWORK_LOOKUP_TABLE.get('thumb'))
        for count, i in enumerate(infolabels):
            local_artwork = self.get_infolabel(i)
            if not local_artwork:
                continue
        if not build_fallback:
            return local_artwork or None
        built_artwork = built_artwork or self.get_builtartwork()
        if not built_artwork:
            return local_artwork or None
        for i in infolabels[:count]:
            if not i.startswith('art('):
                continue
            artwork = built_artwork.get(i[4:-1])
            if not artwork:
                continue
            return artwork
        return local_artwork or None

    def get_image_manipulations(self, use_winprops=False, built_artwork=None):
        self._parent._last_blur_fallback = False

        images = {}

        _manipulations = (
            {'method': 'crop',
                'active': lambda: get_condvisibility("Skin.HasSetting(TMDbHelper.EnableCrop)"),
                'images': lambda: self.get_artwork(
                    source=CROPIMAGE_SOURCE,
                    build_fallback=True, built_artwork=built_artwork)},
            {'method': 'blur',
                'active': lambda: get_condvisibility("Skin.HasSetting(TMDbHelper.EnableBlur)"),
                'images': lambda: self.get_artwork(
                    source=get_property('Blur.SourceImage'),
                    build_fallback=True, built_artwork=built_artwork)
                or get_property('Blur.Fallback')},
            {'method': 'desaturate',
                'active': lambda: get_condvisibility("Skin.HasSetting(TMDbHelper.EnableDesaturate)"),
                'images': lambda: self.get_artwork(
                    source=get_property('Desaturate.SourceImage'),
                    build_fallback=True, built_artwork=built_artwork)
                or get_property('Desaturate.Fallback')},
            {'method': 'colors',
                'active': lambda: get_condvisibility("Skin.HasSetting(TMDbHelper.EnableColors)"),
                'images': lambda: self.get_artwork(
                    source=get_property('Colors.SourceImage'),
                    build_fallback=True, built_artwork=built_artwork)
                or get_property('Colors.Fallback')},)

        for i in _manipulations:
            if not i['active']():
                continue
            imgfunc = ImageFunctions(method=i['method'], is_thread=False, artwork=i['images']())
            if use_winprops:
                imgfunc.run()
            else:
                images[f'{i["method"]}image'] = imgfunc.func(imgfunc.image)
                images[f'{i["method"]}image.original'] = imgfunc.image

        return images

    def get_person_stats(self):
        if not self._itemdetails or not self._itemdetails.listitem:
            return
        return self._parent.get_person_stats(
            self._itemdetails.listitem, self._itemdetails.tmdb_type, self._itemdetails.tmdb_id)

    def get_all_ratings(self, use_deepcopy=False):
        if self._itemdetails.tmdb_type not in ['movie', 'tv']:
            return {}
        if not self._itemdetails or not self._itemdetails.listitem:
            return {}
        _listitem = deepcopy(self._itemdetails.listitem) if use_deepcopy else self._itemdetails.listitem
        return self._parent.get_all_ratings(_listitem, self._itemdetails.tmdb_type, self._itemdetails.tmdb_id, self._season, self._episode) or {}

    def get_nextaired(self):
        if not self._itemdetails or not self._itemdetails.listitem:
            return {}
        if self._itemdetails.tmdb_type != 'tv':
            return self._itemdetails.listitem
        return self._parent.get_nextaired(self._itemdetails.listitem, self._itemdetails.tmdb_type, self._itemdetails.tmdb_id)

    def get_additional_properties(self):
        if not self._itemdetails:
            return
        self._itemdetails.listitem['folderpath'] = self._itemdetails.listitem['infoproperties']['folderpath'] = self.get_infolabel('folderpath')
        self._itemdetails.listitem['filenameandpath'] = self._itemdetails.listitem['infoproperties']['filenameandpath'] = self.get_infolabel('filenameandpath')
        for k, v in BASEITEM_PROPERTIES:
            try:
                self._itemdetails.listitem['infoproperties'][k] = next(j for j in (self.get_infolabel(i) for i in v) if j)
            except StopIteration:
                self._itemdetails.listitem['infoproperties'][k] = None

    def get_itemtypeid(self, tmdb_type):
        li_year = self._year if tmdb_type == 'movie' else None
        ep_year = self._year if tmdb_type == 'tv' else None
        multi_t = 'tv' if self._episode or self._season else None

        if tmdb_type == 'multi':
            tmdb_id, tmdb_type = self._parent.get_tmdb_id_multi(
                media_type=multi_t, query=self._query, imdb_id=self._imdb_id, year=li_year, episode_year=ep_year)
            self._dbtype = convert_type(tmdb_type, 'dbtype')
        elif self._tmdb_id:
            tmdb_id = self._tmdb_id
        else:
            tmdb_id = self._parent.get_tmdb_id(
                tmdb_type=tmdb_type, query=self._query, imdb_id=self._imdb_id, year=li_year, episode_year=ep_year)

        return {'tmdb_type': tmdb_type, 'tmdb_id': tmdb_id}

    def get_itemdetails(self, func, *args, **kwargs):
        """ Use itemdetails cache to return a named tuple of tmdb_type, tmdb_id, listitem, artwork
        Runs func(*args, **kwargs) after retrieving a new uncached item for early code execution
        """
        tmdb_type = self.get_tmdb_type()

        def _get_quick(cache_name_id):
            cache_item = self._cache.get_cache(cache_name_id) if tmdb_type else None

            if not cache_item:
                func(*args, **kwargs) if func else None
                cache_item = self._cache.set_cache(self.get_itemtypeid(tmdb_type), cache_name_id)

            cache_data = self._parent.get_itemdetails_cache(**cache_item, season=self._season, episode=self._episode)
            return cache_data

        cache_name_id = self._parent.get_cur_item(self._position)
        cache_name_iq = f'_get_quick.{cache_name_id}'
        self._itemdetails = self._parent.use_itemcache(cache_name_iq, _get_quick, cache_name_id) if tmdb_type else None
        self._itemdetails = self._itemdetails or self._parent.get_itemdetails_blank()
        return self._itemdetails

    def get_builtartwork(self):
        if not self._itemdetails or not self._itemdetails.artwork:
            return {}
        return self._parent.ib.get_item_artwork(self._itemdetails.artwork, is_season=True if self._season else False) or {}

    def get_builtitem(self):
        if not self._itemdetails:
            return ListItem().get_listitem()

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
        li.art = self.get_builtartwork()
        return li.get_listitem()
