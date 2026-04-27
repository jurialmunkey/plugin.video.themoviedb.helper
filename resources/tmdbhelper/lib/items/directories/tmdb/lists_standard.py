from tmdbhelper.lib.items.directories.lists_default import UncachedItemsPage, ListDefault, ListProperties
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property


class ListStandardProperties(ListProperties):

    total_pages = 0
    total_items = 0
    class_pages = UncachedItemsPage

    @property
    def next_page(self):
        return self.page + self.pmax

    def get_api_response(self, page=1):
        return self.tmdb_api.get_response_json(self.url, page=page)

    @cached_property
    def final_items(self):
        return [
            i for xpage in range(self.page, self.next_page)
            for i in self.class_pages(self, xpage).items
        ]

    def get_uncached_items(self):
        return {
            'items': self.final_items,
            'pages': self.total_pages,
            'count': self.total_items,
        }

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.tmdb_api.mapper.get_info(
            item,
            item.get('media_type') or self.tmdb_type,
            add_infoproperties=add_infoproperties)


class ListStandardLocalProperties(ListStandardProperties):
    page_limit = 8
    item_limit = 20

    @cached_property
    def cache_name_tuple(self):
        return (
            'local_items',
            self.class_name,
            self.tmdb_type,
            self.page,
            self.page_limit,
            self.item_limit,
        )

    # Possible method to get next page but need to account for item offset
    # Might not be worthwhile as too hacky
    # @cached_property
    # def next_page(self):
    #     return next(self.next_page_generator, self.page + self.page_limit + 1)

    @property
    def next_page(self):
        return self.pages + 1  # Override next page object by making next_page out of bounds

    @cached_property
    def next_page_generator(self):
        return (x for x in range(self.page, self.page + self.page_limit))

    @cached_property
    def kodi_db(self):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        return get_kodi_library(self.tmdb_type)

    def get_dbid(self, item):
        if not self.kodi_db:
            return
        try:
            unique_ids = item['unique_ids']
            infolabels = item['infolabels']
        except (KeyError, TypeError):
            return
        return self.kodi_db.get_info(
            info='dbid',
            imdb_id=unique_ids.get('imdb'),
            tmdb_id=unique_ids.get('tmdb'),
            tvdb_id=unique_ids.get('tvdb'),
            originaltitle=infolabels.get('originaltitle'),
            title=infolabels.get('title'),
            year=infolabels.get('year')
        )

    @cached_property
    def item_generator(self):
        return (
            i for xpage in self.next_page_generator
            for i in self.class_pages(self, xpage).items
            if i and self.get_dbid(i)
        )

    @cached_property
    def final_items(self):
        final_items = []
        for x, i in enumerate(self.item_generator):
            if x >= self.item_limit:
                break
            final_items.append(i)
        return final_items


class ListStandard(ListDefault):

    @property
    def list_properties_class(self):
        if not self.is_localonly:
            return ListStandardProperties
        return ListStandardLocalProperties

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
