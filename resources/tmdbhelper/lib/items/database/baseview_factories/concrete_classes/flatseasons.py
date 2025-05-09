from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList


class FlatSeasonMediaList(MediaList):
    table = 'episode'
    cached_data_conditions_base = 'episode.tvshow_id=? AND baseitem.expiry>=? ORDER BY season=0, season ASC, episode ASC'
    cached_data_check_key = 'episode'
    keys = ()
    item_mediatype = 'episode'
    item_tmdb_type = 'tv'
    item_label_key = 'title'

    filter_key_map = {
        'season': 'season',
        'episode': 'episode',
        'year': 'year',
        'title': 'title',
        'votes': 'votes',
        'premiered': 'premiered',
        'rating': 'rating',
    }

    @property
    def cached_data_table(self):
        return (
            'episode'
            ' INNER JOIN season ON episode.season_id = season.id'
            ' INNER JOIN baseitem ON episode.tvshow_id = baseitem.id'
        )

    @property
    def cached_data_keys(self):
        return (
            'episode', 'episode.year as year', 'episode.plot as plot', 'episode.title as title',
            'episode.premiered as premiered', 'episode.rating as rating', 'episode.votes as votes',
            'season.season as season'
        )

    @property
    def cached_data_values(self):
        return (self.item_id, self.current_time)

    def map_item_unique_ids(self, i):
        return {
            'tmdb': self.tmdb_id,
            'tvshow.tmdb': self.tmdb_id
        }

    def map_item_params(self, i):
        return {
            'info': 'details',
            'tmdb_type': self.item_tmdb_type,
            'tmdb_id': self.tmdb_id,
            'season': i['season'],
            'episode': i['episode']
        }


class Tvshow(FlatSeasonMediaList):
    pass
