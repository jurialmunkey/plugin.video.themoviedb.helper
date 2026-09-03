from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import convert_timestamp, is_unaired_timestamp


class SyncNextEpisodeItem:
    def __init__(self, main, item):
        self.main = main  # SyncAllNextEpisodes SyncNextEpisodes class
        self.item = item

    def get_key(self, key):
        try:
            return self.item[key]
        except (KeyError, TypeError, NameError, IndexError):
            return

    @cached_property
    def tmdb_id(self):
        return self.get_key('tmdb_id')

    @cached_property
    def trakt_slug(self):
        return self.get_key('trakt_slug')

    @cached_property
    def id_data(self):
        return {
            k: v for k, v in (
                ('tmdb', self.tmdb_id),
                ('slug', self.trakt_slug),
            ) if v
        }

    @property
    def get_response_sync(self):
        return self.main.get_response_sync

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

    def is_next_episode(self, season, episode):
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
            if self.is_next_episode(season, episode)
        )

    @cached_property
    def response(self):
        return {}  # GET DATA ABOUT EPISODES HERE

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
            "show": {"ids": self.id_data}
        }


class SyncAllNextEpisodesMetaItem:

    dialog_progress_bg_text_fstr = '{sync.tmdb_id} {sync.trakt_slug}'
    sync_item_class = SyncNextEpisodeItem

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
        return self.sync_item_class(self.main, self.item)

    @cached_property
    def data(self):
        data = [self.get_item(item_id) for item_id in self.sync.all_next_episodes]
        self.update_dialog_progress()
        return data

    def get_item(self, item_id):
        tmdb_type, tmdb_id, season_number, episode_number = item_id.split('.')
        return {
            "show": {
                "ids": self.sync.id_data
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
    sd_additional_keys = tuple()

    def __init__(self, main):
        self.main = main

    def get_items(self, item):
        return self.meta_item_getter(self.main, item).data

    @cached_property
    def item_queue(self):
        self.main.dialog_progress_bg.max_value = len(self.sd.items) + 20
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
        sd.additional_keys = self.sd_additional_keys
        return sd


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
