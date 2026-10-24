from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.baseclass import BaseList


class EpisodeGroupsList(BaseList):
    table = 'episode_groups'
    cached_data_check_key = 'tmdb_id'
    cached_data_conditions = 'tvshow_id=?'

    @property
    def cached_data_table(self):
        return self.table

    @property
    def cached_data_values(self):
        return (self.item_id, )

    @property
    def data_cond(self):
        return bool(self.tmdb_id and self.parent_item_data)

    @staticmethod
    def map_item(item):
        return dict(item)


class Tvshow(EpisodeGroupsList):
    pass
