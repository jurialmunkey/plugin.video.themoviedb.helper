"""Infer forward-only collection progress from the current synced watch dates."""
from jurialmunkey.ftools import cached_property


class MovieCollectionProgress:
    def __init__(self, collection_id, members, watched, today):
        self.collection_id = collection_id
        self.members = members
        self.watched = watched
        self.today = today

    @cached_property
    def released(self):
        return self.get_released()

    def get_released(self):
        return sorted(
            (item for item in self.members if item['release_date'] and item['release_date'] <= self.today.isoformat()),
            key=lambda item: (item['release_date'], item['movie_id']))

    @cached_property
    def released_watches(self):
        return self.get_released_watches()

    def get_released_watches(self):
        return tuple(self.watched.get(member['movie_id']) for member in self.released)

    @cached_property
    def reset_item(self):
        return self.get_reset_item()

    def get_reset_item(self):
        return max(self.get_reset_candidates(), key=lambda item: item['watched_date'], default=None)

    def get_reset_candidates(self):
        latest = None
        for watched in reversed(self.released_watches):
            if watched is None:
                break  # No earlier position can have a fully watched suffix.
            if latest is not None and watched['watched_date'] > latest:
                yield watched
            latest = max(latest, watched['watched_date']) if latest is not None else watched['watched_date']

    @cached_property
    def position(self):
        return self.get_position()

    def get_position(self):
        return max(
            (index for index, watched in enumerate(self.released_watches) if self.is_current_run_watch(watched)),
            default=-1)

    def is_current_run_watch(self, watched):
        if watched is None:
            return False
        if self.reset_item is None:
            return True
        return watched['watched_date'] >= self.reset_item['watched_date']

    @cached_property
    def next_member(self):
        return self.get_next_member()

    def get_next_member(self):
        if self.position < 0 or self.position + 1 >= len(self.released):
            return None
        return self.released[self.position + 1]

    @cached_property
    def activity(self):
        return self.get_activity()

    def get_activity(self):
        return max(
            (watched for watched in self.released_watches if watched is not None),
            key=lambda item: item['watched_datetime'])

    @cached_property
    def item(self):
        return self.get_item()

    def get_item(self):
        if self.next_member is None:
            return
        return {
            'tmdb_id': self.next_member['movie_id'], 'premiered': self.next_member['release_date'],
            'collection_id': self.collection_id, 'collection_position': self.position + 2,
            'collection_total': len(self.released),
            'collection_reset_at': self.reset_item['last_watched_at'] if self.reset_item else None,
            'last_watched_at': self.activity['last_watched_at'], 'activity': self.activity['watched_datetime'],
        }
