from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from tmdbhelper.lib.addon.plugin import KeyGetter
from jurialmunkey.ftools import cached_property


class AiringNextItemMapper(ItemMapper):

    prefix = 'next_aired'

    @cached_property
    def tmdb_id(self):
        return self.meta.get('tmdb_id')

    @cached_property
    def premiered(self):
        return self.meta.get(f'{self.prefix}.original')

    @cached_property
    def is_future(self):
        if not self.premiered:
            return
        from tmdbhelper.lib.addon.tmdate import is_future_timestamp
        return is_future_timestamp(self.premiered, time_fmt="%Y-%m-%d", time_lim=10, days=-1)

    def get_metadata(self, key):
        name = f'{self.prefix}.{key}'
        data = f'{self.meta.get(name)}'
        return data

    @cached_property
    def title(self):
        return self.get_metadata('name')

    @cached_property
    def episode(self):
        return self.get_metadata('episode')

    @cached_property
    def season(self):
        return self.get_metadata('season')

    @cached_property
    def label(self):
        label = f'{self.title} ({self.premiered})'
        return label

    def get_infolabels(self):
        return {
            'mediatype': 'episode',
            'title': self.title,
            'episode': self.episode,
            'season': self.season,
            'plot': self.get_metadata('plot'),
            'year': self.get_metadata('year'),
            'premiered': self.premiered
        }

    def get_params(self):
        return {
            'info': 'details',
            'tmdb_type': 'tv',
            'tmdb_id': self.tmdb_id,
            'episode': self.episode,
            'season': self.season,
        }

    def get_unique_ids(self):
        return {
            'tmdb': self.tmdb_id,
            'tvshow.tmdb': self.tmdb_id,
        }

    def get_item(self):
        if not self.is_future:
            return
        return super().get_item()


class AiringNextItemGetter:

    def __init__(self, data):
        self.data = KeyGetter(data)

    @cached_property
    def tmdb_id(self):
        tmdb_id = self.data.get_key('tmdb_id')
        tmdb_id = tmdb_id or self.query_database.get_tmdb_id(
            tmdb_type='tv',
            imdb_id=self.data.get_key('imdb_id'),
            tvdb_id=self.data.get_key('tvdb_id'),
            query=self.data.get_key('showtitle') or self.data.get_key('title'),
            year=self.data.get_key('year')
        )
        return tmdb_id

    @cached_property
    def lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        lidc = ListItemDetails()
        lidc.extendedinfo = False
        return lidc

    @cached_property
    def query_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    @cached_property
    def meta(self):
        if not self.tmdb_id:
            return {}
        meta = self.lidc.get_item('tv', self.tmdb_id)
        meta = meta.get('infoproperties')
        if not meta:
            return {}
        meta['tmdb_id'] = self.tmdb_id
        return meta

    @cached_property
    def item(self):
        if not self.meta:
            return
        return AiringNextItemMapper(self.meta, add_infoproperties=None).item
