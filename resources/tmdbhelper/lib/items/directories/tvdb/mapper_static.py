from tmdbhelper.lib.addon.plugin import ADDONPATH
from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from jurialmunkey.ftools import cached_property


class TVDbStaticItemMapper(ItemMapper):

    @cached_property
    def tvdb_id(self):
        return self.meta.get('id')

    @cached_property
    def label(self):
        return self.meta.get('name')

    def get_infolabels(self):
        from tmdbhelper.lib.addon.consts import TVDB_DISCLAIMER
        return {
            'plot': TVDB_DISCLAIMER,
        }

    def get_params(self):
        return {
            'info': self.info,
            'tvdb_id': self.tvdb_id,
            'tmdb_type': self.tmdb_type,
        }

    def get_unique_ids(self):
        return {
            'tvdb_id': self.tvdb_id,
        }

    def get_art(self):
        return {
            'icon': f'{ADDONPATH}/resources/icons/tvdb/tvdb.png',
        }


class TVDbStaticAwardsItemMapper(TVDbStaticItemMapper):
    info = 'dir_tvdb_award_categories'
    tmdb_type = 'both'


class TVDbStaticAwardCategoriesItemMapper(TVDbStaticItemMapper):
    info = 'tvdb_award_category'
    tmdb_type = 'both'


class TVDbStaticGenresItemMapper(TVDbStaticItemMapper):
    info = 'tvdb_genre'
    tmdb_type = 'both'
