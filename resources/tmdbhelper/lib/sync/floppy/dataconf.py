from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.tmdate import is_unaired_timestamp

"""
Convert Floppy tracked media entries into flat sync records
Record keys match the attribute names read by FloppySyncItemData

EXAMPLE INPUT (GET /api/v1/media/episode/)
{
    "consumption_id": 1121,
    "item": {
        "media_id": "78191",
        "source": "tmdb",
        "media_type": "episode",
        "title": "You Got Me, Babe",
        "season_number": 1,
        "episode_number": 8,
        "release_datetime": "2018-10-29T02:00:00Z",
        ...
    },
    "status": 3,
    "created_at": "2026-10-19T23:53:08.835596Z",
    "end_date": "2026-10-19T23:53:08.824733Z",
    "next_episode": null,
    "total_episodes_left": null,
    ...
}

EXAMPLE OUTPUT (FloppyWatchedShows)
{
    "type": "show",
    "tmdb_id": 78191,
    "title": "You",
    "year": 2018,
    "premiered": "2018-09-09",
    "status": "Ended",
    "country": "United States of America",
    "runtime": None,
    "episodes_left": 0,
    "plays": 48,
    "last_watched_at": "2026-10-19T23:53:08.824733Z",
    "seasons": [
        {
            "number": 1,
            "episodes": [
                {"number": 8, "plays": 1, "last_watched_at": "2026-10-19T23:53:08.824733Z"},
            ]
        }
    ]
}
"""


FLOPPY_STATUS_PLANNING = 0
FLOPPY_STATUS_IN_PROGRESS = 1
FLOPPY_STATUS_PAUSED = 2
FLOPPY_STATUS_COMPLETED = 3
FLOPPY_STATUS_DROPPED = 4


class FloppyEntry:
    """ A single Floppy tracked media entry (one consumption) """

    def __init__(self, entry):
        self.entry = entry

    @cached_property
    def item(self):
        return self.entry['item']

    @cached_property
    def is_tmdb(self):
        return self.item['source'] == 'tmdb'

    @cached_property
    def tmdb_id(self):
        return try_int(self.item['media_id'])

    @cached_property
    def season_number(self):
        return self.item['season_number']

    @cached_property
    def episode_number(self):
        return self.item['episode_number']

    @cached_property
    def tracking_status(self):
        return self.entry['status']

    @cached_property
    def release_datetime(self):
        return self.item.get('release_datetime') or ''

    @cached_property
    def watched_at(self):
        return self.entry['end_date'] or self.entry['progressed_at'] or self.entry['created_at']

    @cached_property
    def updated_at(self):
        return self.entry['progressed_at'] or self.entry['created_at']

    @cached_property
    def meta(self):
        return {
            'tmdb_id': self.tmdb_id,
            'title': self.item.get('title'),
            'year': try_int(self.release_datetime[:4]) or None,
            'premiered': self.release_datetime[:10] or None,
            'status': self.item.get('status') or None,
            'country': self.item.get('country') or None,
            'runtime': self.item.get('runtime_minutes'),
        }

    @cached_property
    def next_episode(self):
        return self.entry['next_episode']

    @cached_property
    def next_episode_aired_at(self):
        return f'{self.next_episode["air_date"][:19]}.000Z'

    @cached_property
    def next_episode_id(self):
        return f'tv.{self.tmdb_id}.{self.next_episode["season_number"]}.{self.next_episode["episode_number"]}'

    @cached_property
    def is_aired_next_episode(self):
        try:
            return not is_unaired_timestamp(self.next_episode['air_date'])
        except TypeError:  # No next episode
            return False


class FloppyRecordList:
    """ Base list converting Floppy entries into one sync record per entry """

    record_type = None
    tracking_statuses = None

    def __init__(self, entries, item_type):
        self.entries = entries
        self.item_type = item_type

    @cached_property
    def floppy_entries(self):
        return self.get_floppy_entries()

    def get_floppy_entries(self):
        return [
            i for i in (FloppyEntry(entry) for entry in self.entries)
            if i.is_tmdb and self.is_included(i)
        ]

    def is_included(self, floppy_entry):
        if self.tracking_statuses is None:
            return True
        return floppy_entry.tracking_status in self.tracking_statuses

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        return [self.get_record(i) for i in self.floppy_entries]

    def get_record_base(self, floppy_entry):
        return {
            **floppy_entry.meta,
            'type': self.record_type or self.item_type,
            'season_number': floppy_entry.season_number,
            'episode_number': floppy_entry.episode_number,
        }

    def get_record(self, floppy_entry):
        return self.get_record_base(floppy_entry)


class FloppyWatchlist(FloppyRecordList):
    tracking_statuses = (FLOPPY_STATUS_PLANNING, )

    def get_record(self, floppy_entry):
        return {
            **self.get_record_base(floppy_entry),
            'listed_at': floppy_entry.entry['created_at'],
            'notes': floppy_entry.entry['notes'] or None,
        }


class FloppyDropped(FloppyRecordList):
    tracking_statuses = (FLOPPY_STATUS_DROPPED, )

    def get_record(self, floppy_entry):
        return {
            **self.get_record_base(floppy_entry),
            'hidden_at': floppy_entry.updated_at,
        }


