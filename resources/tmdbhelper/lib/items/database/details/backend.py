from jurialmunkey.ftools import cached_property, threaded_cached_property
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.items.database.details.apis import DetailsAPIs
from tmdbhelper.lib.items.database.details.metadata import DetailsMetadataCache
from tmdbhelper.lib.items.database.details.storedmetadata import DetailsStoredMetadata


class DetailsDatabase(ItemDetailsDatabase):
    def __init__(self):
        self._basefolder = get_setting('cache_location', 'str') or ''
        super().__init__()

    def database_execute(self, cursor, query, data=None):
        # The coordinator must roll back and restart on database errors. Treating
        # an unsuccessful statement as a cache miss could commit a partial item.
        if not data:
            return cursor.execute(query)
        if isinstance(data, list):
            return cursor.executemany(query, data)
        return cursor.execute(query, data)

    def get_result(self, scope, query, data, get_result):
        return self.get_session_result(scope, query, data, get_result)


class DetailsLookup:
    """Configure a fresh factory before accessing any cached factory properties."""

    item_factory = staticmethod(BaseItemFactory)

    def __init__(
            self, cache, request, common_apis, parent_data=None,
            sync_enabled=True, metadata_cache=None):
        self.request = request
        self.common_apis = common_apis
        self.factory = self.item_factory(request.mediatype, common_apis=self.common_apis)
        self.factory.cache = cache
        for name in (
                'tmdb_id', 'season', 'episode', 'cache_refresh',
                'cache_translations', 'extendedinfo'):
            setattr(self.factory, name, getattr(request, name))
        if request.tvshow_tmdb_id is not None:
            self.factory.tvshow_tmdb_id = request.tvshow_tmdb_id
        self.factory.sync_details = bool(request.sync_details and sync_enabled)
        self.factory.parent_item_data = parent_data
        self.factory.metadata_cache = metadata_cache

    @property
    def key(self):
        return (
            self.request.identity, self.factory.datalevel,
            self.factory.translation, self.factory.fanart_tv,
            self.request.cache_refresh == 'force', self.request.clear_user_art,
        )

    def get_cached_data(self):
        data = self.factory.get_cached_data()
        if data:
            data['infoproperties'].update({
                'dbtype': self.request.mediatype,
                'tmdb_type': self.factory.tmdb_type,
                'tmdb_id': self.request.tmdb_id,
            })
            data['label'] = data['infolabels']['title']
        return data


class DetailsBackend:
    lookup_class = DetailsLookup

    def __init__(self):
        self.apis = DetailsAPIs()

    @cached_property
    def cache(self):
        return DetailsDatabase()

    @threaded_cached_property
    def stored_metadata(self):
        return DetailsStoredMetadata(self.cache)

    @threaded_cached_property
    def metadata_cache(self):
        return self.get_metadata_cache()

    def get_metadata_cache(self):
        return DetailsMetadataCache(self.cache, self.stored_metadata)

    def prepare_stored_metadata(self):
        """Clear stored metadata from another add-on version or settings before reads start."""
        self.stored_metadata.prepare()

    def flush_stored_metadata(self):
        """Write queued stored metadata; the coordinator calls this while no reads are in flight."""
        if not self.stored_metadata.has_work:
            return
        self.stored_metadata.flush()

    @threaded_cached_property
    def is_sync_enabled(self):
        """Settings changes restart the service, so the setting is read once."""
        from tmdbhelper.lib.sync.prepare import SyncPreparation
        return SyncPreparation.is_enabled()

    def lookup(self, request, parent_data=None):
        return self.lookup_class(
            self.cache, request, self.apis.get(request.language),
            parent_data, sync_enabled=self.is_sync_enabled,
            metadata_cache=self.metadata_cache)

    def read(self, request):
        """Read on the calling thread's session: the coordinator's or a reader's held connection."""
        lookup = self.lookup(request)
        return lookup.get_cached_data()

    def fetch(self, request, parent_data):
        """Look up online on a lookup thread, with one connection for the lookup."""
        lookup = self.lookup_class(
            self.cache, request, self.apis.get(request.language),
            parent_data=parent_data, sync_enabled=self.is_sync_enabled)
        if not lookup.factory.data_cond:
            return []
        with self.cache.session():
            return lookup.factory.try_cached_data(return_queue=True) or []

    def commit(self, request, queue):
        # A basic lookup may have finished after a richer lookup populated the row.
        # Keep the richer records rather than replacing them with the basic response.
        if request.cache_refresh != 'force' and self.read(request) is not None:
            return
        factory = self.lookup(request).factory
        # Queued writes run on the coordinator's held connection, whichever thread queued them.
        with self.cache.transaction():
            if request.clear_user_art:
                self.clear_user_art(request)
            for func, args, kwargs in queue:
                func(*args, **kwargs)
            # Stored copies change with the item, so a crash cannot leave a stale copy.
            self.stored_metadata.delete_saved(factory)
        self.metadata_cache.discard_saved(factory)

    def clear_user_art(self, request):
        lookup = self.lookup(request)
        item_id = lookup.factory.item_id
        self.cache.del_list_values(
            table='user_art', values=(item_id, f'{item_id}.%'),
            conditions='parent_id=? OR parent_id LIKE ?')

    def fallback(self, request):
        lookup = self.lookup(request)
        return lookup.factory.get_lookup_fallback()

    def close(self):
        # Reader threads have stopped and closed their own connections before the backend closes.
        self.close_created(('metadata_cache', 'apis'))

    def close_created(self, names):
        """Close each created resource in order, even when an earlier close fails."""
        if not names:
            return
        try:
            if names[0] in self.__dict__:
                self.__dict__[names[0]].close()
        finally:
            self.close_created(names[1:])
