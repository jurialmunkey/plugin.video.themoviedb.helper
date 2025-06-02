from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.baseclass import BaseList
from infotagger.listitem import _ListItemInfoTagVideo


class MediaList(BaseList):
    filters = {}
    sort_by = None
    sort_how = None
    cached_data_base_conditions = 'parent_id=?'
    item_mediatype = ''
    item_tmdb_type = ''
    item_label_key = 'name'
    item_alter_key = ''
    sort_direction = {}
    filter_key_map = {}
    filter_operator_map = {
        'lt': '<',
        'le': '<=',
        'eq': '=',
        'ne': '!=',
        'ge': '>=',
        'gt': '>',
        'in': None,
        'contains': None,
        None: None,
    }
    allowlist_infolabel_keys = _ListItemInfoTagVideo._tag_attr
    limit = None
    offset = None
    group_by = None

    @property
    def cached_data_conditions(self):  # WHERE CONDITIONS
        condition = self.cached_data_base_conditions
        condition = self.configure_filter_conditions(condition, **self.filters) if self.filters else condition
        condition = f'{condition} GROUP BY {self.group_by}' if self.group_by else condition
        condition = f'{condition} ORDER BY {self.order_by}' if self.order_by else condition
        condition = f'{condition} LIMIT {self.limit}' if self.limit else condition
        condition = f'{condition} OFFSET {self.offset}' if self.offset else condition
        return condition

    def configure_filter_conditions(self, condition, filter_key=None, filter_value=None, filter_operator=None, **kwargs):
        if filter_value == 'is_empty':  # Only evaluated on end product
            return condition
        if filter_key not in self.filter_key_map:  # Check we can actually filter DB by this value
            return condition
        if filter_operator not in self.filter_operator_map:  # Check that we support this operation in DB
            return condition
        filter_operator = self.filter_operator_map[filter_operator]
        if not filter_operator:
            return f'{self.filter_key_map[filter_key]} LIKE "%{filter_value}%" AND {condition}'
        return f'{self.filter_key_map[filter_key]}{filter_operator}"{filter_value}" AND {condition}'

    @property
    def order_by(self):
        try:
            return f'{self.filter_key_map[self.sort_by]} {self.order_by_direction}'
        except (KeyError, TypeError, NameError):
            return f'{self.sort_by_fallback} {self.order_by_direction}' if self.sort_by_fallback else None

    sort_by_fallback = None

    @property
    def order_by_direction(self):
        try:
            return self.sort_how or self.sort_direction[self.sort_by]
        except (KeyError, TypeError, NameError):
            return self.sort_how or self.order_by_direction_fallback

    order_by_direction_fallback = 'DESC'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.item_id, )

    @staticmethod
    def map_item_infoproperties(i):
        return {}

    def map_item_infolabels(self, i):
        infolabels = {k: i[k] for k in i.keys() if k in self.allowlist_infolabel_keys}
        infolabels.update({
            'title': i[self.item_label_key],
            'mediatype': self.map_mediatype(i),
        })
        return infolabels

    @staticmethod
    def map_item_unique_ids(i):
        return {'tmdb': i['tmdb_id']}

    @staticmethod
    def map_item_art(i):
        return {}

    def map_label2(self, i):
        return i[self.item_alter_key] if self.item_alter_key else ''

    def map_label(self, i):
        return i[self.item_label_key]

    def map_item_params(self, i):
        return {
            'info': 'details',
            'tmdb_type': self.item_tmdb_type,
            'tmdb_id': i['tmdb_id'],
        }

    def map_mediatype(self, i):
        return self.item_mediatype

    def map_item(self, i):
        return {
            'label': self.map_label(i),
            'label2': self.map_label2(i),
            'mediatype': self.map_mediatype(i),
            'infolabels': self.map_item_infolabels(i),
            'infoproperties': self.map_item_infoproperties(i),
            'unique_ids': self.map_item_unique_ids(i),
            'art': self.map_item_art(i),
            'params': self.map_item_params(i)
        }
