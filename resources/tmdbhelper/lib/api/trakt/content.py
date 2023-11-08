class TraktMethods():

    """
    TRAKT LIST METHODS
    """

    def get_sorted_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_sorted_list
        return get_sorted_list(self, *args, **kwargs)

    def get_simple_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_simple_list
        return get_simple_list(self, *args, **kwargs)

    def get_mixed_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_mixed_list
        return get_mixed_list(self, *args, **kwargs)

    def get_basic_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_basic_list
        return get_basic_list(self, *args, **kwargs)

    def get_stacked_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_stacked_list
        return get_stacked_list(self, *args, **kwargs)

    def get_custom_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_custom_list
        return get_custom_list(self, *args, **kwargs)

    def get_list_of_genres(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_list_of_genres
        return get_list_of_genres(self, *args, **kwargs)

    def get_list_of_lists(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_list_of_lists
        return get_list_of_lists(self, *args, **kwargs)

    def get_sync_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_sync_list
        return get_sync_list(self, *args, **kwargs)

    def merge_sync_sort(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import merge_sync_sort
        return merge_sync_sort(self, *args, **kwargs)

    def filter_inprogress(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import filter_inprogress
        return filter_inprogress(self, *args, **kwargs)

    def get_imdb_top250(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.lists import get_imdb_top250
        return get_imdb_top250(self, *args, **kwargs)

    """
    TRAKT DETAILS METHODS
    """

    def get_details(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.details import get_details
        return get_details(self, *args, **kwargs)

    def get_id(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.details import get_id
        return get_id(self, *args, **kwargs)

    def get_id_search(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.details import get_id_search
        return get_id_search(self, *args, **kwargs)

    def get_showitem_details(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.details import get_showitem_details
        return get_showitem_details(self, *args, **kwargs)

    def get_ratings(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.details import get_ratings
        return get_ratings(self, *args, **kwargs)

    """
    TRAKT SYNC METHODS
    """

    def get_sync_item(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_item
        return get_sync_item(self, *args, **kwargs)

    def add_list_item(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import add_list_item
        return add_list_item(self, *args, **kwargs)

    def like_userlist(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import like_userlist
        return like_userlist(self, *args, **kwargs)

    def sync_item(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import sync_item
        return sync_item(self, *args, **kwargs)

    def get_last_activity(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_last_activity
        return get_last_activity(self, *args, **kwargs)

    def get_sync_response(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_response
        return get_sync_response(self, *args, **kwargs)

    def get_sync_configured(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_configured
        return get_sync_configured(self, *args, **kwargs)

    def is_sync(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import is_sync
        return is_sync(self, *args, **kwargs)

    def get_sync_watched_movies(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_watched_movies
        return get_sync_watched_movies(self, *args, **kwargs)

    def get_sync_watched_shows(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_watched_shows
        return get_sync_watched_shows(self, *args, **kwargs)

    def get_sync_collection_movies(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_collection_movies
        return get_sync_collection_movies(self, *args, **kwargs)

    def get_sync_collection_shows(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_collection_shows
        return get_sync_collection_shows(self, *args, **kwargs)

    def get_sync_playback_movies(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_playback_movies
        return get_sync_playback_movies(self, *args, **kwargs)

    def get_sync_playback_shows(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_playback_shows
        return get_sync_playback_shows(self, *args, **kwargs)

    def get_sync_watchlist_movies(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_watchlist_movies
        return get_sync_watchlist_movies(self, *args, **kwargs)

    def get_sync_watchlist_shows(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_watchlist_shows
        return get_sync_watchlist_shows(self, *args, **kwargs)

    def get_sync_watchlist_seasons(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_watchlist_seasons
        return get_sync_watchlist_seasons(self, *args, **kwargs)

    def get_sync_watchlist_episodes(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_watchlist_episodes
        return get_sync_watchlist_episodes(self, *args, **kwargs)

    def get_sync_favorites_movies(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_favorites_movies
        return get_sync_favorites_movies(self, *args, **kwargs)

    def get_sync_favorites_shows(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_favorites_shows
        return get_sync_favorites_shows(self, *args, **kwargs)

    def get_sync_ratings_movies(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_ratings_movies
        return get_sync_ratings_movies(self, *args, **kwargs)

    def get_sync_ratings_shows(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_ratings_shows
        return get_sync_ratings_shows(self, *args, **kwargs)

    def get_sync_ratings_seasons(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_ratings_seasons
        return get_sync_ratings_seasons(self, *args, **kwargs)

    def get_sync_ratings_episodes(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync_ratings_episodes
        return get_sync_ratings_episodes(self, *args, **kwargs)

    def get_sync(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.sync import get_sync
        return get_sync(self, *args, **kwargs)

    """
    TRAKT PROGRESS METHODS
    """

    def get_ondeck_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_ondeck_list
        return get_ondeck_list(self, *args, **kwargs)

    def get_towatch_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_towatch_list
        return get_towatch_list(self, *args, **kwargs)

    def get_inprogress_items(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_inprogress_items
        return get_inprogress_items(self, *args, **kwargs)

    def get_inprogress_shows_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_inprogress_shows_list
        return get_inprogress_shows_list(self, *args, **kwargs)

    def get_inprogress_shows(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_inprogress_shows
        return get_inprogress_shows(self, *args, **kwargs)

    def is_inprogress_show(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import is_inprogress_show
        return is_inprogress_show(self, *args, **kwargs)

    def get_episodes_watchcount(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_episodes_watchcount
        return get_episodes_watchcount(self, *args, **kwargs)

    def get_hiddenitems(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_hiddenitems
        return get_hiddenitems(self, *args, **kwargs)

    def get_upnext_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_upnext_list
        return get_upnext_list(self, *args, **kwargs)

    def get_upnext_episodes_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_upnext_episodes_list
        return get_upnext_episodes_list(self, *args, **kwargs)

    def get_upnext_episodes_listitems(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_upnext_episodes_listitems
        return get_upnext_episodes_listitems(self, *args, **kwargs)

    def get_show_progress(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_show_progress
        return get_show_progress(self, *args, **kwargs)

    def get_upnext_episodes(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_upnext_episodes
        return get_upnext_episodes(self, *args, **kwargs)

    def get_movie_playcount(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_movie_playcount
        return get_movie_playcount(self, *args, **kwargs)

    def get_movie_playprogress(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_movie_playprogress
        return get_movie_playprogress(self, *args, **kwargs)

    def get_episode_playprogress_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_episode_playprogress_list
        return get_episode_playprogress_list(self, *args, **kwargs)

    def get_episode_playprogress(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_episode_playprogress
        return get_episode_playprogress(self, *args, **kwargs)

    def get_episode_playcount(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_episode_playcount
        return get_episode_playcount(self, *args, **kwargs)

    def get_episodes_airedcount(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_episodes_airedcount
        return get_episodes_airedcount(self, *args, **kwargs)

    def get_season_episodes_airedcount(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.progress import get_season_episodes_airedcount
        return get_season_episodes_airedcount(self, *args, **kwargs)

    """
    TRAKT CALENDAR METHODS
    """

    def get_calendar(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar
        return get_calendar(self, *args, **kwargs)

    def get_calendar_episodes(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episodes
        return get_calendar_episodes(self, *args, **kwargs)

    @staticmethod
    def get_calendar_episode_item(*args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episode_item
        return get_calendar_episode_item(*args, **kwargs)

    @staticmethod
    def get_calendar_episode_item_bool(*args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episode_item_bool
        return get_calendar_episode_item_bool(*args, **kwargs)

    @staticmethod
    def get_stacked_item(*args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.calendar import get_stacked_item
        return get_stacked_item(*args, **kwargs)

    @staticmethod
    def stack_calendar_episodes(*args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.calendar import stack_calendar_episodes
        return stack_calendar_episodes(*args, **kwargs)

    def stack_calendar_tvshows(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.calendar import stack_calendar_tvshows
        return stack_calendar_tvshows(self, *args, **kwargs)

    def get_calendar_episodes_listitems(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episodes_listitems
        return get_calendar_episodes_listitems(self, *args, **kwargs)

    def get_calendar_episodes_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.trakt.methods.calendar import get_calendar_episodes_list
        return get_calendar_episodes_list(self, *args, **kwargs)