class FloppyNextEpisodes(FloppyRecordList):
    record_type = 'show'
    tracking_statuses = (FLOPPY_STATUS_IN_PROGRESS, FLOPPY_STATUS_PAUSED, FLOPPY_STATUS_COMPLETED, )

    def is_included(self, floppy_entry):
        return super().is_included(floppy_entry) and floppy_entry.is_aired_next_episode

    def get_record(self, floppy_entry):
        return {
            **self.get_record_base(floppy_entry),
            'next_episode_id': floppy_entry.next_episode_id,
            'next_episode_aired_at': floppy_entry.next_episode_aired_at,
        }


class FloppyWatchedMovies(FloppyRecordList):
    """ Floppy stores one completed entry per play so plays are counted by grouping on tmdb_id """

    record_type = 'movie'
    tracking_statuses = (FLOPPY_STATUS_COMPLETED, )

    @cached_property
    def grouped_entries(self):
        return self.get_grouped_entries()

    def get_grouped_entries(self):
        grouped_entries = {}
        for i in self.floppy_entries:
            grouped_entries.setdefault(i.tmdb_id, []).append(i)
        return grouped_entries

    def get_data(self):
        return [self.get_grouped_record(entries) for entries in self.grouped_entries.values()]

    def get_grouped_record(self, entries):
        return {
            **self.get_record_base(entries[0]),
            'plays': len(entries),
            'last_watched_at': max(i.watched_at for i in entries),
        }


class FloppyWatchedShows:
    """ Nest watched episode entries under their show in the Trakt sync/watched layout used by SyncItemConstructor """

    def __init__(self, show_entries, episode_entries):
        self.show_entries = show_entries
        self.episode_entries = episode_entries

    @cached_property
    def shows(self):
        return self.get_shows()

    def get_shows(self):
        """ Latest tracked show entry for each tmdb_id """
        entries = sorted(
            (i for i in (FloppyEntry(entry) for entry in self.show_entries) if i.is_tmdb),
            key=lambda i: i.updated_at)
        return {i.tmdb_id: i for i in entries}

    @cached_property
    def episodes(self):
        return self.get_episodes()

    def get_episodes(self):
        """ Watched episode entries grouped by tmdb_id, season and episode """
        episodes = {}
        for i in (FloppyEntry(entry) for entry in self.episode_entries):
            if not i.is_tmdb or i.tracking_status != FLOPPY_STATUS_COMPLETED:
                continue
            episodes.setdefault(i.tmdb_id, {}).setdefault(i.season_number, {}).setdefault(i.episode_number, []).append(i)
        return episodes

    @cached_property
    def data(self):
        return [self.get_show_record(tmdb_id, seasons) for tmdb_id, seasons in self.episodes.items()]

    @staticmethod
    def get_episode_record(number, entries):
        return {
            'number': number,
            'plays': len(entries),
            'last_watched_at': max(i.watched_at for i in entries),
        }

    def get_season_record(self, number, episodes):
        return {
            'number': number,
            'episodes': [self.get_episode_record(k, v) for k, v in episodes.items()],
        }

    def get_show_meta(self, tmdb_id):
        try:
            show = self.shows[tmdb_id]
        except KeyError:  # Episodes watched without a tracked show entry
            return {'tmdb_id': tmdb_id}
        return {**show.meta, 'episodes_left': show.entry['total_episodes_left']}

    def get_show_record(self, tmdb_id, seasons):
        season_records = [self.get_season_record(k, v) for k, v in seasons.items()]
        episode_records = [j for i in season_records for j in i['episodes']]
        return {
            **self.get_show_meta(tmdb_id),
            'type': 'show',
            'plays': sum(i['plays'] for i in episode_records),
            'last_watched_at': max(i['last_watched_at'] for i in episode_records),
            'seasons': season_records,
        }


class FloppyPlaybackEntry:
    """ A single Floppy resume position (GET /api/v1/playback/progress/) """

    def __init__(self, entry):
        self.entry = entry

    @cached_property
    def is_tmdb(self):
        return self.entry['source'] == 'tmdb'

    @cached_property
    def is_resumable(self):
        return bool(self.entry['position_seconds'] and self.entry['duration_seconds'])

    @cached_property
    def progress(self):
        return (self.entry['position_seconds'] / self.entry['duration_seconds']) * 100

    @cached_property
    def record(self):
        return {
            'type': self.entry['media_type'],
            'tmdb_id': try_int(self.entry['media_id']),
            'season_number': self.entry['season_number'],
            'episode_number': self.entry['episode_number'],
            'title': self.entry['series_title'] or self.entry['title'],
            'progress': self.progress,
            'paused_at': self.entry['updated_at'],
            'id': self.entry['position_seconds'],  # Floppy has no playback id so the resume position marks an active entry
        }


class FloppyPlayback:

    def __init__(self, entries, item_type):
        self.entries = entries
        self.item_type = item_type

    @cached_property
    def data(self):
        return [
            i.record for i in (FloppyPlaybackEntry(entry) for entry in self.entries)
            if i.is_tmdb and i.is_resumable
        ]
