from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.items.media import LibraryMedia


class LibrarySeason(LibraryMedia):

    tmdb_type = 'tv'
    mediatype = 'season'
    base_type = 'tvshows'

    strm_filename = None
    strm_contents = None
    info_filename = None
    info_contents = None

    """
    Meta Data
    """

    @cached_property
    def season(self):
        return self.infolabels.get_key('season') or 0

    def get_name(self):
        return f'Season {self.season}'

    """
    Sync Data
    """

    @cached_property
    def episodes_sync(self):
        from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
        try:
            return BaseViewFactory('episodes', 'tv', int(self.tmdb_id), season=self.season)
        except TypeError:
            return

    @cached_property
    def episodes_sync_data(self):
        if not self.episodes_sync:
            return
        return self.episodes_sync.data

    @cached_property
    def episodes(self):
        if not self.episodes_sync_data:
            return []
        return [
            i for i in (
                self.get_episode(episode)
                for episode in self.episodes_sync_data
            ) if i.episode != 0 and i.season != 0
        ]

    def get_episode(self, sync_data):
        from tmdbhelper.lib.update.items.episode import LibraryEpisode
        episode = LibraryEpisode(self.tmdb_id)
        episode.sync_data = self.key_getter(sync_data)
        episode.cache = self.cache
        episode.tvshow_id = self.tvshow_id
        episode.folders = self.folders + episode.folders
        return episode
