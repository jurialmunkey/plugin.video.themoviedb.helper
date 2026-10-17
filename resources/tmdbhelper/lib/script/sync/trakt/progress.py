from tmdbhelper.lib.script.sync.trakt.item import ItemSync
from tmdbhelper.lib.script.sync.progress import ItemProgress as BasicItemProgress
from tmdbhelper.lib.addon.dialog import busy_decorator


class ItemProgress(ItemSync, BasicItemProgress):
    @busy_decorator
    def get_sync_response(self):
        """ Called after user selects choice """
        return self.trakt_api.delete_response('sync', 'playback', self.playback_id)
