from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseclass import BaseItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem
from tmdbhelper.lib.addon.tmdate import age_difference
from tmdbhelper.lib.addon.plugin import get_localized


class Person(BaseItem):
    get_unique_ids = MediaItem.get_unique_ids

    art_dbclist_routes = (
        (('art_profile', None), 'thumb'),
        (('art_fanart', None), 'fanart'),
    )

    infoproperties_person_routes = (
        ('birthday', 'birthday'),
        ('deathday', 'deathday'),
        ('department', 'known_for_department'),
        ('aliases', 'also_known_as'),
        ('born', 'place_of_birth'),
        ('biography', 'biography'),
        ('numitems.tmdb.cast', 'total_cast'),
        ('numitems.tmdb.movies.cast', 'total_movies_cast'),
        ('numitems.tmdb.tvshows.cast', 'total_tvshows_cast'),
        ('numitems.tmdb.crew', 'total_crew'),
        ('numitems.tmdb.movies.crew', 'total_movies_crew'),
        ('numitems.tmdb.tvshows.crew', 'total_tvshows_crew'),
    )

    """
    instance: tuple of (attr, subtype) to retrieve self.db_{attr}_{subtype}_cache
    mappings: dictionary of {property_name: database_key} to map list as ListItem.Property({property_prefix}.{x}.{property_name}) = database[database_key]
    propname: property_prefix
    joinings: optional tuple of (property_name, dictionary_key) to map slash separated and [CR] separated properties as ListItem.Property(name), ListItem.Property(name_CR) e.g. 'Action / Adventure' 'Action[CR]Adventure'
    """
    infoproperties_dbclist_routes = (
        {
            'instance': ('starredmovies', None),  # StarredMovies
            'mappings': {'title': 'title', 'tmdb_id': 'tmdb_id', 'role': 'role', 'character': 'role', 'year': 'year', 'premiered': 'premiered', 'status': 'status'},
            'propname': ('movie.cast', ),
            'joinings': ('movie.cast', 'title')
        },
        {
            'instance': ('starredtvshows', None),  # StarredTVShows
            'mappings': {'title': 'title', 'tmdb_id': 'tmdb_id', 'role': 'role', 'character': 'role', 'year': 'year', 'premiered': 'premiered', 'status': 'status'},
            'propname': ('tvshow.cast', ),
            'joinings': ('tvshow.cast', 'title')
        },
        {
            'instance': ('crewedmovies', None),  # CrewedMovies
            'mappings': {'title': 'title', 'tmdb_id': 'tmdb_id', 'role': 'role', 'job': 'role', 'department': 'department', 'year': 'year', 'premiered': 'premiered', 'status': 'status'},
            'propname': ('movie.crew', ),
            'joinings': ('movie.crew', 'title')
        },
        {
            'instance': ('crewedtvshows', None),  # CrewedTVShows
            'mappings': {'title': 'title', 'tmdb_id': 'tmdb_id', 'role': 'role', 'job': 'role', 'department': 'department', 'year': 'year', 'premiered': 'premiered', 'status': 'status'},
            'propname': ('tvshow.crew', ),
            'joinings': ('tvshow.crew', 'title')
        },
    )

    def get_age(self):
        return age_difference(self.data[0]['birthday'], self.data[0]['deathday'])

    def get_gender(self):
        gender = self.data[0]['gender']
        if gender == 1:
            return get_localized(32071)
        if gender == 2:
            return get_localized(32070)
        if gender == 3:
            return get_localized(32535)
        return get_localized(32536)

    def get_infolabels_details(self):
        return {
            'title': self.data[0]['name'],
            'plot': self.data[0]['biography'],
            'mediatype': 'person',
        }

    def get_infoproperties_person(self, infoproperties):
        for ikey, dkey in self.infoproperties_person_routes:
            value = self.data[0][dkey]
            if not value:
                continue
            infoproperties[ikey] = value
        infoproperties['age'] = self.get_age()
        infoproperties['gender'] = self.get_gender()
        infoproperties['tmdb_type'] = 'person'
        return infoproperties

    def get_infoproperties_special(self, infoproperties):
        infoproperties = self.get_infoproperties_person(infoproperties)
        return infoproperties
