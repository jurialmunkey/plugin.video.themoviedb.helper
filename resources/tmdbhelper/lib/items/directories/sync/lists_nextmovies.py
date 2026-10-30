from datetime import datetime, timezone
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_datetime_today
from tmdbhelper.lib.collections.kodi import get_collection_index
from tmdbhelper.lib.items.directories.sync.lists_standard import ListStandardSync, ListProviderSyncProperties
from tmdbhelper.lib.items.directories.sync.mapper_nextmovies import NextMovieItemMapper
from tmdbhelper.lib.items.directories.sync.nextmovies import MovieCollectionProgress
from tmdbhelper.lib.sync.datasync import SyncDataFactory
from tmdbhelper.lib.sync.collectiondrops import get_collection_drop_store


class ListNextMoviesProperties(ListProviderSyncProperties):
    item_mapper_class = NextMovieItemMapper

    @cached_property
    def syncdata(self):
        return self.get_syncdata()

    @staticmethod
    def get_syncdata():
        return SyncDataFactory()

    @cached_property
    def watched(self):
        return self.get_watched()

    def get_watched(self):
        getter = self.syncdata.get_all_watched_getter('movie')
        return {
            try_int(item['tmdb_id']): self.get_watched_item(item)
            for item in getter.items if item['tmdb_id']
        }

    @classmethod
    def get_watched_item(cls, item):
        watched = convert_timestamp(item['last_watched_at']).replace(tzinfo=timezone.utc).astimezone()
        return dict(
            item, watched_datetime=watched, watched_date=watched.date(),
            watched_timestamp=cls.get_utc_timestamp(item['last_watched_at']))

    @staticmethod
    def get_utc_timestamp(value):
        timestamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc)

    @cached_property
    def collection_movies(self):
        return self.get_collection_movies()

    def get_collection_movies(self):
        return get_collection_index().get_collection_movies(self.watched)

    @cached_property
    def drop_store(self):
        return self.get_drop_store()

    @staticmethod
    def get_drop_store():
        return get_collection_drop_store()

    @cached_property
    def collection_activity(self):
        return self.get_collection_activity()

    def get_collection_activity(self):
        return {
            collection_id: self.get_latest_watch(members)
            for collection_id, members in self.collection_movies.items()
        }

    def get_latest_watch(self, members):
        return max(
            self.watched[member['movie_id']]['watched_timestamp']
            for member in members if member['movie_id'] in self.watched)

    @cached_property
    def dropped_collections(self):
        return self.get_dropped_collections()

    def get_dropped_collections(self):
        drops = self.drop_store.get_drops()
        revived = self.get_revived_collections(drops)
        if not revived:
            return set(drops)
        self.drop_store.remove(revived)
        return set(self.drop_store.get_drops())

    def get_revived_collections(self, drops):
        return {
            collection_id: dropped_at for collection_id, dropped_at in drops.items()
            if collection_id in self.collection_activity
            and self.collection_activity[collection_id] > self.get_utc_timestamp(dropped_at)
        }

    @cached_property
    def progress_items(self):
        return self.get_progress_items()

    def get_progress_items(self):
        today = get_datetime_today().date()
        dropped = self.dropped_collections
        items = (
            MovieCollectionProgress(collection_id, members, self.watched, today).item
            for collection_id, members in self.collection_movies.items()
            if collection_id not in dropped
        )
        return [item for item in items if item is not None]

    def get_sync_data(self):
        if not self.provider_available:
            return []
        ordered = sorted(
            self.progress_items, key=lambda item: (item['activity'], item['collection_id']), reverse=True)
        return self.get_unique_items(ordered)

    @staticmethod
    def get_unique_items(items):
        entries = {}
        for item in items:
            entries.setdefault(item['tmdb_id'], item)
        return list(entries.values())

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        if not self.response:
            return []
        return [self.get_mapped_item(item) for item in self.response.paginated_items.items]

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item


class ListNextMovies(ListStandardSync):
    list_properties_class = ListNextMoviesProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32602
        list_properties.plugin_name = '{localized}'
        list_properties.item_type = 'movie'
        list_properties.container_content = 'movies'
        return list_properties

    def get_items(self, tmdb_type='movie', **kwargs):
        return super().get_items(tmdb_type='movie', **kwargs)
