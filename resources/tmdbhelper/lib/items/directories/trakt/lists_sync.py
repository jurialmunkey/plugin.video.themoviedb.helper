from tmdbhelper.lib.api.trakt.sync.itemlist import ItemListSyncDataFactory
from tmdbhelper.lib.items.itemlist import ItemListPagination
from tmdbhelper.lib.addon.plugin import convert_type, get_plugin_category, get_localized, get_setting
from tmdbhelper.lib.items.container import ContainerDirectory


# class ListCollection(ContainerDirectory):
#     item_list_sync_type = 'collection'
#     item_list_sync_sort_by = 'title'
#     item_list_sync_sort_how = 'asc'
#     item_list_plugin_name = '{plural} {localized}'
#     item_list_localize = 32192

#     def get_items_sync_list(self, item_type, page=1, limit=None, sort_by=None, sort_how=None, params=None, next_page=True, filters=None, tmdb_id=None, **kwargs):
#         return ItemListSyncDataFactory(
#             self.item_list_sync_type, self.trakt_api,
#             sort_by=self.item_list_sync_sort_by,
#             sort_how=self.item_list_sync_sort_how,
#             item_type=item_type,
#             tmdb_id=tmdb_id).items

#     def get_list_items(self, sync_type, item_type, page=1, limit=None, sort_by=None, sort_how=None, params=None, next_page=True, filters=None, tmdb_id=None, **kwargs):
#         if not sync_list.items:
#             return

#         limit = limit or self.trakt_api.sync_item_limit
#         params_def = {item_type: params} if params else None
#         response = ItemListPagination({item_type: sync_list.items}, page=page or 1, limit=limit, params_def=params_def, filters=filters)

#         return response.items if not next_page or sort_by == 'random' else response.items + response.next_page

#     def get_items(self, info, tmdb_type, page=None, **kwargs):
#         from tmdbhelper.lib.addon.consts import TRAKT_SYNC_LISTS
#         info_model = TRAKT_SYNC_LISTS.get(info)
#         info_tmdb_type = info_model.get('tmdb_type') or tmdb_type
#         items = self.get_list_items(
#             sync_type=info_model.get('sync_type', ''),
#             item_type=convert_type(tmdb_type, 'trakt'),
#             page=page,
#             sort_by=kwargs.get('sort_by', None) or info_model.get('sort_by', None),
#             sort_how=kwargs.get('sort_how', None) or info_model.get('sort_how', None),
#             params=info_model.get('params'),
#             filters=info_model.get('filters', None))
#         self.kodi_db = self.get_kodi_database(info_tmdb_type)
#         self.container_content = convert_type(info_tmdb_type, 'container', items=items)
#         self.plugin_category = get_plugin_category(info_model, convert_type(info_tmdb_type, 'plural'))
#         return items


class ListSync(ContainerDirectory):
    def get_list_items(self, sync_type, item_type, page=1, limit=None, sort_by=None, sort_how=None, params=None, next_page=True, filters=None, tmdb_id=None, **kwargs):
        item_keys = tuple(set([v for k, v in filters.items() if k.startswith('filter_key') or k.startswith('exclude_key')])) if filters else None
        sync_list = ItemListSyncDataFactory(sync_type, self.trakt_api, sort_by=sort_by, sort_how=sort_how, item_type=item_type, item_keys=item_keys, tmdb_id=tmdb_id)

        if not sync_list.items:
            return

        limit = limit or self.trakt_api.sync_item_limit
        params_def = {item_type: params} if params else None
        response = ItemListPagination({item_type: sync_list.items}, page=page or 1, limit=limit, params_def=params_def, filters=filters)

        return response.items if not next_page or sort_by == 'random' else response.items + response.next_page

    def get_items(self, info, tmdb_type, page=None, **kwargs):
        from tmdbhelper.lib.addon.consts import TRAKT_SYNC_LISTS
        info_model = TRAKT_SYNC_LISTS.get(info)
        info_tmdb_type = info_model.get('tmdb_type') or tmdb_type
        items = self.get_list_items(
            sync_type=info_model.get('sync_type', ''),
            item_type=convert_type(tmdb_type, 'trakt'),
            page=page,
            sort_by=kwargs.get('sort_by', None) or info_model.get('sort_by', None),
            sort_how=kwargs.get('sort_how', None) or info_model.get('sort_how', None),
            params=info_model.get('params'),
            filters=info_model.get('filters', None))
        self.kodi_db = self.get_kodi_database(info_tmdb_type)
        self.container_content = convert_type(info_tmdb_type, 'container', items=items)
        self.plugin_category = get_plugin_category(info_model, convert_type(info_tmdb_type, 'plural'))
        return items


