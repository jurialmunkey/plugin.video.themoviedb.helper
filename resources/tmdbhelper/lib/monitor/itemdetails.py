from tmdbhelper.lib.addon.plugin import get_condvisibility, get_setting
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.monitor.images import ImageManipulations
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.api.mapping import get_empty_item
from tmdbhelper.lib.query.database.identifier import make_identifier_id


class MonitorItemDetails(ImageManipulations):

    allow_tvshowtitle_query = ('seasons', 'episodes', 'multi')
    allow_title_query = ('movies', 'tvshows', 'actors', 'sets', 'multi')
    allow_label_query = ('movies', 'tvshows', 'actors', 'sets', 'multi')
    allow_episode = ('episodes', 'multi')
    allow_season = ('seasons', 'episodes', 'multi')
    allow_base_id = ('movies', 'tvshows', 'actors', 'sets')
    allow_episode_year = ('seasons', 'episodes', )
    allow_year = ('movies', 'tvshows', )

    container_dbtype_to_tmdb_type = {
        'movies': 'movie',
        'tvshows': 'tv',
        'seasons': 'tv',
        'episodes': 'tv',
        'actors': 'person',
        'sets': 'collection'
    }

    def __init__(self, parent, position=0):
        self.parent = parent  # ListItemMonitorFunctions
        self.position = position
        self.identifier  # Set this immediately so we have a reference point

    """
    infolabels
    """

    @property
    def is_extended(self):
        return get_condvisibility((
            '!Skin.HasSetting(TMDbHelper.DisableExtendedProperties) | '
            '!String.IsEmpty(Window.Property(TMDbHelper.EnableExtendedProperties))'
        ))

    @cached_property
    def infolabel_property_tmdb_type(self):
        return self.get_infolabel('Property(tmdb_type)')

    @cached_property
    def infolabel_channel_number_label(self):
        return self.get_infolabel('ChannelNumberLabel')

    @cached_property
    def infolabel_path(self):
        return self.get_infolabel('path')

    @cached_property
    def infolabel_dbtype(self):
        return self.get_infolabel('dbtype')

    @cached_property
    def infolabel_folderpath(self):
        return self.get_infolabel('folderpath')

    @cached_property
    def infolabel_filenameandpath(self):
        return self.get_infolabel('filenameandpath')

    @cached_property
    def infolabel_uniqueid_tmdb(self):
        return self.get_infolabel('UniqueId(tmdb)') or self.get_infolabel('Property(tmdb_id)')

    @cached_property
    def infolabel_uniqueid_tvshow_tmdb(self):
        return self.get_infolabel('UniqueId(tvshow.tmdb)') or self.get_infolabel('Property(tvshow.tmdb_id)')

    @cached_property
    def infolabel_uniqueid_imdb(self):
        infolabel_uniqueid_imdb = self.get_infolabel('UniqueId(imdb)') or self.get_infolabel('IMDBNumber') or ''
        return infolabel_uniqueid_imdb if infolabel_uniqueid_imdb.startswith('tt') else ''

    """
    item id
    """

    @cached_property
    def identifier(self):
        return self.get_identifier()

    def get_identifier(self):
        return '.'.join((
            self.get_infolabel('path'),
            self.get_infolabel('folderpath'),
            self.get_infolabel('filenameandpath'),
            self.get_infolabel('label'),
            self.get_infolabel('dbtype'),
            self.get_property('Service.Reload'),
        ))

    """
    conditions
    """

    @cached_property
    def is_pvr_window(self):
        return get_condvisibility((
            'Window.IsVisible(DialogPVRInfo.xml) | '
            'Window.IsVisible(MyPVRChannels.xml) | '
            'Window.IsVisible(MyPVRRecordings.xml) | '
            'Window.IsVisible(MyPVRSearch.xml) | '
            'Window.IsVisible(MyPVRGuide.xml)'
        ))

    @cached_property
    def is_pvr_lookups(self):
        return get_condvisibility("!Skin.HasSetting(TMDbHelper.DisablePVR)")

    @cached_property
    def is_container_content_lookups(self):
        if self.parent._container != 'Container.':
            return False
        if not get_setting('service_container_content_fallback'):
            return False
        return True

    """
    properties
    """

    @cached_property
    def container_content_fallback(self):
        if not self.is_container_content_lookups:
            return ''
        return self.get_infolabel('Container.Content') or ''

    @cached_property
    def fuzzy_dbtype(self):
        if self.is_pvr_lookups:
            if self.is_pvr_window:
                return 'multi'
            if self.infolabel_channel_number_label:
                return 'multi'
            if self.infolabel_path == 'pvr://channels/tv/':
                return 'multi'
        return self.container_content_fallback

    @cached_property
    def dbtype(self):
        if self.infolabel_property_tmdb_type == 'person':
            return 'actors'
        if self.infolabel_dbtype:
            return f'{self.infolabel_dbtype}s'
        return self.fuzzy_dbtype

    @cached_property
    def query(self):
        query = ''
        if not query and self.dbtype in self.allow_tvshowtitle_query:
            query = self.get_infolabel('tvshowtitle')
        if not query and self.dbtype in self.allow_title_query:
            query = self.get_infolabel('title')
        if not query and self.dbtype in self.allow_label_query:
            query = self.get_infolabel('label')
        return query

    @cached_property
    def year(self):
        if self.dbtype not in self.allow_year:
            return
        return self.get_infolabel('year')

    @cached_property
    def episode_year(self):
        if self.dbtype not in self.allow_episode_year:
            return
        return self.get_infolabel('year')

    @cached_property
    def season(self):
        if self.dbtype not in self.allow_season:
            return
        season = self.get_infolabel('season')
        return season if season or season == 0 else None

    @cached_property
    def episode(self):
        if self.dbtype not in self.allow_episode:
            return
        return self.get_infolabel('episode') or None

    @cached_property
    def imdb_id(self):
        if self.dbtype not in self.allow_base_id:
            return
        return self.infolabel_uniqueid_imdb

    @cached_property
    def parent_tvshow_tmdb_id(self):
        return self.parent.get_tmdb_id_parent(
            tmdb_id=self.infolabel_uniqueid_tmdb,
            item_type='episode',
            season=self.season,
            episode=self.episode,
        )

    @cached_property
    def parent_tmdb_id(self):
        return self.parent.get_tmdb_id(
            tmdb_type=self.tmdb_type,
            query=self.query,
            imdb_id=self.imdb_id,
            year=self.year,
            episode_year=self.episode_year,
        )

    @cached_property
    def multi_tmdb_id(self):
        tmdb_id, tmdb_type = self.parent.get_tmdb_id_multi(
            tmdb_type='tv' if self.season or self.episode else None,
            query=self.query,
            imdb_id=self.imdb_id
        )
        self.tmdb_type = tmdb_type  # Also update tmdb_type with new type

        def container_type():
            if self.tmdb_type == 'movie':
                return 'movies'
            if self.season and self.episode:
                return 'episodes'
            if self.season:
                return 'seasons'
            if self.tmdb_type == 'tv':
                return 'tvshows'
            if self.tmdb_type == 'person':
                return 'actors'

        self.dbtype = container_type()

        return tmdb_id

    @cached_property
    def identifier_id(self):
        return make_identifier_id(
            dbtype=self.dbtype,
            query=self.query,
            season=self.season,
            episode=self.episode,
            imdb_id=self.imdb_id,
            year=self.year,
            episode_year=self.episode_year,
            infolabel_uniqueid_tmdb=self.infolabel_uniqueid_tmdb,
            infolabel_uniqueid_tvshow_tmdb=self.infolabel_uniqueid_tvshow_tmdb,
        )

    @cached_property
    def tmdb_id(self):
        identifier_details = self.parent.get_identifier_details(self.identifier_id)
        identifier_details = identifier_details or self.parent.set_identifier_details(
            self.identifier_id,
            self.get_tmdb_id(),
            self.tmdb_type
        )
        if identifier_details:
            self.tmdb_type = identifier_details.tmdb_type
            return identifier_details.tmdb_id

    def get_tmdb_id(self):
        if self.dbtype in self.allow_base_id:
            return self.infolabel_uniqueid_tmdb or self.parent_tmdb_id

        if self.dbtype == 'seasons':
            return self.infolabel_uniqueid_tvshow_tmdb or self.parent_tmdb_id  # TODO: Additional fallback check for parent_tvshow first?

        if self.dbtype == 'episodes':
            return self.infolabel_uniqueid_tvshow_tmdb or self.parent_tvshow_tmdb_id or self.parent_tmdb_id

        if self.dbtype == 'multi':
            return self.multi_tmdb_id

    @cached_property
    def tmdb_type(self):
        return self.container_dbtype_to_tmdb_type.get(self.dbtype)

    def get_infolabel(self, info):
        return self.parent.get_infolabel(info, self.position)

    @cached_property
    def all_ratings(self):
        if self.tmdb_type not in ('movie', 'tv'):
            return {}
        if not self.item:
            return {}
        return self.parent.get_all_ratings(self.tmdb_type, self.tmdb_id, self.season, self.episode) or {}

    def set_additional_properties(self, infoproperties=None):
        if not self.item:
            return
        if not infoproperties:
            return
        self.item['infoproperties'].update(infoproperties or {})
        self.item['folderpath'] = self.item['infoproperties']['folderpath'] = self.infolabel_folderpath
        self.item['filenameandpath'] = self.item['infoproperties']['filenameandpath'] = self.infolabel_filenameandpath

    @property
    def is_same_item(self):
        return self.get_identifier() == self.identifier

    @cached_property
    def artwork(self):
        if not self.item or 'art' not in self.item:
            return {}
        return self.item['art']

    def set_blank_itemdetails(self):
        self.tmdb_id = None
        self.tmdb_type = None
        self.artwork = {}
        return get_empty_item()

    @cached_property
    def lidc_item(self):
        return self.get_lidc_item()

    def get_lidc_item(self):
        self.parent.lidc.extendedinfo = self.is_extended
        self.parent.lidc.cache_refresh = None
        return self.parent.lidc.get_item(self.tmdb_type, self.tmdb_id, self.season, self.episode)

    def update_lidc_item(self):
        self.lidc_item = self.get_lidc_item()
        return self.lidc_item

    @cached_property
    def item(self):
        return self.get_item()

    def get_item(self):
        if not self.is_same_item:
            return self.set_blank_itemdetails()
        if not self.tmdb_id:
            return self.set_blank_itemdetails()
        if not self.tmdb_type:
            return self.set_blank_itemdetails()
        if not self.lidc_item:  # or 'art' not in self.lidc_item:
            return self.set_blank_itemdetails()
        return self.lidc_item

    def update_item(self):
        self.update_lidc_item()
        self.item = self.get_item()
        return self.item

    @cached_property
    def listitem(self):
        return self.get_listitem()

    def get_listitem(self):
        if not self.item:
            return ListItem().get_listitem()
        return ListItem(**self.item).get_listitem()

    def update_listitem(self):
        self.update_item()
        self.listitem = self.get_listitem()
        return self.listitem
