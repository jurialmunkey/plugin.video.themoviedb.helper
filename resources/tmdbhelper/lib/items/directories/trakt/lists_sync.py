from tmdbhelper.lib.api.trakt.sync.itemlist import ItemListSyncDataFactory
from tmdbhelper.lib.items.directories.lists_default import ListProperties, ListDefault
from tmdbhelper.lib.items.itemlist import ItemListPagination
from tmdbhelper.lib.addon.plugin import convert_type, get_setting
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class ListSyncProperties(ListProperties):

    next_page = True
    sync_type = ''  # ItemListSyncDataFactory type
    item_type = None  # Conversion to type
    item_keys = None  # Extra keys for filters
    filters = None
    sort_by = None
    sort_how = None
    params_def = None

    @cached_property
    def sync_data(self):
        return ItemListSyncDataFactory(
            self.sync_type,
            self.trakt_api,
            sort_by=self.sort_by,
            sort_how=self.sort_how,
            item_type=self.item_type,
            item_keys=self.item_keys,
            tmdb_id=self.tmdb_id).items

    @cached_property
    def response(self):
        if not self.sync_data:
            return
        return ItemListPagination(
            meta={self.item_type: self.sync_data},
            page=self.page,
            limit=self.limit,
            params_def=self.params_def,
            filters=self.filters)

    @property
    def items(self):
        if not self.response:
            return
        return self.response.items

    @property
    def finalised_items(self):
        if not self.items:
            return
        if not self.next_page or self.sort_by == 'random':
            return self.items
        return self.items + self.response.next_page


class ListStandardSync(ListDefault):

    list_properties_class = ListSyncProperties

    def configure_list_properties(self, list_properties):
        list_properties.limit = 20 * max(get_setting('pagemulti_sync', 'int'), 1)
        list_properties.plugin_name = '{plural} {localized}'
        list_properties.trakt_api = self.trakt_api
        return list_properties

    def get_items(self, tmdb_type, page=1, sort_by=None, sort_how=None, tmdb_id=None, **kwargs):
        self.list_properties.tmdb_id = tmdb_id
        self.list_properties.tmdb_type = tmdb_type
        self.list_properties.item_type = self.list_properties.item_type or convert_type(tmdb_type, 'trakt')
        self.list_properties.page = try_int(page) or 1
        self.list_properties.sort_by = sort_by or self.list_properties.sort_by
        self.list_properties.sort_how = sort_how or self.list_properties.sort_how
        return self.get_items_finalised()


class ListCollection(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'collection'
        list_properties.sort_by = 'title'
        list_properties.sort_how = 'asc'
        list_properties.localize = 32192
        return list_properties


class ListWatchlist(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'watchlist'
        list_properties.sort_by = 'unsorted'
        list_properties.localize = 32193
        return list_properties


class ListWatchlistReleased(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'watchlistreleased'
        list_properties.sort_by = 'released'
        list_properties.sort_how = 'desc'
        list_properties.localize = 32456
        list_properties.item_keys = ('premiered', )
        return list_properties


class ListWatchlistAnticipated(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'watchlistanticipated'
        list_properties.sort_by = 'released'
        list_properties.sort_how = 'asc'
        list_properties.localize = 32457
        list_properties.item_keys = ('premiered', )
        return list_properties


class ListHistory(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'watched'
        list_properties.sort_by = 'watched'
        list_properties.sort_how = 'desc'
        list_properties.localize = 32194
        list_properties.plugin_name = '{localized} {plural}'
        return list_properties


class ListMostWatched(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'watched'
        list_properties.sort_by = 'plays'
        list_properties.sort_how = 'desc'
        list_properties.localize = 32195
        list_properties.plugin_name = '{localized} {plural}'
        return list_properties


class ListPlaybackProgress(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'playback'
        list_properties.sort_by = 'paused'
        list_properties.sort_how = 'desc'
        list_properties.localize = 32196
        list_properties.plugin_name = '{localized} {plural}'
        return list_properties


class ListFavorites(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'favorites'
        list_properties.sort_by = 'unsorted'
        list_properties.localize = 1036
        return list_properties


class ListDropped(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'dropped'
        list_properties.sort_by = 'unsorted'
        list_properties.localize = 32048
        return list_properties


class ListToWatch(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'towatch'
        list_properties.localize = 32078
        return list_properties


class ListNextEpisodes(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'nextup'
        list_properties.sort_how = 'desc'
        list_properties.sort_by = get_setting('trakt_nextepisodesort', 'str')
        list_properties.localize = 32197
        list_properties.plugin_name = '{localized}'
        list_properties.item_type = 'episode'
        list_properties.container_content = 'episodes'
        return list_properties

    @cached_property
    def thumb_override(self):
        return get_setting('calendar_art', 'int')


class ListUpNext(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'upnext'
        list_properties.localize = 32043
        list_properties.plugin_name = '{localized}'
        list_properties.item_type = 'episode'
        list_properties.container_content = 'episodes'
        return list_properties


class ListOnDeck(ListStandardSync):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'playback'
        list_properties.sort_by = 'paused'
        list_properties.sort_how = 'desc'
        list_properties.localize = 32406
        list_properties.plugin_name = '{localized}'
        return list_properties

    def get_items(self, tmdb_type, **kwargs):
        self.list_properties.container_content = 'episodes' if tmdb_type == 'tv' else 'movies'
        self.list_properties.item_type = 'episode' if tmdb_type == 'tv' else 'movie'
        return super().get_items(tmdb_type=tmdb_type, **kwargs)


class ListOnDeckUnWatched(ListOnDeck):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_type = 'unwatchedplayback'
        return list_properties


class ListInProgress(ListOnDeck):
    def get_items(self, tmdb_type, **kwargs):
        if tmdb_type == 'tv':
            self.list_properties.sync_type = 'inprogress'
            self.list_properties.item_type = 'show'
            self.list_properties.params_def = {
                'show': {
                    'info': 'trakt_upnext',
                    'tmdb_type': 'tv',
                    'tmdb_id': '{tmdb_id}'
                }
            }
            self.list_properties.localize = 32041
            return super(ListOnDeck, self).get_items(tmdb_type=tmdb_type, **kwargs)

        self.list_properties.localize = 32045
        return super().get_items(tmdb_type=tmdb_type, **kwargs)
