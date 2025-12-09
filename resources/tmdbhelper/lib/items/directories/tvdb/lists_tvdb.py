from tmdbhelper.lib.items.directories.tvdb.mapper_static import TVDbStaticItemMapper
from tmdbhelper.lib.items.directories.tvdb.mapper_items import TVDbAwardItemMapper
from tmdbhelper.lib.items.directories.lists_default import ListSliceProperties
from jurialmunkey.ftools import cached_property


class ListTVDbProperties(ListSliceProperties):
    item_mapper_class = TVDbStaticItemMapper
    unconfigured_item_data = None
    sorting_key = None
    sorting_rev = False

    @cached_property
    def plugin_category(self):
        plugin_category = self.request.get('name') if isinstance(self.request, dict) else None
        plugin_category = plugin_category or self.plugin_name.format(localized=self.localized, plural=self.plural)
        return plugin_category

    @cached_property
    def request(self):
        return self.tvdb_api.get_request_lc(self.url, **self.request_url_kwargs)

    @cached_property
    def results(self):
        return self.request[self.results_key] if self.request and self.results_key else self.request

    def get_uncached_items(self):
        items = [i for i in [self.item_mapper_class(meta, None).item for meta in (self.results or [])] if i]
        return items

    @cached_property
    def request_url_params(self):
        """ for formatting url path """
        return {}

    @cached_property
    def request_url_kwargs(self):
        """ additional kwargs to add to request """
        return {}

    @cached_property
    def url(self):
        return self.request_url.format(**self.request_url_params)

    @cached_property
    def sorted_items(self):
        sorted_items = self.filtered_items
        sorted_items = sorted(sorted_items, key=self.sorting_key, reverse=self.sorting_rev) if self.sorting_key else sorted_items
        return sorted_items[self.item_a:self.item_z]


class ListTVDbMediaProperties(ListTVDbProperties):
    item_mapper_class = staticmethod(TVDbAwardItemMapper)
    add_infoproperties = None

    @cached_property
    def cache_name(self):
        cache_name_list = [f'{k}={v}' for k, v in self.request_url_kwargs.items()]
        cache_name_list = sorted(cache_name_list)
        cache_name_list = [self.class_name, self.url] + cache_name_list
        return '_'.join(cache_name_list)

    @cached_property
    def request(self):
        request = self.tvdb_api.get_request_lc(self.url, **self.request_url_kwargs)
        return request

    def get_uncached_items(self):
        return self.results or []

    def get_mapped_item(self, item):
        mapped_item = self.item_mapper_class(item, self.add_infoproperties)
        return mapped_item.item if mapped_item.tmdb_id else None

    def get_mapped_items(self, sorted_items):
        from tmdbhelper.lib.addon.thread import ParallelThread
        with ParallelThread(sorted_items, self.get_mapped_item) as pt:
            mapped_items = pt.queue
        return [i for i in mapped_items if i]

    @cached_property
    def sorted_items(self):
        sorted_items = self.filtered_items
        sorted_items = sorted(sorted_items, key=self.sorting_key, reverse=self.sorting_rev) if self.sorting_key else sorted_items
        sorted_items = sorted_items[self.item_a:self.item_z]
        return self.get_mapped_items(sorted_items)
