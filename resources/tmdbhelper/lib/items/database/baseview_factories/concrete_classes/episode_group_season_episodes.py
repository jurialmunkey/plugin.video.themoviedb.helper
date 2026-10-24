from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.episode_group_seasons import EpisodeGroupSeasonsList


class EpisodeGroupEpisodesList(EpisodeGroupSeasonsList):
    table = 'episode_group_season_episodes'
    parent_mediatype = 'episode_group_season'
    cached_data_keys = (
        'm.*', 's.ordering AS group_ordering',
        'IFNULL(group_title.value, e.title) AS title',
        'IFNULL(group_plot.value, e.plot) AS plot',
    )
    cached_data_table = (
        'episode_group_season_episodes m '
        'INNER JOIN episode_group_seasons s ON s.tmdb_id=m.season_group_id '
        'INNER JOIN episode e ON e.id=m.id '
        'LEFT JOIN custom group_title ON group_title.parent_id=s.id AND group_title.key="episode."||m.tmdb_id||".title" '
        'LEFT JOIN custom group_plot ON group_plot.parent_id=s.id AND group_plot.key="episode."||m.tmdb_id||".plot"'
    )
    cached_data_conditions = 'm.group_id=? AND m.tvshow_id=? AND m.season_group_id=? ORDER BY m.ordering'

    @cached_property
    def parent_database(self):
        database_obj = super().parent_database
        database_obj.tmdb_id = self.season_group_id
        database_obj.group_id = self.group_id
        return database_obj

    @property
    def cached_data_values(self):
        return (*super().cached_data_values, self.season_group_id)


class Tvshow(EpisodeGroupEpisodesList):
    pass
