from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.files.ftools import cached_property


class CastMemberMediaList(MediaList):
    table = 'castmember'
    cached_data_conditions_base = 'parent_id=? GROUP BY castmember.tmdb_id ORDER BY IFNULL(ordering, 9999) ASC'  # WHERE conditions
    cached_data_check_key = 'parent_id'
    keys = ('GROUP_CONCAT(role, " / ") as role', 'ordering', 'appearances', 'parent_id')
    item_mediatype = 'person'
    item_tmdb_type = 'person'

    @property
    def cached_data_table(self):
        table = ' '.join((
            f'{self.table}',
            f'INNER JOIN person ON person.tmdb_id = {self.table}.tmdb_id'
        ))
        return f'({table}) as creditedperson'

    @property
    def cached_data_keys(self):
        return (
            *self.keys,
            'creditedperson.tmdb_id', 'creditedperson.thumb', 'creditedperson.name', 'creditedperson.gender',
            'creditedperson.biography', 'creditedperson.known_for_department')

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
