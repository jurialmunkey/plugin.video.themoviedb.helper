from tmdbhelper.lib.api.trakt.sync.itemlist import ItemListSyncDataFactory
from tmdbhelper.lib.items.itemlist import ItemListPagination
from tmdbhelper.lib.addon.plugin import convert_type, get_plugin_category, get_localized, get_setting
from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.files.ftools import cached_property


class ListStandardSync(ContainerDirectory):
    item_list_sync_next_page = True
    item_list_sync_limit = 20 * max(get_setting('pagemulti_sync', 'int'), 1)
    item_list_sync_type = ''  # ItemListSyncDataFactory type
    item_list_sync_item_type = None
    item_list_sync_sort_by = None
    item_list_sync_sort_how = None
    item_list_sync_filters = None  # Filters for pre-pagination
    item_list_sync_item_keys = None  # Extra keys for filters
    item_list_plugin_name = '{plural} {localized}'
    item_list_localize = None
    item_list_sync_params_def = None
    item_list_sync_container_content = None

    def get_items_container_content(self, tmdb_type, items):
        if not self.item_list_sync_container_content:
            return convert_type(tmdb_type, 'container', items=items)
        return self.item_list_sync_container_content

    def get_items_sync_list_fallback(self, item_type, sort_by=None, sort_how=None, tmdb_id=None, **kwargs):
        return

    def get_items_sync_list(self, item_type, sort_by=None, sort_how=None, tmdb_id=None, **kwargs):
        return ItemListSyncDataFactory(
            self.item_list_sync_type,
            self.trakt_api,
            sort_by=sort_by or self.item_list_sync_sort_by,
            sort_how=sort_how or self.item_list_sync_sort_how,
            item_type=item_type,
            item_keys=self.item_list_sync_item_keys,
            tmdb_id=tmdb_id).items  # TODO: Pagination and limit at DB level?

    def get_items(self, tmdb_type, page=1, sort_by=None, sort_how=None, tmdb_id=None, **kwargs):
        item_type = self.item_list_sync_item_type or convert_type(tmdb_type, 'trakt')
        items_kwargs = {
            'item_type': item_type,
            'page': page,
            'sort_by': sort_by,
            'sort_how': sort_how,
            'tmdb_id': tmdb_id,
        }

        items = self.get_items_sync_list(**items_kwargs)

        if not items:
            return self.get_items_sync_list_fallback(**items_kwargs)

        self.plugin_category = self.item_list_plugin_name.format(
            localized=get_localized(self.item_list_localize) if self.item_list_localize else '',
            plural=convert_type(tmdb_type, 'plural')
        )

        response = ItemListPagination(
            {item_type: items},
            page=page or 1,
            limit=self.item_list_sync_limit,
            params_def=self.item_list_sync_params_def,
            filters=self.item_list_sync_filters)

        self.kodi_db = self.get_kodi_database(tmdb_type)
        self.container_content = self.get_items_container_content(tmdb_type, response.items)

        if not self.item_list_sync_next_page or sort_by == 'random':
            return response.items

        return response.items + response.next_page


class ListCollection(ListStandardSync):
    item_list_sync_type = 'collection'
    item_list_sync_sort_by = 'title'
    item_list_sync_sort_how = 'asc'
    item_list_localize = 32192


class ListWatchlist(ListStandardSync):
    item_list_sync_type = 'watchlist'
    item_list_sync_sort_by = 'unsorted'
    item_list_localize = 32193


class ListWatchlistReleased(ListStandardSync):
    item_list_sync_type = 'watchlist'
    item_list_sync_sort_by = 'released'
    item_list_sync_sort_how = 'desc'
    item_list_localize = 32456
    item_list_sync_item_keys = ('premiered', )
    item_list_sync_filters = {
        'filter_key': 'premiered',
        'filter_value': {
            'module': 'tmdbhelper.lib.addon.tmdate',
            'method': 'get_todays_date',
            'kwargs': {}
        },
        'filter_operator': 'lt',
        'exclude_key': 'premiered',
        'exclude_value': 'is_empty'
    }


