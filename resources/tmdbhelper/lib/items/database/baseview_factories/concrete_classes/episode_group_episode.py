from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.episode_group_seasons import EpisodeGroupSeasonsList


class Episode(EpisodeGroupSeasonsList):
    table = 'episode_group_season_episodes'
    cached_data_keys = (
        'm.tmdb_id', 's.ordering AS virtual_season', 'm.ordering + 1 AS virtual_episode',
    )
    cached_data_table = (
        'episode_group_season_episodes m '
        'INNER JOIN episode_group_seasons s ON s.tmdb_id=m.season_group_id'
    )
    cached_data_conditions = (
        'm.group_id=? AND m.tvshow_id=? AND m.season=? AND m.episode=? '
        'ORDER BY s.ordering, m.ordering LIMIT 1'
    )

    @property
    def cached_data_values(self):
        return (*super().cached_data_values, self.season, self.episode)
