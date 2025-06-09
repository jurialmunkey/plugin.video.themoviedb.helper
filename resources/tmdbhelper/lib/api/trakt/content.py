class TraktContent():

    """
    TRAKT LIST METHODS
    """

    def get_sorted_list(self, *args, **kwargs):
        try:
            return self._get_sorted_list(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_sorted_list
            self._get_sorted_list = get_sorted_list
            return self._get_sorted_list(self, *args, **kwargs)

    def get_list_of_genres(self, *args, **kwargs):
        try:
            return self._get_list_of_genres(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_list_of_genres
            self._get_list_of_genres = get_list_of_genres
            return self._get_list_of_genres(self, *args, **kwargs)

    def merge_sync_sort(self, *args, **kwargs):
        try:
            return self._merge_sync_sort(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import merge_sync_sort
            self._merge_sync_sort = merge_sync_sort
            return self._merge_sync_sort(self, *args, **kwargs)

    def filter_inprogress(self, *args, **kwargs):
        try:
            return self._filter_inprogress(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import filter_inprogress
            self._filter_inprogress = filter_inprogress
            return self._filter_inprogress(self, *args, **kwargs)

    def get_imdb_top250(self, *args, **kwargs):
        try:
            return self._get_imdb_top250(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_imdb_top250
            self._get_imdb_top250 = get_imdb_top250
            return self._get_imdb_top250(self, *args, **kwargs)

    """
    TRAKT DETAILS METHODS
    """

    def get_details(self, *args, **kwargs):
        try:
            return self._get_details(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.details import get_details
            self._get_details = get_details
            return self._get_details(self, *args, **kwargs)

    def get_id(self, *args, **kwargs):
        try:
            return self._get_id(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.details import get_id
            self._get_id = get_id
            return self._get_id(self, *args, **kwargs)

    def get_id_search(self, *args, **kwargs):
        try:
            return self._get_id_search(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.details import get_id_search
            self._get_id_search = get_id_search
            return self._get_id_search(self, *args, **kwargs)

    def get_showitem_details(self, *args, **kwargs):
        try:
            return self._get_showitem_details(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.details import get_showitem_details
            self._get_showitem_details = get_showitem_details
            return self._get_showitem_details(self, *args, **kwargs)

    def get_ratings(self, *args, **kwargs):
        try:
            return self._get_ratings(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.details import get_ratings
            self._get_ratings = get_ratings
            return self._get_ratings(self, *args, **kwargs)

    """
    TRAKT CALENDAR METHODS
    """

    def get_calendar(self, *args, **kwargs):
        try:
            return self._get_calendar(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar
            self._get_calendar = get_calendar
            return self._get_calendar(self, *args, **kwargs)

    def get_calendar_episodes(self, *args, **kwargs):
        try:
            return self._get_calendar_episodes(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episodes
            self._get_calendar_episodes = get_calendar_episodes
            return self._get_calendar_episodes(self, *args, **kwargs)
