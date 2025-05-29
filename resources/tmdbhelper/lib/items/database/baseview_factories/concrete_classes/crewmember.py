from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.castmember import CastMemberMediaList
from tmdbhelper.lib.files.ftools import cached_property


class CrewMemberMediaList(CastMemberMediaList):
    table = 'crewmember'
    cached_data_conditions_base = 'parent_id=? GROUP BY crewmember.tmdb_id '
    cached_data_check_key = 'parent_id'
    keys = ('GROUP_CONCAT(role, " / ") as role', 'department', 'appearances', 'parent_id')

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
