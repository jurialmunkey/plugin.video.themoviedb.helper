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

    def get_simple_list(self, *args, **kwargs):
        try:
            return self._get_simple_list(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_simple_list
            self._get_simple_list = get_simple_list
            return self._get_simple_list(self, *args, **kwargs)

    def get_mixed_list(self, *args, **kwargs):
        try:
            return self._get_mixed_list(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_mixed_list
            self._get_mixed_list = get_mixed_list
            return self._get_mixed_list(self, *args, **kwargs)

    def get_basic_list(self, *args, **kwargs):
        try:
            return self._get_basic_list(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_basic_list
            self._get_basic_list = get_basic_list
            return self._get_basic_list(self, *args, **kwargs)

    def get_stacked_list(self, *args, **kwargs):
        try:
            return self._get_stacked_list(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_stacked_list
            self._get_stacked_list = get_stacked_list
            return self._get_stacked_list(self, *args, **kwargs)

    def get_custom_list(self, *args, **kwargs):
        try:
            return self._get_custom_list(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_custom_list
            self._get_custom_list = get_custom_list
            return self._get_custom_list(self, *args, **kwargs)

    def get_list_of_genres(self, *args, **kwargs):
        try:
            return self._get_list_of_genres(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_list_of_genres
            self._get_list_of_genres = get_list_of_genres
            return self._get_list_of_genres(self, *args, **kwargs)

    def get_list_of_lists(self, *args, **kwargs):
        try:
            return self._get_list_of_lists(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.lists import get_list_of_lists
            self._get_list_of_lists = get_list_of_lists
            return self._get_list_of_lists(self, *args, **kwargs)

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

    def get_calendar_episode_item(self, *args, **kwargs):
        try:
            return self._get_calendar_episode_item(*args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episode_item
            self._get_calendar_episode_item = get_calendar_episode_item
            return self._get_calendar_episode_item(*args, **kwargs)

    def get_calendar_episode_item_bool(self, *args, **kwargs):
        try:
            return self._get_calendar_episode_item_bool(*args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episode_item_bool
            self._get_calendar_episode_item_bool = get_calendar_episode_item_bool
            return self._get_calendar_episode_item_bool(*args, **kwargs)

    def get_stacked_item(self, *args, **kwargs):
        try:
            return self._get_stacked_item(*args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.calendar import get_stacked_item
            self._get_stacked_item = get_stacked_item
            return self._get_stacked_item(*args, **kwargs)

    def stack_calendar_episodes(self, *args, **kwargs):
        try:
            return self._stack_calendar_episodes(*args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.calendar import stack_calendar_episodes
            self._stack_calendar_episodes = stack_calendar_episodes
            return self._stack_calendar_episodes(*args, **kwargs)

    def stack_calendar_tvshows(self, *args, **kwargs):
        try:
            return self._stack_calendar_tvshows(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.calendar import stack_calendar_tvshows
            self._stack_calendar_tvshows = stack_calendar_tvshows
            return self._stack_calendar_tvshows(self, *args, **kwargs)

    def get_calendar_episodes_listitems(self, *args, **kwargs):
        try:
            return self._get_calendar_episodes_listitems(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episodes_listitems
            self._get_calendar_episodes_listitems = get_calendar_episodes_listitems
            return self._get_calendar_episodes_listitems(self, *args, **kwargs)

    def get_calendar_episodes_list(self, *args, **kwargs):
        try:
            return self._get_calendar_episodes_list(self, *args, **kwargs)
        except AttributeError:
            from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episodes_list
            self._get_calendar_episodes_list = get_calendar_episodes_list
            return self._get_calendar_episodes_list(self, *args, **kwargs)
