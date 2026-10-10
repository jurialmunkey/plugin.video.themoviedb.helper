from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseclass import BaseItem


class EpisodeGroup(BaseItem):

    def get_unique_ids(self, unique_ids):
        unique_ids.update({
            'tmdb': self.get_data_value('tmdb_id'),
            'tvshow.tmdb': self.get_data_value('tvshow_tmdb_id'),
        })
        return unique_ids


class EpisodeGroupSeason(EpisodeGroup):

    def get_infoproperties_special(self, infoproperties):
        infoproperties['group_season'] = self.get_data_value('ordering')
        infoproperties.update({
            key: self.get_data_value(key)
            for key in ('totalepisodes', 'airedepisodes', 'watchedepisodes')
        })
        return infoproperties
