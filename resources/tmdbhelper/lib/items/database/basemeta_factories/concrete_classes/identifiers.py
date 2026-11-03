from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList
from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import UniqueId


class ExternalIds(UniqueId):
    id_types = ('tmdb', 'imdb', 'tvdb')

    @cached_property
    def ids(self):
        return self.get_ids()

    def get_ids(self):
        with self.connection.open():
            return {
                item['key']: item['value'] for item in self.cached_data or ()
                if item['key'] in self.id_types and item['value'] not in (None, '', 'None')}


class EpisodeParent(ItemDetailsList):
    table = (
        'unique_id INNER JOIN episode ON episode.id=unique_id.parent_id '
        'INNER JOIN tvshow ON tvshow.id=episode.tvshow_id '
        'INNER JOIN season ON season.id=episode.season_id')

    keys = ('tvshow.tmdb_id',)
    conditions = (
        'unique_id.key=? AND unique_id.value=? '
        'AND (? IS NULL OR season.season=?) '
        'AND (? IS NULL OR episode.episode=?) LIMIT 1')
    season = None
    episode = None

    @property
    def values(self):
        return ('tmdb', str(self.tmdb_id), self.season, self.season, self.episode, self.episode)

    @cached_property
    def parent_id(self):
        return self.get_parent_id()

    def get_parent_id(self):
        with self.connection.open():
            rows = self.cached_data
        return try_int(rows[0]['tmdb_id'], fallback=None) if rows else None
