from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.flatseasons import FlatSeasonMediaList
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.anticipatedseason import AnticipatedSeasonMediaListMixin


class AnticipatedEpisodeMediaList(AnticipatedSeasonMediaListMixin, FlatSeasonMediaList):
    cached_data_conditions_base = 'episode.tvshow_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? AND episode.premiered>DATE("now") AND season.season>0 ORDER BY season.season ASC, episode.episode ASC'


class Tvshow(AnticipatedEpisodeMediaList):
    pass
