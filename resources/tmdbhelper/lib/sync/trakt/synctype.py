from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import convert_timestamp, is_unaired_timestamp
from tmdbhelper.lib.addon.consts import HALFDAY_EXPIRY
from tmdbhelper.lib.sync.datatype import timerlock
from tmdbhelper.lib.sync.trakt.datatype import TraktDataType, TraktDataTypeEpisodesInShows


class SyncHiddenProgressWatched(TraktDataType):
    keys = ('hidden_at', )
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_watched'
    key_prefix = 'progress_watched'

    @timerlock
    def sync_func(self):
        """ Get items that are hidden on Trakt """
        from tmdbhelper.lib.addon.logger import TimerFunc
        with TimerFunc(f'Sync: {self.__class__.__name__} get_response_sync users {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            return self.get_response_sync(
                'users', self.method,
                type=f'{self.item_type}s'
            )


class SyncHiddenProgressCollected(SyncHiddenProgressWatched):
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_collected'
    key_prefix = 'progress_collected'


class SyncHiddenCalendar(SyncHiddenProgressWatched):
    last_activities_key = 'hidden_at'
    method = 'hidden/calendar'
    key_prefix = 'calendar'


class SyncHiddenDropped(SyncHiddenProgressWatched):
    last_activities_key = 'dropped_at'
    method = 'hidden/dropped'
    key_prefix = 'dropped'


class SyncWatched(TraktDataTypeEpisodesInShows):
    keys = ('plays', 'last_watched_at', 'last_updated_at', 'aired_episodes', 'watched_episodes', 'reset_at', )
    last_activities_key = 'watched_at'
    sync_kwgs = {'extended': 'full,progress'}
    method = 'watched'


class SyncPlayback(TraktDataTypeEpisodesInShows):
    keys = ('progress', 'paused_at', 'id', )
    last_activities_key = 'paused_at'
    sync_kwgs = {'extended': 'full'}
    method = 'playback'
    key_prefix = 'playback'


class SyncRatings(TraktDataType):
    keys = ('rating', 'rated_at', )
    last_activities_key = 'rated_at'
    method = 'ratings'


class SyncFavorites(TraktDataType):
    keys = ('rank', 'listed_at', 'notes', )
    last_activities_key = 'favorited_at'
    sync_kwgs = {'extended': 'full'}
    method = 'favorites'
    key_prefix = 'favorites'


class SyncWatchlist(TraktDataType):
    keys = ('rank', 'listed_at', 'notes', )
    last_activities_key = 'watchlisted_at'
    sync_kwgs = {'extended': 'full'}
    method = 'watchlist'
    key_prefix = 'watchlist'


class SyncCollection(TraktDataTypeEpisodesInShows):
    keys = ('last_collected_at', 'last_updated_at', )
    last_activities_key = 'collected_at'
    method = 'collection'
    key_prefix = 'collection'


class SyncNextEpisodeItem:
    def __init__(self, parent, item):
        self.parent = parent  # SyncAllNextEpisodes SyncNextEpisodes class
        self.item = item

    @cached_property
    def tmdb_id(self):
        try:
            return self.item['tmdb_id']
        except (KeyError, TypeError, NameError):
            return

    @cached_property
    def trakt_slug(self):
        try:
            return self.item['trakt_slug']
        except (KeyError, TypeError, NameError):
            return

    @property
    def get_response_sync(self):
        return self.parent.get_response_sync

    @cached_property
    def reset_at(self):
        return self.response.get('reset_at')

    @cached_property
    def reset_at_datetime_obj(self):
        if not self.reset_at:
            return
        return convert_timestamp(self.reset_at)

    @cached_property
    def next_episode(self):
        try:
            return self.response['next_episode']
        except (KeyError, TypeError, NameError):
            return

    @cached_property
    def next_episode_aired_at(self):
        try:
            return self.next_episode['first_aired']
        except (KeyError, TypeError, NameError):
            return

    @cached_property
    def next_episode_is_unaired(self):
        return is_unaired_timestamp(self.next_episode_aired_at)

    @cached_property
    def next_episode_season(self):
        try:
            return self.next_episode['season']
        except (KeyError, TypeError, NameError):
            return

    @cached_property
    def next_episode_number(self):
        try:
            return self.next_episode['number']
        except (KeyError, TypeError, NameError):
            return

    def get_next_episode_id(self, season, number):
        return f'tv.{self.tmdb_id}.{season}.{number}'

    def is_next_episode(self, episode):
        if not episode.get('completed'):
            return True
        if not self.reset_at_datetime_obj:
            return False
        if convert_timestamp(episode.get('last_watched_at')) < self.reset_at_datetime_obj:
            return True
        return False

    @cached_property
    def all_next_episodes(self):
        """
        Returns a generator of all next episodes by comparing againt reset_at date and timestamps
        """
        if not self.response:
            return iter(())

        return (
            self.get_next_episode_id(season['number'], episode['number'])
            for season in self.response_seasons for episode in (season.get('episodes') or [])
            if self.is_next_episode(episode)
        )

    @cached_property
    def response(self):
        if not self.trakt_slug:
            return
        return self.get_response_sync(
            f'shows/{self.trakt_slug}/progress/watched',
            extended='full',
        )

    @cached_property
    def response_seasons(self):
        return self.response.get('seasons') or []

    @cached_property
    def next_episode_id(self):
        if not self.response:
            return
        if not self.reset_at and self.next_episode and not self.next_episode_is_unaired:
            return self.get_next_episode_id(self.next_episode_season, self.next_episode_number)
        try:
            return next(self.all_next_episodes)
        except StopIteration:
            return

    @cached_property
    def next_episode_id_dictionary(self):
        if not self.next_episode_id:
            return {}
        return {
            "next_episode_id": self.next_episode_id,
            "next_episode_aired_at": self.next_episode_aired_at,
            "show": {
                "ids": {
                    "tmdb": self.tmdb_id,
                    "slug": self.trakt_slug
                }
            }
        }


