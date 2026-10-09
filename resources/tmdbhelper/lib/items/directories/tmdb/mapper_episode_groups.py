from copy import deepcopy
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper


class EpisodeGroupItemMapper(ItemMapper):

    @cached_property
    def tvshow_item(self):
        return self.meta['tvshow_item']

    @cached_property
    def group(self):
        return self.meta['group']

    @cached_property
    def label(self):
        return self.group['title'] or ''

    def get_infolabels(self):
        infolabels = deepcopy(self.tvshow_item.get('infolabels') or {})
        infolabels.update({'title': self.label, 'plot': self.group['plot']})
        return infolabels

    def get_infoproperties(self):
        return deepcopy(self.tvshow_item.get('infoproperties') or {})

    def get_unique_ids(self):
        unique_ids = dict(self.tvshow_item.get('unique_ids') or {})
        unique_ids['group_tmdb'] = self.group['tmdb_id']
        return unique_ids

    def get_params(self):
        params = dict(self.tvshow_item.get('params') or {})
        params.update({'info': 'details', 'tmdb_type': 'tv', 'tmdb_id': self.unique_ids['tmdb']})
        return params

    def get_art(self):
        return dict(self.tvshow_item.get('art') or {})

    def get_context_menu(self):
        return list(self.tvshow_item.get('context_menu') or [])

    def get_item(self):
        item = deepcopy(self.tvshow_item)
        item.update(super().get_item())
        item['is_folder'] = True
        return item
