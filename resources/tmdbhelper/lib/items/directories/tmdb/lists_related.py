from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.items.directories.tmdb.lists_view import ItemViews
from tmdbhelper.lib.files.ftools import cached_property


class ListRelated(ListStandard):
    def get_request_url(self, tmdb_type, tmdb_id, **kwargs):
        return self.list_properties.request_url.format(tmdb_type=tmdb_type, tmdb_id=tmdb_id)


class ListRecommendations(ListRelated):

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'  # TODO: BASED ON {item}
        list_properties.dbid_sorted = True
        list_properties.request_url = '{tmdb_type}/{tmdb_id}/recommendations'
        list_properties.localize = 32223
        list_properties.length = 2  # Recommendations only have 2 pages
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


class ItemKeywords(ItemViews):
    item_mediatype = 'keyword'
    tmdb_type = 'movie'

    def __init__(self, meta):
        self.meta = meta
        self.label = self.meta['name']
        self.tmdb_id = self.meta['id']

    @cached_property
    def params(self):
        return {
            'info': 'discover',
            'tmdb_type': self.tmdb_type,
            'with_keywords': self.tmdb_id,
            'with_id': 'True'
        }


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
        return ItemKeywords(item).item