class SyncAllNextEpisodesMetaItem:

    dialog_progress_bg_text_fstr = '{sync.tmdb_id} {sync.trakt_slug}'

    def __init__(self, main, item):
        self.main = main
        self.item = item

    @property
    def is_sync(self):
        return bool(self.sync.all_next_episodes)

    @property
    def dialog_progress_bg_text(self):
        text = self.dialog_progress_bg_text_fstr.format(sync=self.sync)
        text = f'Sync: {text}' if self.is_sync else f'Skip: {text}'
        return text

    def update_dialog_progress(self):
        self.main.dialog_progress_bg.increment()
        self.main.dialog_progress_bg.set_message(self.dialog_progress_bg_text)

    @cached_property
    def sync(self):
        return SyncNextEpisodeItem(self.main, self.item)

    @cached_property
    def data(self):
        self.update_dialog_progress()
        return [self.get_item(item_id) for item_id in self.sync.all_next_episodes]

    def get_item(self, item_id):
        tmdb_type, tmdb_id, season_number, episode_number = item_id.split('.')
        return {
            "show": {
                "ids": {
                    "tmdb": self.item["tmdb_id"],
                    "slug": self.item["trakt_slug"]
                }
            },
            "upnext_episode_id": item_id,
            "type": "episode",
            "episode": {
                "season": season_number,
                "number": episode_number,
            }
        }


class SyncAllNextEpisodesMeta:

    meta_item_getter = SyncAllNextEpisodesMetaItem

    def __init__(self, main):
        self.main = main

    def get_items(self, item):
        return self.meta_item_getter(self.main, item).data

    @cached_property
    def item_queue(self):
        self.main.dialog_progress_bg.max_value = len(self.sd.items)
        from tmdbhelper.lib.addon.thread import ParallelThread
        with ParallelThread(self.sd.items, self.get_items) as pt:
            item_queue = pt.queue
        return item_queue

    @cached_property
    def items(self):
        return [i for items in self.item_queue for i in items if i]

    @cached_property
    def sd(self):
        sd = self.main.instance_syncdata.get_all_unhidden_shows_inprogress_getter()
        sd.additional_keys = ('trakt_slug', )
        return sd


class SyncAllNextEpisodes(TraktDataTypeEpisodesInShows):
    keys = ('upnext_episode_id', )
    last_activities_key = 'watched_at'
    method = 'all_next_episodes'
    expiry_time = HALFDAY_EXPIRY

    @timerlock
    def sync_func(self):
        """ Get next episodes on Trakt """
        from tmdbhelper.lib.addon.logger import TimerFunc
        with TimerFunc(
            f'Sync: {self.__class__.__name__} get_meta {self.method} {self.item_type}',
            inline=True,
            log_threshold=0.001
        ):
            return SyncAllNextEpisodesMeta(self).items


class SyncNextEpisodesMetaItem(SyncAllNextEpisodesMetaItem):
    dialog_progress_bg_text_fstr = '{sync.next_episode_id}'

    @cached_property
    def data(self):
        return self.sync.next_episode_id_dictionary

    @property
    def is_sync(self):
        return bool(self.sync.next_episode_id)


class SyncNextEpisodesMeta(SyncAllNextEpisodesMeta):
    meta_item_getter = SyncNextEpisodesMetaItem

    @cached_property
    def items(self):
        return [i for i in self.item_queue if i]


class SyncNextEpisodes(SyncAllNextEpisodes):
    keys = ('next_episode_id', 'next_episode_aired_at')
    last_activities_key = 'watched_at'
    method = 'nextup'
    expiry_time = HALFDAY_EXPIRY

    @timerlock
    def sync_func(self):
        """ Get next episodes on Trakt """
        from tmdbhelper.lib.addon.logger import TimerFunc

        with TimerFunc(
            f'Sync: {self.__class__.__name__} get_meta {self.method} {self.item_type}',
            inline=True,
            log_threshold=0.001
        ):
            return SyncNextEpisodesMeta(self).items
