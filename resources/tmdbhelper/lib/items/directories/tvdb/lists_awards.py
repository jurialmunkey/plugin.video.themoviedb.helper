from tmdbhelper.lib.items.directories.tvdb.mapper_static import TVDbStaticAwardsItemMapper, TVDbStaticAwardCategoriesItemMapper
from tmdbhelper.lib.items.directories.tvdb.lists_tvdb import ListTVDbProperties, ListTVDbMediaProperties
from tmdbhelper.lib.items.directories.lists_default import ListDefault
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property


class ListTVDbAwardsProperties(ListTVDbProperties):
    item_mapper_class = TVDbStaticAwardsItemMapper


class ListTVDbAwardCategoriesProperties(ListTVDbProperties):
    item_mapper_class = TVDbStaticAwardCategoriesItemMapper


class ListAwards(ListDefault):
    list_properties_class = ListTVDbAwardsProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32460
        list_properties.plugin_name = '{localized}'
        list_properties.tvdb_api = self.tvdb_api
        list_properties.results_key = None
        list_properties.request_url = 'awards'
        list_properties.page_length = 4
        return list_properties

    def get_items(self, tmdb_type=None, **kwargs):
        return super().get_items(tmdb_type=tmdb_type, **kwargs)


class ListAwardCategories(ListAwards):
    list_properties_class = ListTVDbAwardCategoriesProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32460
        list_properties.results_key = 'categories'
        list_properties.request_url = 'awards/{tvdb_id}/extended'
        return list_properties

    def get_items(self, tvdb_id, **kwargs):
        self.list_properties.request_url_params = {'tvdb_id': tvdb_id}
        return super().get_items(**kwargs)


class ListTVDbAwardCategoryProperties(ListTVDbMediaProperties):
    @cached_property
    def award_category(self):
        return self.request.get('name')

    @cached_property
    def award_category_id(self):
        return self.request.get('id')

    @cached_property
    def award_type(self):
        return self.request.get('award', {}).get('name')

    @cached_property
    def award_type_id(self):
        return self.request.get('award', {}).get('id')

    @cached_property
    def add_infoproperties(self):
        return (
            ('award_category', self.award_category),
            ('award_category_id', self.award_category_id),
            ('award_type', self.award_type),
            ('award_type_id', self.award_type_id),
        )


class ListAwardCategory(ListAwards):

    list_properties_class = ListTVDbAwardCategoryProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32460
        list_properties.sorting_rev = True
        list_properties.sorting_key = lambda x: x.get('year') or 9999
        list_properties.results_key = 'nominees'
        list_properties.request_url = 'awards/categories/{tvdb_id}/extended'
        list_properties.page_length = get_setting('pagemulti_trakt', 'int') or 1
        return list_properties

    def get_items(self, tvdb_id, **kwargs):
        self.list_properties.request_url_params = {'tvdb_id': tvdb_id}
        return super().get_items(**kwargs)
