from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.starredcombined import StarredCombinedMediaList


class CrewedCombinedMediaList(StarredCombinedMediaList):
    table = 'crewmember'

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'role': i['role'],
            'job': i['role'],
            'department': i['department'],
            'popularity': i['popularity'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': i['tmdb_type'],
        }

    cached_data_keys = (
        'media.id as parent_id',
        'GROUP_CONCAT(role, " / ") as role',
        'GROUP_CONCAT(department, " / ") as department',
        'media.tmdb_id as tmdb_id',
        'media.tmdb_type as tmdb_type',
        'media.mediatype as mediatype',
        'media.title as title',
        'media.year as year',
        'media.premiered as premiered',
        'media.status as status',
        'media.votes as votes',
        'media.rating as rating',
        'media.popularity as popularity',
    )


class Person(CrewedCombinedMediaList):
    pass
