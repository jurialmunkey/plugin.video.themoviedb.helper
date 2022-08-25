from resources.lib.items.container import Container
from resources.lib.addon.plugin import get_localized, convert_media_type
from resources.lib.items.pages import PaginatedItems
from resources.lib.api.tvdb.lists import ListLists


class ListAwards(ListLists):
    def get_items(self, info, **kwargs):
        self.plugin_category = get_localized(32460)
        return self._get_items('awards', 'dir_tvdb_award_categories')


class ListAwardCategories(ListLists):
    def get_items(self, info, tvdb_id, **kwargs):
        items = self._get_items(f'awards/{tvdb_id}/extended', 'tvdb_award_category', key='categories')
        self.plugin_category = self.plugin_category or get_localized(32460)
        return items


class ListAwardCategory(Container):
    def get_items(self, info, tvdb_id, page=1, **kwargs):
        from resources.lib.addon.thread import ParallelThread
        data = self.tvdb_api.get_request_lc('awards', 'categories', tvdb_id, 'extended')
        if not data or not data.get('nominees'):
            return

        award_category = data.get('name')
        award_category_id = data.get('id')
        award_type = data.get('award', {}).get('name')
        award_type_id = data.get('award', {}).get('id')

        def _get_item(i):
            item = self.tvdb_api.mapper.get_type(i)
            if not item:
                return
            item = self.tvdb_api.mapper.get_info(item)
            tmdb_type = convert_media_type(item['infolabels'].get('mediatype'))
            item['infoproperties']['award_category'] = award_category
            item['infoproperties']['award_category_id'] = award_category_id
            item['infoproperties']['award_type'] = award_type
            item['infoproperties']['award_type_id'] = award_type_id
            item['unique_ids']['tmdb'] = self.tmdb_api.get_tmdb_id(
                tmdb_type=tmdb_type,
                tvdb_id=item['unique_ids'].get('tvdb') if tmdb_type == 'tv' else None,
                query=item['infolabels'].get('title') if tmdb_type == 'movie' else None,
                year=item['infolabels'].get('year') if tmdb_type == 'movie' else None)
            item['infolabels']['plot'] = f"{get_localized(32461) if i.get('isWinner') else get_localized(32462)} {award_category} {i.get('year')}. {item['infolabels'].get('plot', '')}"
            return item

        response = PaginatedItems(sorted(data['nominees'], key=lambda i: i.get('year') or 9999, reverse=True), page=page)
        if not response or not response.items:
            return
        with ParallelThread(response.items, _get_item) as pt:
            item_queue = pt.queue
        items = [i for i in item_queue if i]

        # Figure out container type based on counts of mediatypes
        mediatypes = {}
        for i in items:
            mediatypes.setdefault(i['infolabels']['mediatype'], []).append(i)
        info_mediatype = max(mediatypes, key=lambda k: len(mediatypes[k]))
        self.library = 'video'
        self.container_content = f'{info_mediatype}s'
        self.plugin_category = data.get('name') or get_localized(32460)
        return items + response.next_page
