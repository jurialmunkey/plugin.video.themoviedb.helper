from tmdbhelper.lib.addon.plugin import ADDONPATH
from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from jurialmunkey.ftools import cached_property


class TVDbItemMapperBase(ItemMapper):

    metadata_subkey = None
    plot_affix = None

    @cached_property
    def query_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    def get_tmdb_id(self, year=None):
        return self.query_database.get_tmdb_id(tmdb_type=self.tmdb_type, query=self.title, year=year)

    @cached_property
    def tmdb_id(self):
        tmdb_id = self.get_tmdb_id(self.year)
        tmdb_id = tmdb_id or self.get_tmdb_id()
        return tmdb_id

    @cached_property
    def metadata(self):
        if not self.meta_skey:
            return self.meta
        return self.meta[self.meta_skey]

    @cached_property
    def year(self):
        return self.metadata.get('year')

    @cached_property
    def tvdb_id(self):
        return self.metadata.get('id')

    @cached_property
    def tvdb_slug(self):
        return self.metadata.get('slug')

    @cached_property
    def title(self):
        return self.metadata.get('name')

    @cached_property
    def label(self):
        return self.title

    @cached_property
    def icon(self):
        icon = self.metadata.get('image')
        icon = icon or f'{ADDONPATH}/resources/icons/tvdb/tvdb.png'
        return icon

    def get_infolabels(self):
        return {
            'mediatype': self.mediatype,
            'year': self.year,
            'title': self.title,
        }

    def get_infoproperties(self):
        return {
            'plot_affix': self.plot_affix,
            'tmdb_type': self.tmdb_type,
            'tmdb_id': self.tmdb_id,
        }

    def get_params(self):
        return {
            'info': 'details',
            'tmdb_type': self.tmdb_type,
            'tmdb_id': self.tmdb_id,
        }

    def get_unique_ids(self):
        return {
            'tmdb': self.tmdb_id,
            'tvdb': self.tvdb_id,
            'tvdb_slug': self.tvdb_slug,
        }

    def get_art(self):
        return {
            'icon': self.icon,
        }


class TVDbGenreItemMapperTVShow(TVDbItemMapperBase):
    mediatype = 'tvshow'
    tmdb_type = 'tv'


class TVDbGenreItemMapperMovie(TVDbItemMapperBase):
    mediatype = 'movie'
    tmdb_type = 'movie'


class TVDbAwardItemMapperBase(TVDbItemMapperBase):
    @cached_property
    def award_year(self):
        return self.meta.get('year')

    @cached_property
    def is_winner(self):
        return self.meta.get('isWinner')

    @cached_property
    def plot_affix(self):
        if self.is_winner:
            return f'[B]Winner {self.award_year}[/B]: '
        return f'[B]Nominee {self.award_year}[/B]: '


class TVDbAwardItemMapperTVShow(TVDbAwardItemMapperBase):
    meta_skey = 'series'
    mediatype = 'tvshow'
    tmdb_type = 'tv'


class TVDbAwardItemMapperMovie(TVDbAwardItemMapperBase):
    meta_skey = 'movie'
    mediatype = 'movie'
    tmdb_type = 'movie'


def TVDbGenreItemMapper(meta, add_infoproperties=None):
    if 'episodes' in meta:
        return TVDbGenreItemMapperTVShow(meta, add_infoproperties=add_infoproperties)
    return TVDbGenreItemMapperMovie(meta, add_infoproperties=add_infoproperties)


def TVDbAwardItemMapper(meta, add_infoproperties=None):
    if meta.get('series'):
        return TVDbAwardItemMapperTVShow(meta, add_infoproperties=add_infoproperties)
    if meta.get('movie'):
        return TVDbAwardItemMapperMovie(meta, add_infoproperties=add_infoproperties)
