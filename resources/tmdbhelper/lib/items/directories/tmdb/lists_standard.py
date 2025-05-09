from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory, use_item_cache
from tmdbhelper.lib.addon.plugin import convert_type, get_localized, get_setting, get_condvisibility
from tmdbhelper.lib.items.filters import is_excluded
from jurialmunkey.parser import try_int


ITEMS_LENGTH = 20
PAGES_LENGTH = get_setting('pagemulti_tmdb', 'int') or 1


class ListStandard(ContainerDefaultCacheDirectory):
    item_list_request_url = ''  # PATH to request
    item_list_results_key = 'results'  # KEY in RESPONSE from PATH holding ITEMS
    item_list_plugin_name = '{localized} {plural}'
    item_list_dbid_sorted = False
    item_list_localize = None
    item_list_sorted_reversed = False
    item_list_sorted_function = None
    item_list_length = None  # Override user setting for length
    item_list_tmdb_type = None  # Override type for items (e.g. for related lists that get a different type to source)

    def get_plugin_category(self, plural=''):
        localized = get_localized(self.item_list_localize) if self.item_list_localize else ''
        return self.item_list_plugin_name.format(localized=localized, plural=plural)

    @staticmethod
    def paginated_items(items, page=1, length=PAGES_LENGTH, total_pages=None):
        if total_pages and (page + length - 1) < total_pages:
            items.append({'next_page': page + length})
            return items

        return items

    def get_mapped_item(self, item, tmdb_type, add_infoproperties=None):
        return self.tmdb_api.mapper.get_info(
            item,
            item.get('media_type') or tmdb_type,
            add_infoproperties=add_infoproperties)

    def get_cached_items_page_configured(self, response, tmdb_type):
        def items_page(items=None, pages=None, total=None):
            return {
                'items': items or [],
                'pages': pages,
                'total': total
            }

        try:
            results = response[self.item_list_results_key]
        except (TypeError, KeyError):
            return items_page()
        try:
            pages = response['total_pages']
            total = response['total_results']
        except (TypeError, KeyError):
            pages, total = None, None

        add_infoproperties = [
            ('total_pages', pages),
            ('total_results', total),
        ]

        if not results:
            return items_page()

        return items_page(
            items=[
                self.get_mapped_item(i, tmdb_type, add_infoproperties=add_infoproperties)
                for i in results if i
            ],
            pages=pages,
            total=total,
        )

    @use_item_cache('ItemContainer.db')
    def get_cached_items_page(self, *args, **kwargs):
        return self._get_cached_items_page(*args, **kwargs)

    def _get_cached_items_page(self, request_url, tmdb_type, page=1):
        response = self.tmdb_api.get_response_json(request_url, page=page)
        return self.get_cached_items_page_configured(response, tmdb_type)

    @use_item_cache('ItemContainer.db')
    def get_cached_items(self, *args, **kwargs):
        return self._get_cached_items(*args, **kwargs)

    def _get_cached_items(self, request_url, tmdb_type, page=1, length=PAGES_LENGTH, paginated=True):
        items = []
        pages = 0

        for x in range(page, page + length):
            ipage = self.get_cached_items_page(request_url, tmdb_type, x)
            pages = ipage['pages']
            items.extend(ipage['items'])

        if not paginated:
            return items

        return self.paginated_items(items, page, length, pages)

    def get_request_url(self, tmdb_type, **kwargs):
        return self.item_list_request_url.format(tmdb_type=tmdb_type)

    def get_items(self, tmdb_type, page=1, length=PAGES_LENGTH, **kwargs):
        request_url = self.get_request_url(tmdb_type=tmdb_type, **kwargs)
        items = self.get_cached_items(
            request_url,
            self.item_list_tmdb_type or tmdb_type,
            page=try_int(page) or 1,
            length=self.item_list_length or try_int(length) or PAGES_LENGTH,
            paginated=self.pagination)
        return self.get_items_finalised(items, self.item_list_tmdb_type or tmdb_type)

    def get_items_finalised(self, items, tmdb_type):
        self.kodi_db = self.get_kodi_database(tmdb_type)
        self.container_content = convert_type(tmdb_type, 'container', items=items)
        self.plugin_category = self.get_plugin_category(convert_type(tmdb_type, 'plural'))
        self.sort_by_dbid = True if self.kodi_db and self.item_list_dbid_sorted else False
        items = [i for i in items if not is_excluded(i, **self.filters)] if self.filters else items
        if not self.item_list_sorted_function:
            return items
        return sorted(items, key=self.item_list_sorted_function, reverse=self.item_list_sorted_reversed)


class ListPopular(ListStandard):
    item_list_request_url = '{tmdb_type}/popular'
    item_list_localize = 32175


class ListTopRated(ListStandard):
    item_list_request_url = '{tmdb_type}/top_rated'
    item_list_localize = 32176


class ListUpcoming(ListStandard):
    item_list_request_url = '{tmdb_type}/upcoming'
    item_list_localize = 32177


class ListTrendingDay(ListStandard):
    item_list_request_url = 'trending/{tmdb_type}/day'
    item_list_plugin_name = '{plural} {localized}'
    item_list_localize = 32178


class ListTrendingWeek(ListStandard):
    item_list_request_url = 'trending/{tmdb_type}/week'
    item_list_plugin_name = '{plural} {localized}'
    item_list_localize = 32179


class ListInTheatres(ListStandard):
    item_list_request_url = '{tmdb_type}/now_playing'
    item_list_plugin_name = '{localized}'
    item_list_localize = 32180


class ListAiringToday(ListStandard):
    item_list_request_url = '{tmdb_type}/airing_today'
    item_list_plugin_name = '{localized}'
    item_list_localize = 32181


class ListCurrentlyAiring(ListStandard):
    item_list_request_url = '{tmdb_type}/on_the_air'
    item_list_plugin_name = '{localized}'
    item_list_localize = 32182


class ListRevenue(ListStandard):
    item_list_request_url = 'discover/{tmdb_type}?sort_by=revenue.desc'
    item_list_localize = 32184


class ListMostVoted(ListStandard):
    item_list_request_url = 'discover/{tmdb_type}?sort_by=vote_count.desc'
    item_list_localize = 32185
