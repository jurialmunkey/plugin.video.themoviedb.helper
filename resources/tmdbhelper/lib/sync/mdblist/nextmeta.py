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
        return self.get_next_episode_id(season['number'], episode['number']) not in self.watched_episode_ids

    @cached_property
    def response(self):
        if not self.tmdb_id:
            return {}
        return MDbListSyncBaseView(self.tmdb_id).data


class MDbListSyncAllNextEpisodesMetaItem(SyncAllNextEpisodesMetaItem):
    sync_item_class = MDbListSyncNextEpisodeItem


class MDbListSyncAllNextEpisodesMeta(SyncAllNextEpisodesMeta):
    meta_item_getter = MDbListSyncAllNextEpisodesMetaItem

    def get_watched_episode_ids(self):
        sd = self.main.instance_syncdata.get_all_episode_playcounts_getter()
        return frozenset(i['id'] for i in sd.items if i['plays'])

    def get_item_queue(self):
        self.watched_episode_ids = self.get_watched_episode_ids()
        return super().get_item_queue()

    def get_items(self, item):
        meta_item = self.meta_item_getter(self.main, item)
        meta_item.sync.watched_episode_ids = self.watched_episode_ids
        return meta_item.data
