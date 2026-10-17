from tmdbhelper.lib.items.directories.mapper_basic import ItemMapper
from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH
from jurialmunkey.ftools import cached_property


class StreamingChartsItemMapper(ItemMapper):
    @cached_property
    def label(self):
        return get_localized(self.meta['localize'])

    def get_art(self):
        return {'icon': f'{ADDONPATH}/resources/icons/mdblist/mdblist.png'}

    def get_params(self):
        return {
            'info': 'mdblist_streamingchart',
            'tmdb_type': self.meta['tmdb_type'],
            'rank': self.meta['rank'],
        }
