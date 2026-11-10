from tmdbhelper.lib.items.database.basemeta_factories.factory import BaseMetaFactory
from tmdbhelper.lib.query.database.table import FindQueriesDatabaseTable


class FindQueriesDatabaseTableEpisodeParent(FindQueriesDatabaseTable):
    table = 'external_ids'
    keys = ('parent_tmdb_id',)
    conditions = (
        'tmdb_type=? AND tmdb_id=? AND episode IS NOT NULL '
        'AND (? IS NULL OR season=?) '
        'AND (? IS NULL OR episode=?) LIMIT 1')
    season = None
    episode = None
    imdb_id = None
    tvdb_id = None

    @property
    def values(self):
        return ('tv', self.tmdb_id, self.season, self.season, self.episode, self.episode)

    @property
    def is_expired_get(self):
        # A cached episode-to-show relationship remains useful after ID expiry.
        return False

    @staticmethod
    def get_mapping(data):
        return data[0]['parent_tmdb_id'] if data else None

    def get_metadata_parent_id(self):
        reader = BaseMetaFactory('episode_parent')
        reader.tmdb_id = self.tmdb_id
        reader.season = self.season
        reader.episode = self.episode
        return reader.parent_id

    def get_external_parent_id(self):
        if self.imdb_id or self.tvdb_id:
            return self.parent.get_tmdb_id('tv', imdb_id=self.imdb_id, tvdb_id=self.tvdb_id)

    def use(self):
        return self.get_metadata_parent_id() or self.get() or self.get_external_parent_id()


class FindQueriesDatabaseEpisodeParent:
    def get_episode_parent_id(self, tmdb_id, season=None, episode=None, imdb_id=None, tvdb_id=None):
        table = FindQueriesDatabaseTableEpisodeParent(self)
        table.tmdb_id = tmdb_id
        table.season = int(season) if season is not None else None
        table.episode = int(episode) if episode is not None else None
        table.imdb_id = imdb_id
        table.tvdb_id = tvdb_id
        return table.use()
