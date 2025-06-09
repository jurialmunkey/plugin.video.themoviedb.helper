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
