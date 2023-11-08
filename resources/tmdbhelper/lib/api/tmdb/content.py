class TMDbMethods():

    """
    TMDb DETAILS METHODS
    """

    def get_genres(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_genres
        return get_genres(self, *args, **kwargs)

    @staticmethod
    def get_tmdb_multisearch_validfy(*args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_tmdb_multisearch_validfy
        return get_tmdb_multisearch_validfy(*args, **kwargs)

    def get_tmdb_multisearch_request(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_tmdb_multisearch_request
        return get_tmdb_multisearch_request(self, *args, **kwargs)

    def get_tmdb_multisearch(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_tmdb_multisearch
        return get_tmdb_multisearch(self, *args, **kwargs)

    def get_tmdb_id(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_tmdb_id
        return get_tmdb_id(self, *args, **kwargs)

    def get_tmdb_id_request(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_tmdb_id_request
        return get_tmdb_id_request(self, *args, **kwargs)

    def get_tmdb_id_from_query(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_tmdb_id_from_query
        return get_tmdb_id_from_query(self, *args, **kwargs)

    def get_collection_tmdb_id(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_collection_tmdb_id
        return get_collection_tmdb_id(self, *args, **kwargs)

    def get_tmdb_id_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_tmdb_id_list
        return get_tmdb_id_list(self, *args, **kwargs)

    def get_tvshow_nextaired(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_tvshow_nextaired
        return get_tvshow_nextaired(self, *args, **kwargs)

    def get_details_request(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_details_request
        return get_details_request(self, *args, **kwargs)

    def get_details(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_details
        return get_details(self, *args, **kwargs)

    def get_next_episode(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.details import get_next_episode
        return get_next_episode(self, *args, **kwargs)

    """
    TMDb LIST METHODS
    """

    def get_flatseasons_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_flatseasons_list
        return get_flatseasons_list(self, *args, **kwargs)

    def get_episode_group_episodes_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_episode_group_episodes_list
        return get_episode_group_episodes_list(self, *args, **kwargs)

    def get_episode_group_seasons_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_episode_group_seasons_list
        return get_episode_group_seasons_list(self, *args, **kwargs)

    def get_episode_groups_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_episode_groups_list
        return get_episode_groups_list(self, *args, **kwargs)

    def get_videos_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_videos_list
        return get_videos_list(self, *args, **kwargs)

    def get_season_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_season_list
        return get_season_list(self, *args, **kwargs)

    def get_episode_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_episode_list
        return get_episode_list(self, *args, **kwargs)

    def get_cast_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_cast_list
        return get_cast_list(self, *args, **kwargs)

    @staticmethod
    def get_downloaded_list(*args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_downloaded_list
        return get_downloaded_list(*args, **kwargs)

    @staticmethod
    def get_daily_list(*args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_daily_list
        return get_daily_list(*args, **kwargs)

    @staticmethod
    def get_all_items_list(*args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_all_items_list
        return get_all_items_list(*args, **kwargs)

    def get_search_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_search_list
        return get_search_list(self, *args, **kwargs)

    def get_basic_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_basic_list
        return get_basic_list(self, *args, **kwargs)

    def get_discover_list(self, *args, **kwargs):
        from tmdbhelper.lib.api.tmdb.methods.lists import get_discover_list
        return get_discover_list(self, *args, **kwargs)
