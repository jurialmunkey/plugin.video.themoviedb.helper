from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.nextmeta import SyncNextEpisodeItem, SyncAllNextEpisodesMetaItem, SyncAllNextEpisodesMeta
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory


class MDbListSyncBaseView:
    def __init__(self, tmdb):
        self.tmdb = tmdb

    @cached_property
    def baseview_factory(self):
        return BaseViewFactory('flatseasons', 'tv', self.tmdb)

    @cached_property
    def data(self):
        return {'seasons': self.seasons}

    @cached_property
    def seasons(self):
        seasons = {}
        for i in self.baseview_factory.data:
            number = i['params']['season']
            season = seasons.setdefault(number, {'number': number, 'episodes': []})
            season['episodes'].append({'number': i['params']['episode']})
        return list(seasons.values())


class MDbListSyncNextEpisodeItem(SyncNextEpisodeItem):

    reset_at = None  # MDbList doesnt track this rewatch data ?

    def is_next_episode(self, season, episode):
        if self.main.instance_syncdata.get_episode_playcount(  # TODO Maybe a faster way than this due to timerlock e.g. check next episode ID and then all episodes later
            self.tmdb_id,
            season=season['number'],
            episode=episode['number']
        ):
            return False
        return True

    @cached_property
    def response(self):
        if not self.tmdb_id:
            return {}
        return MDbListSyncBaseView(self.tmdb_id).data


class MDbListSyncAllNextEpisodesMetaItem(SyncAllNextEpisodesMetaItem):
    sync_item_class = MDbListSyncNextEpisodeItem


class MDbListSyncAllNextEpisodesMeta(SyncAllNextEpisodesMeta):
    meta_item_getter = MDbListSyncAllNextEpisodesMetaItem
