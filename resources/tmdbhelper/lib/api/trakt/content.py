class TraktContent():

    """
    TRAKT LIST METHODS
    """


    def get_list_of_genres(self, *args, **kwargs):
        try:
            return self._get_list_of_genres(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_list_of_genres
            self._get_list_of_genres = get_list_of_genres
            return self._get_list_of_genres(self, *args, **kwargs)

