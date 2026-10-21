from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.script.sync.floppy.item import ItemSync, FloppyResponses
from tmdbhelper.lib.script.sync.actions import (
    ItemWatched as BasicItemWatched,
    ItemUnwatched as BasicItemUnwatched,
    ItemWatchlist as BasicItemWatchlist,
    ItemCollection as BasicItemCollection,
    ItemDropped as BasicItemDropped,
)


class ItemWatched(ItemSync, BasicItemWatched):
    """ Floppy records one play per request so whole seasons and shows are sent episode by episode """

    activity_methods = ('watched', 'nextup', 'all_next_episodes', 'playback', )
    floppy_method = 'json'

    @cached_property
    def episodes(self):
        return self.get_episodes()

    def get_episodes(self):
        if self.trakt_type == 'episode':
            return [(self.season, self.episode)]
        from tmdbhelper.lib.script.sync.floppy.episodes import FloppyAiredEpisodes
        return FloppyAiredEpisodes(self.tmdb_id, self.season).items

    @cached_property
    def watch_paths(self):
        return self.get_watch_paths()

    def get_watch_paths(self):
        if self.trakt_type == 'movie':
            return [(*self.media_path, 'watch', )]
        return [(*self.get_episode_path(season, episode), 'watch', ) for season, episode in self.episodes]

    def get_watch_response(self, path):
        return self.get_floppy_send(*path, postdata={}, method=self.floppy_method)

    def get_floppy_response(self):
        from tmdbhelper.lib.addon.thread import ParallelThread
        self.library_media_type  # Resolve once before threading
        with ParallelThread(self.watch_paths, self.get_watch_response) as pt:
            responses = pt.queue
        return FloppyResponses(responses)


class ItemUnwatched(ItemWatched, BasicItemUnwatched):
    """ Floppy removes the most recent play per request so repeat for every synced play """

    floppy_method = 'json_delete'

    def get_episode_plays(self, season, episode):
        return self.syncdata.get_episode_playcount(self.tmdb_id, season, episode) or 0

    def get_episodes(self):
        return [i for i in super().get_episodes() if self.get_episode_plays(*i)]

    def get_watch_paths(self):
        if self.trakt_type == 'movie':
            plays = self.syncdata.get_movie_playcount(self.tmdb_id) or 1
            return [(*self.media_path, 'watch', )] * plays
        return [
            (*self.get_episode_path(season, episode), 'watch', )
            for season, episode in self.episodes
            for _ in range(self.get_episode_plays(season, episode))
        ]

    def get_floppy_response(self):
        """ Plays of the same item are removed one at a time """
        return FloppyResponses([self.get_watch_response(path) for path in self.watch_paths])


class ItemWatchlist(ItemSync, BasicItemWatchlist):
    """ Floppy watchlist is any entry with the Planning status """

    activity_methods = ('watchlist', )

    def get_planning_consumption_ids(self):
        from tmdbhelper.lib.sync.floppy.dataconf import FLOPPY_STATUS_PLANNING
        history = self.get_floppy_json(*self.media_path, 'history') or {}
        return [i['consumption_id'] for i in history.get('results') or [] if i['status'] == FLOPPY_STATUS_PLANNING]

    def get_remove_response(self, consumption_id):
        return self.get_floppy_send(*self.media_path, 'history', consumption_id, method='json_delete')

    def get_add_response(self):
        postdata = {'source': 'tmdb', 'media_id': f'{self.tmdb_id}', 'status': 0}
        return self.get_floppy_send('media', self.floppy_media_type, postdata=postdata, method='json')

    def get_floppy_response(self):
        if not self.remove:
            return self.get_add_response()
        return FloppyResponses([self.get_remove_response(i) for i in self.get_planning_consumption_ids()])


class ItemCollection(ItemSync, BasicItemCollection):
    """ Floppy collection sync is not supported yet """

    def get_is_available(self):
        return False


class ItemDropped(ItemSync, BasicItemDropped):
    activity_methods = ('dropped', 'nextup', 'all_next_episodes', 'watched', )

    def get_floppy_response(self):
        from tmdbhelper.lib.sync.floppy.dataconf import FLOPPY_STATUS_DROPPED, FLOPPY_STATUS_IN_PROGRESS
        postdata = {'status': FLOPPY_STATUS_IN_PROGRESS if self.remove else FLOPPY_STATUS_DROPPED}
        return self.get_floppy_send(*self.media_path, postdata=postdata, method='json_patch')

    def reset_lastactivities(self):
        super().reset_lastactivities()
        if self.is_successful_sync:
            self.delete_listdata()
