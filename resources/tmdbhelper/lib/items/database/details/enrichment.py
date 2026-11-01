from jurialmunkey.ftools import cached_property
from jurialmunkey.window import get_property
from tmdbhelper.lib.addon.consts import KODI_LIBRARY_LAST_UPDATED
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.mcache import ProcessMemoryCache
from tmdbhelper.lib.items.database.details.merge import ItemDetailsMerger


class KodiLibraryCache(ProcessMemoryCache):
    """Kodi library indexes kept in the item detail service between lists.

    The main service records when the Kodi library last changed. The indexes are
    rebuilt after a change instead of waiting for them to expire.
    """

    def __init__(self):
        super().__init__('KodiLibrary')
        self.library_updated = None

    def get_library_updated(self):
        return get_property(KODI_LIBRARY_LAST_UPDATED)

    def refresh(self):
        """Clear the indexes if the library changed since they were built."""
        library_updated = self.get_library_updated()
        with self.lock:
            if library_updated == self.library_updated:
                return
            self.library_updated = library_updated
            self.clear()


class KodiItemData:
    """The list item data that Kodi library matching reads."""

    def __init__(self, item):
        self.unique_ids = item.get('unique_ids') or {}
        self.infolabels = item.get('infolabels') or {}


class KodiDetailsEnrichment:
    """Match a batch of list items to the Kodi library and merge in the library details.

    Items are merged list item data, or None for items that must not be enriched.
    The libraries to load are chosen from the media types in the batch.
    """

    library_types = {'movie': 'movie', 'tvshow': 'tv', 'season': 'tv', 'episode': 'tv'}

    def __init__(self, items, library_cache=None):
        self.items = items
        self.library_cache = library_cache  # A KodiLibraryCache shared between batches

    @cached_property
    def setting(self):
        return get_setting('use_kodi_local_db', 'int')

    @cached_property
    def is_preferred(self):
        return self.setting == 2  # Overwrite TMDb data with Kodi data rather than complement it

    @cached_property
    def library_type(self):
        return self.get_library_type()

    def get_library_type(self):
        types = {
            self.library_types.get(item['infolabels'].get('mediatype'))
            for item in self.items if item and item.get('infolabels')}
        types.discard(None)
        if len(types) > 1:
            return 'both'
        return next(iter(types), None)

    @cached_property
    def kodi_db(self):
        return self.get_kodi_db()

    def get_kodi_db(self):
        if not self.setting or not self.library_type:
            return
        from tmdbhelper.lib.items.kodi import KodiDb
        if self.library_cache is not None:
            self.library_cache.refresh()
        return KodiDb(self.library_type, cache=self.library_cache)

    @cached_property
    def item_data(self):
        return [KodiItemData(item) if item else None for item in self.items]

    @cached_property
    def enriched(self):
        return self.get_enriched()

    def get_enriched(self):
        """The enriched item data, or None where nothing in the library matched."""
        if not self.kodi_db:
            return [None for _ in self.items]
        self.kodi_db.prepare_listitems([data for data in self.item_data if data])
        return [
            self.get_enriched_item(item, data) if item else None
            for item, data in zip(self.items, self.item_data)]

    def get_enriched_item(self, item, data):
        details = self.kodi_db.get_kodi_details(data)
        if not details:
            return
        return {**item, **ItemDetailsMerger(item, details, reverse=self.is_preferred).merged}
