from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from jurialmunkey.ftools import cached_property


class WatchersItemMapper(ItemMapper):
    @cached_property
    def label(self):
        return self.meta.get('name') or self.meta.get('username') or ''

    @cached_property
    def user_ids(self):
        return self.meta.get('ids') or {}

    @cached_property
    def user_slug(self):
        return self.user_ids.get('slug')

    def get_params(self):
        params = {
            'info': 'trakt_userslists',
            'user_slug': self.user_slug,
        }
        return params

    def get_infoproperties(self):
        infoproperties = {
            k: v for d in (self.meta, ) for k, v in d.items()
            if v and type(v) not in [list, dict]
        }
        return infoproperties

    def get_unique_ids(self):
        unique_ids = {
            'user': self.user_slug,
        }
        return unique_ids
