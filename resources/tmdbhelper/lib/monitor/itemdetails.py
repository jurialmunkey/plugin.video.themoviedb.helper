from tmdbhelper.lib.addon.plugin import get_condvisibility, get_infolabel, convert_media_type, convert_type, get_setting
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_region_date
from tmdbhelper.lib.monitor.images import ImageManipulations
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.api.mapping import get_empty_item
from collections import namedtuple
from copy import deepcopy


CV_USE_MULTI_TYPE = ""\
    "Window.IsVisible(DialogPVRInfo.xml) | "\
    "Window.IsVisible(MyPVRChannels.xml) | " \
    "Window.IsVisible(MyPVRRecordings.xml) | "\
    "Window.IsVisible(MyPVRSearch.xml) | "\
    "Window.IsVisible(MyPVRGuide.xml)"

ItemDetails = namedtuple("ItemDetails", "tmdb_type tmdb_id listitem artwork")

EXTENDED_PROPERTIES = ""\
    "!Skin.HasSetting(TMDbHelper.DisableExtendedProperties) | "\
    "!String.IsEmpty(Window.Property(TMDbHelper.EnableExtendedProperties))"


class ListItemDetails(ImageManipulations):
    def __init__(self, parent, position=0):
        self._parent = parent
        self._position = position
        self._season = None
        self._episode = None
        self._itemdetails = None

    @property
    def dbtype(self):
        if self.get_infolabel('Property(tmdb_type)') == 'person':
            return 'actors'

        def _get_fallback():
            if get_condvisibility("!Skin.HasSetting(TMDbHelper.DisablePVR)"):
                if get_condvisibility(CV_USE_MULTI_TYPE):
                    return 'multi'
                if self.get_infolabel('ChannelNumberLabel'):
                    return 'multi'
                if self.get_infolabel('Path') == 'pvr://channels/tv/':
                    return 'multi'
            if self._parent._container == 'Container.' and get_setting('service_container_content_fallback'):
                return get_infolabel('Container.Content') or ''
            return ''

        dbtype = self.get_infolabel('dbtype')
        return f'{dbtype}s' if dbtype else _get_fallback()

    @property
    def query(self):
        query = self.get_infolabel('TvShowTitle')
        if not query and self._dbtype in ['movies', 'tvshows', 'actors', 'sets', 'multi']:
            query = self.get_infolabel('Title') or self.get_infolabel('Label')
        return query

    @property
    def year(self):
        return self.get_infolabel('year')

    @property
    def season(self):
        if self._dbtype not in ['seasons', 'episodes', 'multi']:
            return
        return self.get_infolabel('Season') or None

    @property
    def episode(self):
        if self._dbtype not in ['episodes', 'multi']:
            return
        return self.get_infolabel('Episode') or None

    @property
    def imdb_id(self):
        if self._season:
            return
        if self._dbtype not in ['movies', 'tvshows']:
            return
        imdb_id = self.get_infolabel('UniqueId(imdb)') or self.get_infolabel('IMDBNumber') or ''
        return imdb_id if imdb_id.startswith('tt') else ''

    @property
    def tmdb_id(self):
        if self._dbtype in ['movies', 'tvshows']:
            return self.get_infolabel('UniqueId(tmdb)')

        if self._dbtype == 'seasons':
            # TODO: Trakt lookup of TMDb ID for season similar to episodes
            return self.get_infolabel('UniqueId(tvshow.tmdb)')

        if self._dbtype == 'episodes':
            return self.get_infolabel('UniqueId(tvshow.tmdb)') or self._parent.get_tmdb_id_parent(
                tmdb_id=self.get_infolabel('UniqueId(tmdb)'),
                trakt_type='episode',
                season_episode_check=(self._season, self._episode,))

    @property
    def tmdb_type(self):
        if self._dbtype == 'multi':
            return 'multi'
        return convert_media_type(self._dbtype, 'tmdb', strip_plural=True, parent_type=True)

    def setup_current_listitem(self):
        """ Cache property getter return values for performance """
        self._dbtype = self.dbtype
        self._query = self.query
        self._year = self.year
        self._season = self.season
        self._episode = self.episode
        self._imdb_id = self.imdb_id
        self._tmdb_id = self.tmdb_id

    def get_infolabel(self, info):
        return self._parent.get_infolabel(info, self._position)

    def get_person_stats(self):
        if not self._itemdetails or not self._itemdetails.listitem:
            return
        return self._parent.get_person_stats(
            self._itemdetails.listitem, self._itemdetails.tmdb_type, self._itemdetails.tmdb_id)

    def get_all_ratings(self):
        if self._itemdetails.tmdb_type not in ['movie', 'tv']:
            return {}
        if not self._itemdetails or not self._itemdetails.listitem:
            return {}
        return self._parent.get_all_ratings(self._itemdetails.tmdb_type, self._itemdetails.tmdb_id, self._season, self._episode) or {}

    def get_nextaired(self):
        if not self._itemdetails or not self._itemdetails.listitem:
            return {}
        if self._itemdetails.tmdb_type != 'tv':
            return self._itemdetails.listitem
        return self._parent.get_nextaired(self._itemdetails.tmdb_type, self._itemdetails.tmdb_id)

    def get_additional_properties(self, infoproperties=None):
        if not self._itemdetails:
            return
        self._itemdetails.listitem['folderpath'] = self._itemdetails.listitem['infoproperties']['folderpath'] = self.get_infolabel('folderpath')
        self._itemdetails.listitem['filenameandpath'] = self._itemdetails.listitem['infoproperties']['filenameandpath'] = self.get_infolabel('filenameandpath')
        if not infoproperties:
            return
        for k, v in infoproperties.items():
            self._itemdetails.listitem['infoproperties'][k] = v

    def get_itemtypeid(self, tmdb_type):
        li_year = None
        multi_t = None

        if tmdb_type == 'movie':
            li_year = self._year

        if self._episode or self._season:
            multi_t = 'tv'

        if tmdb_type == 'multi':
            tmdb_id, tmdb_type = self._parent.get_tmdb_id_multi(
                tmdb_type=multi_t,
                query=self._query,
                imdb_id=self._imdb_id,
                year=li_year,
            )
            self._dbtype = convert_type(tmdb_type, 'dbtype')

        elif self._tmdb_id:
            tmdb_id = self._tmdb_id

        else:
            tmdb_id = self._parent.get_tmdb_id(
                tmdb_type=tmdb_type,
                query=self._query,
                imdb_id=self._imdb_id,
                year=li_year,
            )

        return (tmdb_type, tmdb_id)

    def get_itemdetails(self):
        """ Use itemdetails cache to return a named tuple of tmdb_type, tmdb_id, listitem, artwork
        Runs func(*args, **kwargs) after retrieving a new uncached item for early code execution
        """
        if not self.tmdb_type:
            self._itemdetails = self.get_itemdetails_blank()
            return self.get_itemdetails_blank()
        try:
            tmdb_type, tmdb_id = self.get_itemtypeid(self.tmdb_type)
            self._parent.lidc.extendedinfo = get_condvisibility(EXTENDED_PROPERTIES)
            item_data = self._parent.lidc.get_item(tmdb_type, tmdb_id, self._season, self._episode)
            self._itemdetails = ItemDetails(tmdb_type, tmdb_id, item_data, item_data['art'])
        except (KeyError, AttributeError, TypeError):
            self._itemdetails = self.get_itemdetails_blank()

        return self._itemdetails

    @staticmethod
    def get_itemdetails_blank():
        return ItemDetails(None, None, get_empty_item(), {})

    def get_builtartwork(self):
        if not self._itemdetails or not self._itemdetails.artwork:
            return {}
        return self._itemdetails.artwork

    def get_builtitem(self):
        if not self._itemdetails:
            return ListItem().get_listitem()

        def set_time_properties(li):
            duration = li.infolabels.get('duration') or 0
            hours = duration // 60 // 60
            minutes = duration // 60 % 60
            totalmin = duration // 60
            li.infoproperties['Duration'] = totalmin
            li.infoproperties['Duration_H'] = hours
            li.infoproperties['Duration_M'] = minutes
            li.infoproperties['Duration_HHMM'] = f'{hours:02d}:{minutes:02d}'

        def set_date_properties(li):
            premiered = li.infolabels.get('premiered')
            date_obj = convert_timestamp(premiered, time_fmt="%Y-%m-%d", time_lim=10)
            if not date_obj:
                return
            li.infoproperties['Premiered'] = get_region_date(date_obj, 'dateshort')
            li.infoproperties['Premiered_Long'] = get_region_date(date_obj, 'datelong')
            li.infoproperties['Premiered_Custom'] = date_obj.strftime(get_infolabel('Skin.String(TMDbHelper.Date.Format)') or '%d %b %Y')

        li = ListItem(**self._itemdetails.listitem)
        set_time_properties(li)
        set_date_properties(li)

        return li.get_listitem()
