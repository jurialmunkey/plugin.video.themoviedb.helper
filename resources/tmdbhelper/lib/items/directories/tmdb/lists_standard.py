from tmdbhelper.lib.items.directories.lists_default import ListDefault, ListProperties
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property


class UncachedItemsPage:
    def __init__(self, outer_class, page):
        self.outer_class = outer_class
        self.page = page

    @cached_property
    def response(self):
        return self.outer_class.get_api_response(self.page)

    @cached_property
    def results(self):
        return self.get_results()

    def get_results(self):
        try:
            results = self.response[self.outer_class.results_key]
        except (TypeError, KeyError):
            return []
        try:
            self.outer_class.total_pages = self.response['total_pages']
            self.outer_class.total_items = self.response['total_results']
        except (TypeError, KeyError):
            self.outer_class.total_pages = 0
            self.outer_class.total_items = 0
        return results

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        return [j for j in [
            self.outer_class.get_mapped_item(i, add_infoproperties=(
                ('total_pages', self.outer_class.total_pages),
                ('total_results', self.outer_class.total_items),
                ('rank', x),
            ))
            for x, i in enumerate(self.results, 1) if i
        ] if j]


class ListStandardProperties(ListProperties):

    total_pages = 0
    total_items = 0
    class_pages = UncachedItemsPage

    @property
    def next_page(self):
        return self.page + self.pmax

    def get_api_response(self, page=1):
        return self.tmdb_api.get_response_json(self.url, page=page)

    def get_uncached_items(self):
        return {
            'items': [
                i for xpage in range(self.page, self.next_page)
                for i in self.class_pages(self, xpage).items
            ],
            'pages': self.total_pages,
            'count': self.total_items,
        }

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.tmdb_api.mapper.get_info(
            item,
            item.get('media_type') or self.tmdb_type,
            add_infoproperties=add_infoproperties)


class ListStandard(ListDefault):
    list_properties_class = ListStandardProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.page_length = get_setting('pagemulti_tmdb', 'int') or 1
        return list_properties


class ListPopular(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/popular'
        list_properties.localize = 32175
        return list_properties


class ListTopRated(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/top_rated'
        list_properties.localize = 32176
        return list_properties


class ListUpcoming(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/upcoming'
        list_properties.localize = 32177
        return list_properties


class ListTrendingDay(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'trending/{tmdb_type}/day'
        list_properties.plugin_name = '{plural} {localized}'
        list_properties.localize = 32178
        return list_properties


class ListTrendingWeek(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'trending/{tmdb_type}/week'
        list_properties.plugin_name = '{plural} {localized}'
        list_properties.localize = 32179
        return list_properties


class ListInTheatres(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/now_playing'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32180
        return list_properties


class ListAiringToday(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/airing_today'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32181
        return list_properties


class ListCurrentlyAiring(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{tmdb_type}/on_the_air'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32182
        return list_properties


class ListRevenue(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'discover/{tmdb_type}?sort_by=revenue.desc'
        list_properties.localize = 32184
        return list_properties


class ListMostVoted(ListStandard):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'discover/{tmdb_type}?sort_by=vote_count.desc'
        list_properties.localize = 32185
        return list_properties
