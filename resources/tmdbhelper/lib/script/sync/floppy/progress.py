from jurialmunkey.parser import try_int
from tmdbhelper.lib.script.sync.floppy.item import ItemSync
from tmdbhelper.lib.script.sync.progress import ItemProgress as BasicItemProgress


class ItemProgress(ItemSync, BasicItemProgress):

    def get_floppy_response(self):
        postdata = {'media_type': self.trakt_type, 'ids': {'tmdb': f'{self.tmdb_id}'}}
        if self.trakt_type == 'episode':
            postdata.update({'season_number': try_int(self.season), 'episode_number': try_int(self.episode)})
        return self.floppy_api.get_response_send('playback', 'progress', postdata=postdata, method='json_delete')

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.invalidate_activity('playback', item_type=self.trakt_type)  # Floppy playback syncs shows as episodes
        self.syncdata.reset_lastactivities()
        self.set_floppy_reload()
