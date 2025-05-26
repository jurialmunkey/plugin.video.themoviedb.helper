from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.anticipatedseason import AnticipatedSeasonMediaList
from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH


class UpNextSeason(AnticipatedSeasonMediaList):
    table = 'season'
    item_specialseason = get_localized(32043)
    cached_data_conditions_base = 'season.tvshow_id=? AND totalepisodes>0 ORDER BY season.season DESC LIMIT 1'

    def map_item_art(self, i):
        map_item_art = self.parent_item_data['art']
        map_item_art['thumb'] = f'{ADDONPATH}/resources/icons/trakt/up-next.png'
        map_item_art['poster'] = map_item_art['thumb']
        return map_item_art

    def get_cached_data_keys(self):
        """ SELECT """
        cached_data_keys = [f'{self.table}.{k}' for k in self.keys if k != 'plot']
        cached_data_keys.extend([
            'tvshow.title AS tvshowtitle',
            'tvshow.tagline as tagline',
            'ifnull(season.plot, tvshow.plot) as plot',
            (
                '(    SELECT COUNT(simplecache.item_type) '
                '     FROM simplecache WHERE simplecache.id LIKE season.tvshow_id || ".%"'
                '                        AND simplecache.last_watched_at IS NULL'
                '                        AND simplecache.item_type = \'episode\''
                '     GROUP BY simplecache.item_type'
                ') as totalepisodes'
            )
        ])
        return tuple(cached_data_keys)

    def map_item_params(self, i):
        return {
            'info': 'trakt_upnext',
            'tmdb_type': 'tv',
            'tmdb_id': self.tmdb_id,
            'hide_unaired': 'true'
        }


class Tvshow(UpNextSeason):
    pass
