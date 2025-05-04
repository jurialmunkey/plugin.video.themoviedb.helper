from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.items.directories.tmdb.lists_view import ItemViews
from tmdbhelper.lib.files.ftools import cached_property


class ListRelated(ListStandard):
    def get_request_url(self, tmdb_type, tmdb_id, **kwargs):
        return self.item_list_request_url.format(tmdb_type=tmdb_type, tmdb_id=tmdb_id)


class ListRecommendations(ListRelated):
    item_list_plugin_name = '{localized}'  # TODO: BASED ON {item}
    item_list_dbid_sorted = True
    item_list_request_url = '{tmdb_type}/{tmdb_id}/recommendations'
    item_list_localize = 32223
    item_list_length = 2  # Recommendations only have 2 pages


class ListSimilar(ListRelated):
    item_list_plugin_name = '{localized}'  # TODO: BASED ON {item}
    item_list_dbid_sorted = True
    item_list_request_url = '{tmdb_type}/{tmdb_id}/similar'
    item_list_localize = 32224


class ListCollection(ListRelated):
    # TODO: Move this to a BaseView instead of a lookup
    item_list_plugin_name = '{localized}'
    item_list_request_url = 'collection/{tmdb_id}'
    item_list_results_key = 'parts'
    item_list_tmdb_type = 'movie'
    item_list_localize = 32192
    item_list_length = 1  # Collections come as one page

    @staticmethod
    def item_list_sorted_function(i):
        try:
            return i['infolabels']['premiered']
        except (KeyError, AttributeError, TypeError):
            return ''


class ListReviews(ListRelated):
    item_list_plugin_name = '{localized}'  # TODO: BASED ON {item}
    item_list_dbid_sorted = True
    item_list_request_url = '{tmdb_type}/{tmdb_id}/reviews'
    item_list_tmdb_type = 'review'
    item_list_localize = 32188


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
    item_list_plugin_name = '{localized}'  # TODO: BASED ON {item}
    item_list_request_url = 'movie/{tmdb_id}/keywords'
    item_list_results_key = 'keywords'
    item_list_tmdb_type = 'keyword'
    item_list_localize = 21861

    def get_mapped_item(self, item, *args, **kwargs):
        return ItemKeywords(item).item
