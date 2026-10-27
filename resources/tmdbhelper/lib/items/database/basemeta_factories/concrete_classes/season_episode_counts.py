from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Season


class SeasonEpisodeCounts(Season):
    cached_data_keys = ('season', 'episode_count')
    conditions = 'tvshow_id=? AND season>0'
