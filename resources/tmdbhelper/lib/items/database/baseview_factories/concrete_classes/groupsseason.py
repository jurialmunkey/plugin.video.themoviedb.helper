from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH


class GroupsSeason(MediaList):
    cached_data_table = table = 'tvshow'
    keys = ('id', 'tmdb_id', 'title', 'plot')
    cached_data_check_key = 'id'
    cached_data_base_conditions = (
        'tvshow.id=? AND EXISTS ('
        'SELECT 1 FROM episode_groups WHERE episode_groups.tvshow_id=tvshow.id'
        ')'
    )
    item_mediatype = 'tvshow'
    item_tmdb_type = 'tv'
    item_label_key = 'title'
    item_specialseason = get_localized(32541)

    @property
    def data_cond(self):
        return bool(self.tmdb_id and self.parent_item_data)

    def map_label(self, i):
        return self.item_specialseason

    def map_item_infolabels(self, i):
        infolabels = super().map_item_infolabels(i)
        infolabels['title'] = self.item_specialseason
        return infolabels

    def map_item_infoproperties(self, i):
        return {
            'specialseason': self.item_specialseason,
            'IsSpecial': 'true',
            'label_override': self.item_specialseason,
        }

    def map_item_unique_ids(self, i):
        return {'tmdb': self.tmdb_id, 'tvshow.tmdb': self.tmdb_id}

    def map_item_art(self, i):
        art = self.parent_item_data['art'].copy()
        art['thumb'] = f'{ADDONPATH}/resources/icons/themoviedb/episodes.png'
        art['poster'] = art['thumb']
        return art

    def map_item_params(self, i):
        return {
            'info': 'episode_groups',
            'tmdb_type': 'tv',
            'tmdb_id': self.tmdb_id,
        }


class Tvshow(GroupsSeason):
    pass
