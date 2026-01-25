from tmdbhelper.lib.items.directories.lists_default import UncachedItemsPage, ListDefault, ListProperties
from tmdbhelper.lib.addon.plugin import get_setting

# Constants for library-only mode
LIBRARY_ONLY_MAX_PAGES = 10


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
        # Standard behavior when library_only is not active
        if not self.is_library_only or not self.library_tmdb_ids:
            return {
                'items': [
                    i for xpage in range(self.page, self.next_page)
                    for i in self.class_pages(self, xpage).items
                ],
                'pages': self.total_pages,
                'count': self.total_items,
            }

        # Library-only mode: accumulate pages until we have enough matches
        matching_items = []
        current_page = self.page
        pages_fetched = 0

        while pages_fetched < LIBRARY_ONLY_MAX_PAGES:
            page_data = self.class_pages(self, current_page)

            # No more pages available
            if not page_data.items:
                break
            if self.total_pages and current_page > self.total_pages:
                break

            # Filter items by library TMDb IDs
            for item in page_data.items:
                tmdb_id = str(item.get('unique_ids', {}).get('tmdb', ''))
                if tmdb_id and tmdb_id in self.library_tmdb_ids:
                    matching_items.append(item)
                    if len(matching_items) >= self.library_target_count:
                        break

            pages_fetched += 1
            current_page += 1

            # Stop if we have enough items
            if len(matching_items) >= self.library_target_count:
                break

        return {
            'items': matching_items,
            'pages': 0,  # No pagination for library-only
            'count': len(matching_items),
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
