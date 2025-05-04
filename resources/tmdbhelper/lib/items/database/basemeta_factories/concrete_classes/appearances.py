
from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList


class StarredMovies(ItemDetailsList):
    table = 'castmember'
    conditions = 'castmember.tmdb_id=? GROUP BY movie.tmdb_id ORDER BY premiered DESC LIMIT 10'  # WHERE conditions
    cached_data_keys = ('role', 'movie.tmdb_id AS tmdb_id', 'title', 'year', 'premiered', 'status')

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.tmdb_id, )

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)

    @property
    def cached_data_table(self):
        return f'{self.table} INNER JOIN movie ON movie.id = {self.table}.parent_id'


class StarredTVShows(ItemDetailsList):
    table = 'castmember'
    keys = ('role', )
    conditions = 'castmember.tmdb_id=? GROUP BY tvshow.tmdb_id ORDER BY appearances DESC LIMIT 10'  # WHERE conditions
    cached_data_keys = ('role', 'tvshow.tmdb_id AS tmdb_id', 'title', 'year', 'premiered', 'status')

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.tmdb_id, )

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)

    @property
    def cached_data_table(self):
        return f'{self.table} INNER JOIN tvshow ON tvshow.id = {self.table}.parent_id'


class CrewedMovies(ItemDetailsList):
    table = 'crewmember'
    conditions = 'crewmember.tmdb_id=? GROUP BY movie.tmdb_id ORDER BY premiered DESC LIMIT 10'  # WHERE conditions
    cached_data_keys = ('role', 'department', 'movie.tmdb_id AS tmdb_id', 'title', 'year', 'premiered', 'status')

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.tmdb_id, )

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)

    @property
    def cached_data_table(self):
        return f'{self.table} INNER JOIN movie ON movie.id = {self.table}.parent_id'


class CrewedTVShows(ItemDetailsList):
    table = 'crewmember'
    keys = ('role', )
    conditions = 'crewmember.tmdb_id=? GROUP BY tvshow.tmdb_id ORDER BY appearances DESC LIMIT 10'  # WHERE conditions
    cached_data_keys = ('role', 'department', 'tvshow.tmdb_id AS tmdb_id', 'title', 'year', 'premiered', 'status')

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.tmdb_id, )

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)

    @property
    def cached_data_table(self):
        return f'{self.table} INNER JOIN tvshow ON tvshow.id = {self.table}.parent_id'
