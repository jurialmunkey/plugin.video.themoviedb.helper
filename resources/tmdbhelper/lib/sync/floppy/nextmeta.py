from jurialmunkey.parser import try_int
from tmdbhelper.lib.sync.mdblist.nextmeta import MDbListSyncAllNextEpisodesMetaItem, MDbListSyncAllNextEpisodesMeta


class FloppySyncAllNextEpisodesMetaItem(MDbListSyncAllNextEpisodesMetaItem):
    """ Compares TMDb episodes against synced watched episodes and returns flat Floppy sync records """

    def get_item(self, item_id):
        tmdb_type, tmdb_id, season_number, episode_number = item_id.split('.')
        return {
            'type': 'episode',
            'tmdb_id': try_int(tmdb_id),
            'season_number': try_int(season_number),
            'episode_number': try_int(episode_number),
            'upnext_episode_id': item_id,
        }


class FloppySyncAllNextEpisodesMeta(MDbListSyncAllNextEpisodesMeta):
    meta_item_getter = FloppySyncAllNextEpisodesMetaItem
