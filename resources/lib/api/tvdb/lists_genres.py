from resources.lib.addon.plugin import get_localized, convert_type
from resources.lib.api.tvdb.lists import ListLists
from resources.lib.items.container import Container
from resources.lib.items.pages import PaginatedItems


class ListGenres(ListLists):
    def get_items(self, info, tmdb_type, **kwargs):
        self.plugin_category = get_localized(135)
        items = self._get_items('genres', 'tvdb_genre', params={'tmdb_type': tmdb_type})
        return sorted(items, key=lambda x: x.get('label') or 0)


class ListGenre(Container):
    def get_items(self, info, tvdb_id, tmdb_type, page=1, **kwargs):
        from resources.lib.addon.thread import ParallelThread
        try:
            tvdb_type = {'movie': 'movies', 'tv': 'series'}[tmdb_type]
        except KeyError:
            return
        mediatype = convert_type(tmdb_type, 'dbtype')
        data = self.tvdb_api.get_request_lc(tvdb_type, 'filter', genre=tvdb_id, sort='score', sortType='desc')
        if not data:
            return

        tmdb_type = 'movie'

        def _get_item(i):
            item = self.tvdb_api.mapper.get_info(i, tmdb_type=tmdb_type)
            item['infolabels']['mediatype'] = mediatype
            item['unique_ids']['tmdb'] = self.tmdb_api.get_tmdb_id(
                tmdb_type=tmdb_type,
                tvdb_id=item['unique_ids'].get('tvdb') if tmdb_type == 'tv' else None,
                query=item['infolabels'].get('title') if tmdb_type == 'movie' else None,
                year=item['infolabels'].get('year') if tmdb_type == 'movie' else None)
            return item

        response = PaginatedItems(data, page=page)
        if not response or not response.items:
            return
        with ParallelThread(response.items, _get_item) as pt:
            item_queue = pt.queue
        items = [i for i in item_queue if i]

        self.library = convert_type(tmdb_type, 'library')
        self.container_content = convert_type(tmdb_type, 'container')
        self.plugin_category = get_localized(135)
        return items + response.next_page
