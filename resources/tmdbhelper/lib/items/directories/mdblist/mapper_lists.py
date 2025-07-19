from tmdbhelper.lib.items.directories.trakt.mapper_standard import MediaItemMapper
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.addon.consts import RUNSCRIPT


class ListsMDbListItemMapper(MediaItemMapper):

    tmdb_type = ''
    mediatype = ''

    @cached_property
    def label(self):
        return self.meta.get('name') or ''

    infolabels_map = {
        'description': 'plot',
    }
    infoproperties_map = {
        'items': 'items',
        'likes': 'likes',
    }

    def get_infoproperties(self):
        infoproperties = super().get_infoproperties()
        infoproperties['is_sortable'] = 'mdblist'
        return infoproperties

    def get_context_menu(self):
        return [
            (
                get_localized(32309),
                RUNSCRIPT.format('sort_mdblist,{}'.format(','.join(f'{k}={v}' for k, v in self.params.items())))
            ),
        ]

    def get_unique_ids(self):
        unique_ids = {
            'list_id': self.meta['id'],
            'user_id': self.meta.get('user_id'),
            'user_name': self.meta.get('user_name'),
            'list_slug': self.meta.get('slug'),
        }
        return unique_ids

    def get_params(self):
        params = {
            'info': 'mdblist_userlist',
            'list_id': self.meta['id'],
            'list_name': self.label,
            'plugin_category': self.label,
        }
        return params
