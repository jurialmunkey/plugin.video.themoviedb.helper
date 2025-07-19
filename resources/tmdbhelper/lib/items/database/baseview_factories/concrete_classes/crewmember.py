from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.castmember import CastMemberMediaList
from jurialmunkey.ftools import cached_property


class CrewMemberMediaList(CastMemberMediaList):
    table = 'crewmember'
    cached_data_base_conditions = 'parent_id=? AND expiry>=? AND datalevel>=?'  # WHERE conditions
    cached_data_check_key = 'parent_id'
    group_by = 'crewmember.tmdb_id'
    keys = ('GROUP_CONCAT(role, " / ") as role', 'department', 'appearances', 'parent_id')

    sort_by_fallback = None
    order_by_direction_fallback = 'ASC'

    filter_key_map = {
        'role': 'role',
        'department': 'department',
        'appearances': 'appearances',
        'title': 'creditedperson.name',
        'gender': 'creditedperson.gender',
    }

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'role': i['role'],
            'job': i['role'],
            'department': i['department'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'person',
        }


class Movie(CrewMemberMediaList):
    pass


class Tvshow(CrewMemberMediaList):
    pass


class Season(CrewMemberMediaList):
    @cached_property
    def item_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)


class Episode(CrewMemberMediaList):
    @cached_property
    def item_id(self):
        return self.get_episode_id(self.tmdb_type, self.tmdb_id, self.season, self.episode)
