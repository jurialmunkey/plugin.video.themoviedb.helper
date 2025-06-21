from collections import namedtuple


IdentifierTuple = namedtuple("identifierTuple", "item_id tmdb_id tmdb_type")


TABLE = 'identifier'
KEYS = ('id', 'tmdb_id', 'tmdb_type')


def make_identifier_id(
    dbtype=None,
    query=None,
    season=None,
    episode=None,
    imdb_id=None,
    year=None,
    episode_year=None,
    infolabel_uniqueid_tmdb=None,
    infolabel_uniqueid_tvshow_tmdb=None,
):
    return '.'.join(map(str, (
        dbtype or None,
        query or None,
        season or None,
        episode or None,
        imdb_id or None,
        year or None,
        episode_year or None,
        infolabel_uniqueid_tmdb or None,
        infolabel_uniqueid_tvshow_tmdb or None,
    )))


class FindQueriesDatabaseIdentifier:

    identifier_columns = {
        'id': {
            'data': 'BLOB PRIMARY KEY',
            'indexed': True
        },
        'tmdb_id': {
            'data': 'INTEGER'
        },
        'tmdb_type': {
            'data': 'TEXT'
        },
    }

    def get_identifier(self, item_id):
        kwgs = {'values': (item_id, ), 'conditions': 'id=?'}
        data = self.get_cached_values(TABLE, KEYS, **kwgs)
        return (
            IdentifierTuple(item_id, data[0]['tmdb_id'], data[0]['tmdb_type'])
            if data and data[0] else
            None
        )

    def set_identifier(self, item_id, tmdb_id, tmdb_type):
        if not item_id or not tmdb_id or not tmdb_type:
            return
        identifier_tuple = IdentifierTuple(item_id, tmdb_id, tmdb_type)
        self.set_cached_values(TABLE, KEYS, [identifier_tuple])
        return identifier_tuple

    def del_identifier(self, item_id):
        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            self.access.del_cached(TABLE, item_id, children=False)
            connection.execute('COMMIT')
