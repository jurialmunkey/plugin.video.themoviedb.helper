from datetime import timezone
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_datetime_today
from tmdbhelper.lib.collections.kodi import get_collection_index
from tmdbhelper.lib.items.directories.sync.lists_standard import ListStandardSync, ListProviderSyncProperties
from tmdbhelper.lib.items.directories.sync.mapper_nextmovies import NextMovieItemMapper
from tmdbhelper.lib.items.directories.sync.nextmovies import MovieCollectionProgress
from tmdbhelper.lib.sync.datasync import SyncDataFactory


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

    @staticmethod
    def get_watched_item(item):
        watched = convert_timestamp(item['last_watched_at']).replace(tzinfo=timezone.utc).astimezone()
        return dict(item, watched_datetime=watched, watched_date=watched.date())

    @cached_property
    def collection_movies(self):
        return self.get_collection_movies()

    def get_collection_movies(self):
        return get_collection_index().get_collection_movies(self.watched)

    @cached_property
    def progress_items(self):
        return self.get_progress_items()

    def get_progress_items(self):
        today = get_datetime_today().date()
        items = (
            MovieCollectionProgress(collection_id, members, self.watched, today).item
            for collection_id, members in self.collection_movies.items()
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
