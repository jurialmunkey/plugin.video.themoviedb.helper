from tmdbhelper.lib.items.container import ContainerDirectory, use_item_cache
from tmdbhelper.lib.addon.plugin import convert_type, get_localized
from tmdbhelper.lib.addon.dialog import progress_bg


class ListAiringNext(ContainerDirectory):

    @progress_bg
    def get_list_items(self, seed_items: list, prefix: str, reverse: bool = False, **kwargs):
        from tmdbhelper.lib.addon.thread import ParallelThread
        from tmdbhelper.lib.addon.tmdate import is_future_timestamp
        from tmdbhelper.lib.api.mapping import get_empty_item
        from tmdbhelper.lib.items.database.listitem import ListItemDetails

        self.dialog_progress_bg.update(0, message=f'Initialising')
        self._get_list_items_progress_max = len(seed_items)
        self._get_list_items_progress_now = 0

        def _get_lidc():
            lidc = ListItemDetails(self)
            lidc.extendedinfo = False
            return lidc

        def _get_lidc_data(tmdb_id):
            data = _get_lidc().get_item('tv', tmdb_id)
            return data.get('infoproperties') or {}

        def _get_nextaired_item(tmdb_id):
            ip = _get_lidc_data(tmdb_id)

            premiered = ip.get(f'{prefix}.original')
            if not is_future_timestamp(premiered, time_fmt="%Y-%m-%d", time_lim=10, days=-1):
                return

            try:
                item = get_empty_item()
                item['label'] = f"{ip.get(f'{prefix}.name')} ({premiered})"
                item['infolabels']['mediatype'] = 'episode'
                item['infolabels']['title'] = ip.get(f'{prefix}.name')
                item['infolabels']['episode'] = ip.get(f'{prefix}.episode')
                item['infolabels']['season'] = ip.get(f'{prefix}.season')
                item['infolabels']['plot'] = ip.get(f'{prefix}.plot')
                item['infolabels']['year'] = ip.get(f'{prefix}.year')
                item['infolabels']['premiered'] = premiered
                item['infoproperties']['tmdb_type'] = 'episode'
                item['infoproperties']['tmdb_id'] = item['unique_ids']['tvshow.tmdb'] = tmdb_id
                item['params'] = {
                    'info': 'details',
                    'tmdb_type': 'tv',
                    'tmdb_id': tmdb_id,
                    'episode': item['infolabels']['episode'],
                    'season': item['infolabels']['season']}
            except (TypeError, KeyError, AttributeError):
                return

            return item

        def _get_nextaired_item_thread(i):
            tmdb_id = i.get('tmdb_id') or self.query_database.get_tmdb_id(
                tmdb_type='tv',
                imdb_id=i.get('imdb_id'),
                tvdb_id=i.get('tvdb_id'),
                query=i.get('showtitle') or i.get('title'),
                year=i.get('year')
            )

            if not tmdb_id:
                self._get_list_items_progress_now += 1
                return

            item = _get_nextaired_item(tmdb_id)

            self.dialog_progress_bg.update(
                int((self._get_list_items_progress_now / self._get_list_items_progress_max) * 100),
                message=f'{tmdb_id} - Checking TMDb ID')

            self._get_list_items_progress_now += 1
            return item or None

        with ParallelThread(seed_items, _get_nextaired_item_thread) as pt:
            item_queue = pt.queue

        items = [i for i in item_queue if i]
        items = sorted(items, key=lambda i: i['infolabels']['premiered'], reverse=reverse)
        return items


class ListLibraryAiringNext(ListAiringNext):

    @use_item_cache('ItemContainer.db', cache_days=0.02)  # Only cache for 30 minutes in case of library changes
    def get_cache_items(self):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        kodi_db = get_kodi_library('tv')
        return self.get_list_items(kodi_db.database, 'next_aired') if kodi_db and kodi_db.database else None

    def get_items(self, **kwargs):
        from tmdbhelper.lib.items.pages import PaginatedItems
        self.container_content = convert_type('episode', 'container')
        self.plugin_category = f'{get_localized(32458)}'
        paginated_items = PaginatedItems(self.get_cache_items(), page=kwargs.get('page', 1), limit=20)
        return paginated_items.items + paginated_items.next_page


class ListTraktAiringNext(ListAiringNext):

    @use_item_cache('ItemContainer.db', cache_days=0.02)  # Only cache for 30 minutes in case of trakt changes
    def get_cache_items(self):
        sd = self.trakt_api.trakt_syncdata
        sd = sd.get_all_unhidden_shows_started_getter()
        try:
            items = [{'tmdb_id': i[sd.keys.index('tmdb_id')]} for i in sd.items if i]
        except Exception:
            return
        return self.get_list_items(items, 'next_aired') if items else None

    def get_items(self, **kwargs):
        from tmdbhelper.lib.items.pages import PaginatedItems
        self.container_content = convert_type('episode', 'container')
        self.plugin_category = f'{get_localized(32459)}'
        paginated_items = PaginatedItems(self.get_cache_items(), page=kwargs.get('page', 1), limit=20)
        return paginated_items.items + paginated_items.next_page
