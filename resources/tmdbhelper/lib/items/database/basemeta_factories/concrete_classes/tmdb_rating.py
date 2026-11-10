from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList


class MovieTMDbRating(ItemDetailsList):
    """The TMDb rating stored with an item's unexpired details, in TMDb response keys."""

    table = 'movie INNER JOIN baseitem ON baseitem.id=movie.id'
    keys = ('movie.rating', 'movie.votes')
    conditions = 'movie.id=? AND baseitem.expiry>=? LIMIT 1'

    @property
    def values(self):
        return (self.item_id, self.current_time)

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        with self.connection.open():
            rows = self.cached_data
        if not rows or rows[0]['rating'] is None:
            return {}
        return {'vote_average': rows[0]['rating'], 'vote_count': rows[0]['votes']}


class TvshowTMDbRating(MovieTMDbRating):
    table = 'tvshow INNER JOIN baseitem ON baseitem.id=tvshow.id'
    keys = ('tvshow.rating', 'tvshow.votes')
    conditions = 'tvshow.id=? AND baseitem.expiry>=? LIMIT 1'
