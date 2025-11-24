from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList


class SeriesItemDetailsList(ItemDetailsList):
    @property
    def values(self):  # WHERE = ?
        return (self.collection_id, )


class SeriesGenre(SeriesItemDetailsList):
    keys = ('DISTINCT name', 'tmdb_id')  # SELECT
    table = 'genre INNER JOIN belongs ON genre.parent_id = belongs.id'  # FROM
    conditions = 'belongs.parent_id=? ORDER BY name'  # WHERE


class SeriesMovie(SeriesItemDetailsList):
    keys = (
        'title', 'year', 'plot', 'duration', 'premiered', 'status',
        'rating', 'votes', 'popularity', 'tmdb_id', 'originaltitle',
    )
    table = 'movie INNER JOIN belongs ON movie.id = belongs.id'  # FROM
    conditions = 'belongs.parent_id=? ORDER BY year ASC'  # WHERE


class SeriesStats(SeriesItemDetailsList):
    keys = (
        'ROUND(AVG(CASE WHEN rating > 0 THEN rating ELSE NULL END), 1) as rating',
        'SUM(votes) as votes',
        'COUNT(movie.tmdb_id) as numitems',
        'MAX(year) as year_last',
        'MIN(year) as year_first',
    )  # SELECT
    table = 'movie INNER JOIN belongs ON movie.id = belongs.id'  # FROM
    conditions = 'belongs.parent_id=? GROUP BY belongs.parent_id'  # WHERE