class ListWatchlistAnticipated(ListStandardSync):
    item_list_sync_type = 'watchlist'
    item_list_sync_sort_by = 'released'
    item_list_sync_sort_how = 'asc'
    item_list_localize = 32457
    item_list_sync_item_keys = ('premiered', )
    item_list_sync_filters = {
        'exclude_key': 'premiered',
        'exclude_value': {
            'module': 'tmdbhelper.lib.addon.tmdate',
            'method': 'get_todays_date',
            'kwargs': {}
        },
        'exclude_operator': 'lt'
    }


class ListHistory(ListStandardSync):
    item_list_sync_type = 'watched'
    item_list_sync_sort_by = 'watched'
    item_list_sync_sort_how = 'desc'
    item_list_localize = 32194
    item_list_plugin_name = '{localized} {plural}'


class ListMostWatched(ListStandardSync):
    item_list_sync_type = 'watched'
    item_list_sync_sort_by = 'plays'
    item_list_sync_sort_how = 'desc'
    item_list_localize = 32195
    item_list_plugin_name = '{localized} {plural}'


class ListPlaybackProgress(ListStandardSync):
    item_list_sync_type = 'playback'
    item_list_sync_sort_by = 'paused'
    item_list_sync_sort_how = 'desc'
    item_list_localize = 32196
    item_list_plugin_name = '{localized} {plural}'


class ListFavorites(ListStandardSync):
    item_list_sync_type = 'favorites'
    item_list_sync_sort_by = 'unsorted'
    item_list_localize = 1036


class ListDropped(ListStandardSync):
    item_list_sync_type = 'dropped'
    item_list_sync_sort_by = 'unsorted'
    item_list_localize = 32048


class ListToWatch(ListStandardSync):
    item_list_sync_type = 'towatch'
    item_list_localize = 32078
    # item_type='movie' if tmdb_type == 'movie' else 'show',


class ListNextEpisodes(ListStandardSync):
    item_list_sync_type = 'nextup'
    item_list_sync_sort_how = 'desc'
    item_list_localize = 32197
    item_list_plugin_name = '{localized}'
    item_list_sync_item_type = 'episode'
    item_list_sync_container_content = 'episodes'

    @cached_property
    def thumb_override(self):
        return get_setting('calendar_art', 'int')

    @cached_property
    def item_list_sync_sort_by(self):
        return get_setting('trakt_nextepisodesort', 'str')


class ListUpNext(ListStandardSync):
    item_list_sync_type = 'upnext'
    # item_list_sync_sort_how = 'desc'
    item_list_localize = 32043
    item_list_plugin_name = '{localized}'
    item_list_sync_item_type = 'episode'
    item_list_sync_container_content = 'episodes'

    def get_items_sync_list_fallback(self, item_type, sort_by=None, sort_how=None, tmdb_id=None, **kwargs):
        from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
        try:
            items = BaseViewFactory('episodes', 'tv', tmdb_id, season=1).data
        except TypeError:
            return
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = 'episodes'
        return items


class ListOnDeck(ListStandardSync):
    item_list_sync_type = 'playback'
    item_list_sync_sort_by = 'paused'
    item_list_sync_sort_how = 'desc'
    item_list_localize = 32406
    item_list_plugin_name = '{localized}'

    def get_items(self, tmdb_type, **kwargs):
        self.item_list_sync_container_content = 'episodes' if tmdb_type == 'tv' else 'movies'
        self.item_list_sync_item_type = 'episode' if tmdb_type == 'tv' else 'movie'
        return super().get_items(tmdb_type=tmdb_type, **kwargs)


class ListOnDeckUnWatched(ListOnDeck):
    item_list_sync_type = 'unwatchedplayback'


class ListInProgress(ListOnDeck):
    def get_items(self, tmdb_type, **kwargs):
        if tmdb_type == 'tv':
            self.item_list_sync_type = 'inprogress'
            self.item_list_sync_item_type = 'show'
            self.item_list_sync_params_def = {
                'show': {
                    'info': 'trakt_upnext',
                    'tmdb_type': 'tv',
                    'tmdb_id': '{tmdb_id}'
                }
            }
            self.item_list_localize = 32041
            return super(ListOnDeck, self).get_items(tmdb_type=tmdb_type, **kwargs)

        self.item_list_localize = 32045
        return super().get_items(tmdb_type=tmdb_type, **kwargs)