class ListToWatch(ListSync):
    def get_items(self, info, tmdb_type, page=None, **kwargs):
        """ Get a mix of watchlisted and inprogress """
        if tmdb_type not in ['movie', 'tv']:
            return
        self.kodi_db = self.get_kodi_database(tmdb_type)
        self.container_content = convert_type(tmdb_type, 'container')
        self.plugin_category = f'{convert_type(tmdb_type, "plural")} {get_localized(32078)}'
        return self.get_list_items(
            sync_type='towatch',
            item_type='movie' if tmdb_type == 'movie' else 'show',
            page=page)


class ListOnDeck(ListSync):
    def get_ondeck_movies(self, page=None, sort_by=None, sort_how=None, unwatched=False, **kwargs):
        self.container_content = 'movies'
        self.plugin_category = f'{get_localized(32196)} {convert_type("movie", "plural")}'
        self.kodi_db = self.get_kodi_database('movie')
        sync_type = 'unwatchedplayback' if unwatched else 'playback'
        return self.get_list_items(sync_type=sync_type, item_type='movie', page=page, sort_by=sort_by, sort_how=sort_how)

    def get_ondeck_episodes(self, page=None, sort_by=None, sort_how=None, unwatched=False, **kwargs):
        self.container_content = 'episodes'
        self.plugin_category = get_localized(32406)
        self.kodi_db = self.get_kodi_database('tv')
        sync_type = 'unwatchedplayback' if unwatched else 'playback'
        return self.get_list_items(sync_type=sync_type, item_type='episode', page=page, sort_by=sort_by, sort_how=sort_how)

    def get_items(self, **kwargs):
        return self.get_ondeck_episodes(**kwargs)


class ListOnDeckUnWatched(ListOnDeck):
    def get_items(self, tmdb_type, **kwargs):
        func = self.get_ondeck_episodes if tmdb_type == 'tv' else self.get_ondeck_movies
        return func(unwatched=True, **kwargs)


class ListInProgress(ListOnDeck):
    def get_items(self, info, tmdb_type, page=None, sort_by=None, sort_how=None, **kwargs):

        if tmdb_type != 'tv':
            return self.get_ondeck_movies(page=page, sort_by=sort_by, sort_how=sort_how, **kwargs)

        params = {
            'info': 'trakt_upnext',
            'tmdb_type': 'tv',
            'tmdb_id': '{tmdb_id}'}

        self.kodi_db = self.get_kodi_database(tmdb_type)
        self.container_content = convert_type(tmdb_type, 'container')
        self.plugin_category = f'{get_localized(32196)} {convert_type(tmdb_type, "plural")}'
        return self.get_list_items(sync_type='inprogress', item_type='show', page=page, sort_by=sort_by, sort_how=sort_how, params=params)


class ListNextEpisodes(ListSync):
    def get_items(self, info, tmdb_type, page=None, **kwargs):
        if tmdb_type != 'tv':
            return

        sort_by = get_setting('trakt_nextepisodesort', 'str')
        sort_how = 'desc'

        self.container_content = 'episodes'
        self.thumb_override = get_setting('calendar_art', 'int')
        self.plugin_category = get_localized(32197)
        return self.get_list_items(sync_type='nextup', item_type='episode', page=page, sort_by=sort_by, sort_how=sort_how)


class ListUpNext(ListSync):
    def get_items(self, info, tmdb_type, tmdb_id, page=None, **kwargs):
        if tmdb_type != 'tv':
            return
        items = self.get_list_items(
            sync_type='upnext',
            item_type='episode',
            tmdb_id=tmdb_id,
            page=page)
        if not items:
            from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
            try:
                items = BaseViewFactory('episodes', 'tv', int(tmdb_id), season=1).data
            except TypeError:
                return
        self.kodi_db = self.get_kodi_database(tmdb_type)
        self.container_content = 'episodes'
        self.plugin_category = get_localized(32043)
        return items
