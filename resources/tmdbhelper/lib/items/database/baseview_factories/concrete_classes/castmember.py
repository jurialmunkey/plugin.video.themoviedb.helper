from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.addon.consts import DATALEVEL_MAX
from jurialmunkey.ftools import cached_property


class CastMemberMediaList(MediaList):
    table = 'castmember'
    cached_data_check_key = 'parent_id'
    keys = ('GROUP_CONCAT(role, " / ") as role', 'ordering', 'appearances', 'parent_id')
    item_mediatype = 'person'
    item_tmdb_type = 'person'

    cached_data_base_conditions = 'parent_id=? AND expiry>=? AND datalevel>=?'  # WHERE conditions
    group_by = 'castmember.tmdb_id'
    sort_by_fallback = 'IFNULL(ordering, 9999)'
    order_by_direction_fallback = 'ASC'

    filter_key_map = {
        'role': 'role',
        'appearances': 'appearances',
        'title': 'creditedperson.name',
        'gender': 'creditedperson.gender',
    }

    sort_direction = {
        'appearances': 'DESC',
    }

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.item_id, self.current_time, DATALEVEL_MAX)

    @property
    def cached_data_table(self):
        cached_data_table = (
            f'{self.table} INNER JOIN person ON person.tmdb_id = {self.table}.tmdb_id '
            f'INNER JOIN baseitem ON {self.table}.parent_id = baseitem.id'

        )
        cached_data_table = f'({cached_data_table}) as creditedperson'
        return cached_data_table

    @property
    def cached_data_keys(self):
        return (
            *self.keys,
            'creditedperson.tmdb_id', 'creditedperson.name', 'creditedperson.gender',
            'creditedperson.biography', 'creditedperson.known_for_department',
            (
                '(    SELECT art.icon FROM art'
                '     WHERE art.parent_id=person.id AND type=\'profiles\' '
                '     ORDER BY rating DESC LIMIT 1'
                ') as thumb'
            ),
        )

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'role': i['role'],
            'character': i['role'],
            'episodes': i['appearances'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'person',
        }

    def map_item_art(self, i):
        return {
            'thumb': self.image_path_func(i['thumb'])
        }

    @staticmethod
    def map_label2(i):
        return i['role']


class Movie(CastMemberMediaList):
    pass


class Tvshow(CastMemberMediaList):
    pass


class Season(CastMemberMediaList):
    @cached_property
    def item_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)


class Episode(CastMemberMediaList):
    @cached_property
    def item_id(self):
        return self.get_episode_id(self.tmdb_type, self.tmdb_id, self.season, self.episode)
