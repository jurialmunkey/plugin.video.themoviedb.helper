from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.baseclass import BaseItem


class Person(BaseItem):
    table = 'person'
    tmdb_type = 'person'
    ftv_id = None

    @property
    def cached_data_keys(self):
        """ SELECT """
        cached_data_keys = [f'{self.table}.{k}' for k in self.keys]
        cached_data_keys.extend([
            (
                '(    SELECT COUNT(DISTINCT castmember.parent_id) '
                '     FROM castmember WHERE castmember.tmdb_id=person.tmdb_id '
                ') as total_cast'
            ),
            (
                '(    SELECT COUNT(DISTINCT castmember.parent_id) '
                '     FROM castmember INNER JOIN movie ON movie.id=castmember.parent_id'
                '     WHERE castmember.tmdb_id=person.tmdb_id '
                ') as total_movies_cast'
            ),
            (
                '(    SELECT COUNT(DISTINCT castmember.parent_id) '
                '     FROM castmember INNER JOIN tvshow ON tvshow.id=castmember.parent_id'
                '     WHERE castmember.tmdb_id=person.tmdb_id '
                ') as total_tvshows_cast'
            ),
            (
                '(    SELECT COUNT(DISTINCT crewmember.parent_id) '
                '     FROM crewmember WHERE crewmember.tmdb_id=person.tmdb_id '
                ') as total_crew'
            ),
            (
                '(    SELECT COUNT(DISTINCT crewmember.parent_id) '
                '     FROM crewmember INNER JOIN movie ON movie.id=crewmember.parent_id'
                '     WHERE crewmember.tmdb_id=person.tmdb_id '
                ') as total_movies_crew'
            ),
            (
                '(    SELECT COUNT(DISTINCT crewmember.parent_id) '
                '     FROM crewmember INNER JOIN tvshow ON tvshow.id=crewmember.parent_id'
                '     WHERE crewmember.tmdb_id=person.tmdb_id '
                ') as total_tvshows_crew'
            ),
            (
                '(    SELECT art.icon FROM art'
                '     WHERE art.parent_id=person.id AND type=\'profiles\' '
                '     ORDER BY rating DESC LIMIT 1'
                ') as thumb'
            ),
        ])
        return cached_data_keys

    @staticmethod
    def set_unaired_expiry(*args, **kwargs):
        return  # People dont have premiered dates so we dont modify expiry time

    @property
    def online_data_kwgs(self):
        return {'append_to_response': self.common_apis.tmdb_api.append_to_response_person}

    @property
    def db_table_caches(self):
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('belongs'),
            self.return_basemeta_db('movie'),
            self.return_basemeta_db('tvshow'),
            self.return_basemeta_db('unique_id'),
            self.return_basemeta_db('custom'),
            self.return_basemeta_db('castmember'),
            self.return_basemeta_db('crewmember'),
            self.return_basemeta_db('art'),
        )
