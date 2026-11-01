from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting


class SyncPreparation:
    """Refresh the synced play data that item details read, for one sync item type."""

    sync_keys = {
        'movie': (('plays', ), ('playback_progress', )),
        'show': (('plays', 'watched_episodes', 'aired_episodes', ), ('playback_progress', )),
    }
    mediatype_item_types = {'movie': 'movie', 'tvshow': 'show', 'season': 'show', 'episode': 'show'}
    hint_movie_infos = ('stars_in_movies', 'crew_in_movies', 'trakt_userlist', 'stars_in_both', 'crew_in_both', )
    hint_movie_types = ('movie', 'both', )
    hint_show_infos = (
        'stars_in_tvshows', 'crew_in_tvshows', 'trakt_userlist', 'trakt_calendar', 'stars_in_both',
        'crew_in_both', 'specified_episodes', )
    hint_show_types = ('tv', 'season', 'both', )

    def __init__(self, item_type):
        self.item_type = item_type

    @staticmethod
    def is_enabled():
        """Watched status and play progress both follow the watched indicators setting."""
        return bool(get_setting('trakt_watchedindicators'))

    @classmethod
    def get_item_types(cls, mediatypes):
        """The sync item types for a batch of item details."""
        return {cls.mediatype_item_types[i] for i in mediatypes if i in cls.mediatype_item_types}

    @classmethod
    def get_hint_item_types(cls, info=None, tmdb_type=None):
        """The sync item types a list is likely to need, before its items are known."""
        item_types = set()
        if tmdb_type in cls.hint_movie_types or info in cls.hint_movie_infos:
            item_types.add('movie')
        if tmdb_type in cls.hint_show_types or info in cls.hint_show_infos:
            item_types.add('show')
        return item_types

    @cached_property
    def syncdata(self):
        return self.get_syncdata()

    def get_syncdata(self):
        from tmdbhelper.lib.sync.datasync import SyncDataFactory
        return SyncDataFactory()

    def sync(self):
        for keys in self.sync_keys[self.item_type]:
            self.syncdata.sync(self.item_type, keys)
