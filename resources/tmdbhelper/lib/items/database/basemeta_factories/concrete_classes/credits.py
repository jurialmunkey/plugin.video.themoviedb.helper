from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList


class CastMember(ItemDetailsList):
    table = 'castmember'
    keys = ('tmdb_id', 'role', 'ordering', 'appearances', 'parent_id')
    conflict_constraint = 'tmdb_id, role, parent_id'
    conditions = 'parent_id=? GROUP BY castmember.tmdb_id ORDER BY IFNULL(ordering, 9999) ASC LIMIT 100'  # WHERE conditions  # TODO: Move limit to settings ???
    cached_data_keys = (
        'castmember.tmdb_id', 'GROUP_CONCAT(role, " / ") as role', 'ordering', 'appearances',
        'name', 'gender', 'biography', 'known_for_department',
        (
            '(    SELECT art.icon FROM art'
            '     WHERE art.parent_id=\'person.\' || castmember.tmdb_id AND art.type=\'profiles\' '
            '     ORDER BY art.rating DESC LIMIT 1'
            ') as thumb'
        ),
    )

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)

    @property
    def cached_data_table(self):
        return f'{self.table} INNER JOIN person ON person.tmdb_id = {self.table}.tmdb_id'


class CrewMember(CastMember):
    table = 'crewmember'
    keys = ('tmdb_id', 'role', 'department', 'appearances', 'parent_id')
    conditions = 'parent_id=? ORDER BY appearances DESC LIMIT 100'
    conflict_constraint = 'tmdb_id, role, department, parent_id'
    cached_data_keys = (
        'crewmember.tmdb_id', 'role', 'department', 'appearances',
        'name', 'gender', 'biography', 'known_for_department',
        (
            '(    SELECT art.icon FROM art'
            '     WHERE art.parent_id=\'person.\' || crewmember.tmdb_id AND art.type=\'profiles\' '
            '     ORDER BY art.rating DESC LIMIT 1'
            ') as thumb'
        ),
    )


class Creator(CrewMember):
    conditions = 'parent_id=? AND role=? LIMIT 20'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.parent_id, 'Creator',)  # Creator is for TV Show so get parent for season/episode


class Director(CrewMember):
    conditions = 'parent_id=? AND department=? AND role=? LIMIT 20'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Directing', 'Director')


class Writer(CrewMember):
    conditions = 'parent_id=? AND department=? LIMIT 20'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Writing', )


class Screenplay(CrewMember):
    conditions = 'parent_id=? AND department=? AND role=? LIMIT 20'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Writing', 'Screenplay')


class Producer(CrewMember):
    conditions = 'parent_id=? AND department=? LIMIT 20'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Production')


class SoundDepartment(CrewMember):
    conditions = 'parent_id=? AND department=? LIMIT 20'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Sound')


class ArtDepartment(CrewMember):
    conditions = 'parent_id=? AND department=? LIMIT 20'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Art')


class Photography(CrewMember):
    conditions = 'parent_id=? AND department=? LIMIT 20'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Camera')


class Editor(CrewMember):
    conditions = 'parent_id=? AND department=? LIMIT 20'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'Editing')


class Person(ItemDetailsList):
    table = 'person'
    keys = ('id', 'tmdb_id', 'name', 'gender', 'biography', 'known_for_department')
    conditions = 'tmdb_id=?'
