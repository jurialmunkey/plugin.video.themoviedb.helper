from tmdbhelper.lib.items.directories.lists_default import ListDefault
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.parser import try_int


PAGES_LENGTH = get_setting('pagemulti_tmdb', 'int') or 1


class ListStandard(ListDefault):

    def get_items(self, *args, length=None, **kwargs):
        return super().get_items(*args, length=try_int(length) or PAGES_LENGTH, **kwargs)

    def _get_cached_items(self, request_url, tmdb_type, page=1, length=None, paginated=True):
        items = []
        pages = 0

        for x in range(page, page + length):
            ipage = self.get_cached_items_page(request_url, tmdb_type, x)
            pages = ipage['pages']
            items.extend(ipage['items'])

        if not paginated:
            return items

        return self.paginated_items(items, page, length, pages)

    def _get_cached_items_page(self, request_url, tmdb_type, page=1):
        response = self.tmdb_api.get_response_json(request_url, page=page)
        return self.get_cached_items_page_configured(response, tmdb_type)

    @staticmethod
    def paginated_items(items, page=1, length=None, total_pages=None):
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
            results = response[self.list_properties.results_key]
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
