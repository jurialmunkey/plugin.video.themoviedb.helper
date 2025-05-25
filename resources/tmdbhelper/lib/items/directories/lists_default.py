from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory, use_item_cache
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type, get_localized, get_setting
from tmdbhelper.lib.items.filters import is_excluded
from jurialmunkey.parser import try_int


ITEMS_LENGTH = 20
PAGES_LENGTH = get_setting('pagemulti_tmdb', 'int') or 1


class ListProperties:

    plugin_name = ''  # item_list_plugin_name
    localize = None  # item_list_localize
    tmdb_type = None
    items = None
    url = None
    params = {}

    @cached_property
    def plural(self):
        return convert_type(self.tmdb_type, 'plural')

    @cached_property
    def localized(self):
        return get_localized(self.localize) if self.localize else ''

    @cached_property
    def plugin_category(self):
        return self.plugin_name.format(localized=self.localized, plural=self.plural)

    @cached_property
    def container_content(self):
        return convert_type(self.tmdb_type, 'container', items=self.items)


class ListDefault(ContainerDefaultCacheDirectory):
    item_list_request_url = ''  # PATH to request
    item_list_results_key = 'results'  # KEY in RESPONSE from PATH holding ITEMS
    item_list_plugin_name = '{localized} {plural}'
    item_list_dbid_sorted = False
    item_list_localize = None
    item_list_sorted_reversed = False
    item_list_sorted_function = None
    item_list_length = None  # Override user setting for length

    @cached_property
    def item_list_tmdb_type(self):  # Override type for items (e.g. for related lists that get a different type to source)
        return self.params.get('tmdb_type')

    @cached_property
    def list_properties(self):
        lp = ListProperties()
        lp.plugin_name = self.item_list_plugin_name
        lp.localize = self.item_list_localize
        lp.tmdb_type = self.item_list_tmdb_type
        return lp

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

    def get_items(self, page=1, length=PAGES_LENGTH, **kwargs):
        self.list_properties.url = self.get_request_url(**kwargs)
        self.list_properties.page = try_int(page) or 1
        self.list_properties.length = self.item_list_length or try_int(length) or PAGES_LENGTH

        items = self.get_cached_items(
            self.list_properties.url,
            self.list_properties.tmdb_type,
            page=self.list_properties.page,
            length=self.list_properties.length,
            paginated=self.pagination)

        return self.get_items_finalised(items, self.list_properties.tmdb_type)

    @cached_property
    def sort_by_dbid(self):
        if not self.kodi_db:
            return False
        if not self.item_list_dbid_sorted:
            return False
        return True

    @cached_property
    def kodi_db(self):
        return self.get_kodi_database(self.list_properties.tmdb_type)

    def get_items_finalised(self, items, tmdb_type):
        self.list_properties.items = items
        self.container_content = self.list_properties.container_content
        self.plugin_category = self.list_properties.plugin_category
        items = [i for i in items if not is_excluded(i, **self.filters)] if self.filters else items
        if not self.item_list_sorted_function:
            return items
        return sorted(items, key=self.item_list_sorted_function, reverse=self.item_list_sorted_reversed)
