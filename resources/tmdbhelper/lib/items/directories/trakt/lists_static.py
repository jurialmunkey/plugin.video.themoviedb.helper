from tmdbhelper.lib.items.directories.trakt.lists_standard import (
    ListTraktStandard,
    ListTraktStandardProperties
)
from tmdbhelper.lib.items.directories.trakt.mapper_static import (
    StaticItemMapper,
    StaticUnLikedItemMapper,
    StaticLikedItemMapper,
    StaticOwnedItemMapper,
    StaticGenresItemMapper
)
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized


class ListTraktStaticProperties(ListTraktStandardProperties):

    container_content = ''
    item_mapper_class = StaticItemMapper
    query = None

    @property
    def url(self):
        return self.request_url.format(query=self.query)

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item

    @cached_property
    def plugin_category(self):
        return self.plugin_name.format(localized=self.localized, plural=self.plural, query=self.query)


class ListTraktStaticNoCacheProperties(ListTraktStaticProperties):
    def get_cached_items(self, *args, **kwargs):
        """ Divert cached to uncached """
        items = self.get_uncached_items(*args, **kwargs)
        return items


class ListTraktStaticOwnedNoCacheProperties(ListTraktStaticNoCacheProperties):
    def get_mapped_item(self, item, add_infoproperties=None):
        """ Owned lists are flatter so need to reconfigure to match config of other types """
        return super().get_mapped_item({'list': item}, add_infoproperties=add_infoproperties)


class ListTraktStaticListedProperties(ListTraktStaticProperties):
    @property
    def url(self):
        return self.request_url.format(
            trakt_type=self.trakt_type,
            trakt_slug=self.trakt_slug,
            trakt_sort=self.trakt_sort
        )

    def get_cache_name_list_prefix(self):
        return [self.class_name, self.tmdb_type, self.tmdb_id, self.trakt_sort]

    @cached_property
    def trakt_slug(self):
        return self.query_database.get_trakt_id(self.tmdb_id, 'tmdb', item_type=self.trakt_type, output_type='slug')

    def get_mapped_item(self, item, add_infoproperties=None):
        """ Listed lists are flatter so need to reconfigure to match config of other types """
        return super().get_mapped_item({'list': item}, add_infoproperties=add_infoproperties)


class ListTraktStaticGenresProperties(ListTraktStaticProperties):
    @property
    def url(self):
        return self.request_url.format(trakt_type=self.trakt_type)

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties, tmdb_type=self.tmdb_type).item


class ListTraktStatic(ListTraktStandard):
    default_cacheonly = True
    list_properties_class = ListTraktStaticProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.page_length = 5
        return list_properties

    def get_items_finalised(self):
        from xbmcplugin import SORT_METHOD_UNSORTED
        self.sort_methods = [{'sortMethod': SORT_METHOD_UNSORTED, 'label2Mask': '%U'}]  # By studio (ie username)
        return super().get_items_finalised()


class ListTraktStaticNoCache(ListTraktStatic):
    list_properties_class = ListTraktStaticNoCacheProperties


class ListTraktStaticOwnedNoCache(ListTraktStatic):
    list_properties_class = ListTraktStaticOwnedNoCacheProperties


class ListTraktStaticTrending(ListTraktStatic):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticUnLikedItemMapper
        list_properties.request_url = 'lists/trending'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32208
        return list_properties


class ListTraktStaticPopular(ListTraktStatic):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticUnLikedItemMapper
        list_properties.request_url = 'lists/popular'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32209
        return list_properties


class ListTraktStaticUsers(ListTraktStaticOwnedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticOwnedItemMapper
        list_properties.request_url = 'users/{user_slug}/lists'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32524
        return list_properties

    def get_items(self, *args, user_slug=None, **kwargs):
        self.list_properties.request_url = f'users/{user_slug}/lists'
        self.list_properties.plugin_name = f'{{localized}} ({user_slug})'
        return super().get_items(*args, **kwargs)


class ListTraktStaticLiked(ListTraktStaticNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticLikedItemMapper
        list_properties.trakt_authorization = True
        list_properties.request_url = 'users/likes/lists'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32210
        return list_properties


class ListTraktStaticOwned(ListTraktStaticOwnedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticOwnedItemMapper
        list_properties.trakt_authorization = True
        list_properties.request_url = 'users/me/lists'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32211
        return list_properties


class ListTraktStaticSearch(ListTraktStaticNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticUnLikedItemMapper
        list_properties.trakt_authorization = True
        list_properties.request_url = 'search/list?query={query}&fields=name'
        list_properties.plugin_name = '{localized} ({query})'
        list_properties.localize = 32361
        return list_properties

    def get_items(self, *args, query=None, **kwargs):
        from xbmcgui import Dialog
        self.list_properties.query = query or Dialog().input(get_localized(32044))
        return super().get_items(*args, **kwargs)


class ListTraktStaticListed(ListTraktStatic):

    list_properties_class = ListTraktStaticListedProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticUnLikedItemMapper
        list_properties.request_url = '{trakt_type}s/{trakt_slug}/lists/personal/{trakt_sort}'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32232
        return list_properties

    def get_items(self, *args, tmdb_id, sort_by=None, **kwargs):
        self.list_properties.tmdb_id = tmdb_id
        self.list_properties.trakt_sort = sort_by or 'popular'
        return super().get_items(*args, **kwargs)


class ListTraktStaticGenres(ListTraktStatic):

    list_properties_class = ListTraktStaticGenresProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticGenresItemMapper
        list_properties.request_url = 'genres/{trakt_type}s'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 135
        return list_properties
