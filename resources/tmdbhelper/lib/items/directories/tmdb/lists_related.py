from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties
from tmdbhelper.lib.items.directories.tmdb.lists_allitems import ItemKeywords, ItemReviews
from jurialmunkey.ftools import cached_property


class ListRelatedProperties(ListStandardProperties):
    @cached_property
    def url(self):
        return self.request_url.format(tmdb_type=self.tmdb_type, tmdb_id=self.tmdb_id)

    @cached_property
    def cache_name_tuple(self):
        return (
            self.class_name,
            self.tmdb_type,
            self.tmdb_id,
            self.page,
            self.pmax
        )


class ListRelated(ListStandard):
    list_properties_class = ListRelatedProperties

    def get_items(self, *args, tmdb_id=None, **kwargs):
        self.list_properties.tmdb_id = tmdb_id
        return super().get_items(*args, **kwargs)


class ListRecommendations(ListRelated):

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'  # TODO: BASED ON {item}
        list_properties.dbid_sorted = True
        list_properties.request_url = '{tmdb_type}/{tmdb_id}/recommendations'
        list_properties.localize = 32223
        list_properties.page_length = 2  # Recommendations only have 2 pages
        list_properties.length = 2
        return list_properties


class ListSimilar(ListRelated):

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'  # TODO: BASED ON {item}
        list_properties.dbid_sorted = True
        list_properties.request_url = '{tmdb_type}/{tmdb_id}/similar'
        list_properties.localize = 32224
        return list_properties


class ListReviews(ListRelated):

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'  # TODO: BASED ON {item}
        list_properties.dbid_sorted = True
        list_properties.request_url = '{tmdb_type}/{tmdb_id}/reviews'
        list_properties.tmdb_type = 'review'
        list_properties.localize = 32188
        return list_properties

    def get_mapped_item(self, item, *args, **kwargs):
        return ItemReviews(**item).item


class ListKeywords(ListRelated):

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'  # TODO: BASED ON {item}
        list_properties.request_url = 'movie/{tmdb_id}/keywords'
        list_properties.results_key = 'keywords'
        list_properties.tmdb_type = 'keyword'
        list_properties.localize = 21861
        return list_properties

    def get_mapped_item(self, item, *args, **kwargs):
        return ItemKeywords(**item).item
