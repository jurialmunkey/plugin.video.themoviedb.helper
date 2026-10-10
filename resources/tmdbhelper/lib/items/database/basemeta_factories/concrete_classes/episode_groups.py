from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList
from tmdbhelper.lib.items.database.tabledef import (
    EPISODE_GROUP_COLUMNS, EPISODE_GROUP_SEASON_COLUMNS, EPISODE_GROUP_SEASON_EPISODE_COLUMNS,
)


class EpisodeGroups(ItemDetailsList):
    table = 'episode_groups'
    keys = tuple(EPISODE_GROUP_COLUMNS)
    conditions = 'tvshow_id=?'


class EpisodeGroupSeasons(EpisodeGroups):
    table = 'episode_group_seasons'
    keys = tuple(EPISODE_GROUP_SEASON_COLUMNS)
    conditions = 'group_id=? ORDER BY ordering'

    @property
    def values(self):
        return (self.tmdb_id, )

    @staticmethod
    def get_count_keys():
        keys = []
        for key, join, condition in (
            ('totalepisodes', '', ''),
            ('airedepisodes', 'INNER JOIN episode e ON e.id=m.id', 'AND e.premiered<=DATE("now", "localtime")'),
            ('watchedepisodes', 'INNER JOIN simplecache w ON w.id=m.id', 'AND w.plays>0'),
        ):
            keys.append(
                f'(SELECT COUNT(*) FROM episode_group_season_episodes m {join} '
                f'WHERE m.season_group_id=episode_group_seasons.tmdb_id {condition}) AS {key}')
        return tuple(keys)

    def delete_cached_data(self):
        self.cache.del_list_values(
            table='baseitem', values=self.values,
            conditions='id IN (SELECT id FROM episode_group_seasons WHERE group_id=?)',
            connection=self.open_connection)


class EpisodeGroupSeasonEpisodes(EpisodeGroupSeasons):
    table = 'episode_group_season_episodes'
    keys = tuple(EPISODE_GROUP_SEASON_EPISODE_COLUMNS)
    conflict_constraint = 'id, season_group_id'
