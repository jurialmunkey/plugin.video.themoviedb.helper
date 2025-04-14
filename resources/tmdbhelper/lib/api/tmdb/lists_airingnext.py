from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.addon.plugin import convert_type, get_localized, get_setting
from tmdbhelper.lib.addon.dialog import progress_bg


class ListAiringNext(ContainerDirectory):

    @progress_bg
    def get_list_items(self, seed_items: list, prefix: str, reverse: bool = False, **kwargs):
        from tmdbhelper.lib.addon.thread import ParallelThread
        from tmdbhelper.lib.addon.tmdate import date_in_range, is_future_timestamp
        from tmdbhelper.lib.api.mapping import get_empty_item

        self.dialog_progress_bg.update(0, message=f'Initialising')

        _cache = self.tmdb_api.get_special_cache('TMDbListAiringNext.db')

        self._get_list_items_progress_max = len(seed_items)
        self._get_list_items_progress_now = 0

        class _ParallelThread(ParallelThread):
            thread_max = min(get_setting('max_threads', mode='int') or 50, 50)

        def _get_nextaired_item(tmdb_id):
            cache_name = f'{prefix}.{tmdb_id}'
            cache_item = _cache.get_cache(cache_name)
            if cache_item:
                return cache_item

            ip = self.tmdb_api.get_tvshow_nextaired(tmdb_id)
            if not ip:
                return

            item_airdate = ip.get(f'{prefix}.original')
            if not item_airdate:
                return

            status = ip.get('status')
            if status in ['Canceled', 'Ended']:
                cache_days = 30  # Check in a month just in case gets renewed on another network
            elif date_in_range(item_airdate, 10, -2, date_fmt="%Y-%m-%d", date_lim=10):
                cache_days = 1  # Item airing this week so check again tomorrow in case schedule changes
            else:
                cache_days = 7  # Item airing in more than a week so let's check next week just in case of changes

            item = get_empty_item()
            item['infoproperties'] = ip
            item['infolabels']['mediatype'] = 'episode'
            item['infolabels']['title'] = ip.get(f'{prefix}.name')
            item['infolabels']['episode'] = ip.get(f'{prefix}.episode')
            item['infolabels']['season'] = ip.get(f'{prefix}.season')
            item['infolabels']['plot'] = ip.get(f'{prefix}.plot')
            item['infolabels']['year'] = ip.get(f'{prefix}.year')
            item['infolabels']['premiered'] = item_airdate
            item['art']['thumb'] = ip.get(f'{prefix}.thumb')
            item['label'] = f"{item['infolabels']['title']} ({item_airdate})"
            item['infoproperties']['tmdb_type'] = 'episode'
            item['infoproperties']['tmdb_id'] = item['unique_ids']['tvshow.tmdb'] = tmdb_id
            item['params'] = {
                'info': 'details',
                'tmdb_type': 'tv',
                'tmdb_id': tmdb_id,
                'episode': item['infolabels']['episode'],
                'season': item['infolabels']['season']}
            return _cache.set_cache(item, cache_name=cache_name, cache_days=cache_days)

        def _get_nextaired_item_thread(i):
            tmdb_id = i.get('tmdb_id') or self.tmdb_api.get_tmdb_id(
                tmdb_type='tv', imdb_id=i.get('imdb_id'), tvdb_id=i.get('tvdb_id'),
                query=i.get('showtitle') or i.get('title'), year=i.get('year'))

            if not tmdb_id:
                self._get_list_items_progress_now += 1
                return

            item = _get_nextaired_item(tmdb_id)

            self.dialog_progress_bg.update(
                int((self._get_list_items_progress_now / self._get_list_items_progress_max) * 100),
                message=f'{tmdb_id} - Checking TMDb ID')

            if not item:
                self._get_list_items_progress_now += 1
                return

            self._get_list_items_progress_now += 1
            item['infolabels']['tvshowtitle'] = i.get('showtitle') or i.get('title')
            return item

        with _ParallelThread(seed_items, _get_nextaired_item_thread) as pt:
            item_queue = pt.queue

        self.dialog_progress_bg.update(99, message=f'Sorting items')

        items = [
            i for i in item_queue if i
            and is_future_timestamp(
                i['infoproperties'].get(f'{prefix}.original'),
                time_fmt="%Y-%m-%d", time_lim=10, days=-1)]

        return sorted(items, key=lambda i: i['infoproperties'][f'{prefix}.original'], reverse=reverse)


class ListLibraryAiringNext(ListAiringNext):

    def get_items(self, **kwargs):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        from tmdbhelper.lib.items.pages import PaginatedItems

        kodi_db = get_kodi_library('tv')
        if not kodi_db or not kodi_db.database:
            return

        self.ib.cache_only = self.tmdb_cache_only = False
        self.container_content = convert_type('episode', 'container')

        self.plugin_category = f'{get_localized(32458)}'

        cache = self.tmdb_api.get_special_cache('TMDbListAiringNext.db')
        items = cache.use_cache(
            self.get_list_items, kodi_db.database, 'next_aired',
            cache_name='all_items_list_library',
            cache_days=0.02,  # Cache for approx 30 minutes
            **kwargs)

        paginated_items = PaginatedItems(items, page=kwargs.get('page', 1), limit=20)
        return paginated_items.items + paginated_items.next_page


class ListTraktAiringNext(ListAiringNext):

    def get_items(self, **kwargs):
        from tmdbhelper.lib.items.pages import PaginatedItems

        sd = self.trakt_api.trakt_syncdata.get_all_unhidden_shows_started_getter()
        sd.items

        items = sd.items
        if not items:
            return
        items = [{'tmdb_id': i[sd.keys.index('tmdb_id')]} for i in items if i]
        if not items:
            return

        self.ib.cache_only = self.tmdb_cache_only = False
        self.container_content = convert_type('episode', 'container')

        self.plugin_category = f'{get_localized(32459)}'

        cache = self.tmdb_api.get_special_cache('TMDbListAiringNext.db')
        items = cache.use_cache(
            self.get_list_items, items, 'next_aired',
            cache_name='all_items_list_trakt',
            cache_days=0.02,  # Cache for approx 30 minutes
            **kwargs)

        paginated_items = PaginatedItems(items, page=kwargs.get('page', 1), limit=20)
        return paginated_items.items + paginated_items.next_page
