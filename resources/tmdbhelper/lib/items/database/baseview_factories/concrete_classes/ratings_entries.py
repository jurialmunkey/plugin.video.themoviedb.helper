from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.items.database.basedata import ItemDetailsDatabaseAccess
from tmdbhelper.lib.query.database.database import FindQueriesDatabase


class RatingsStoredData(ItemDetailsDatabaseAccess):
    """ Saved ratings and provider expiries for one or more items, one query per table """

    value_keys = ('id', 'provider', 'key', 'value')
    expiry_keys = ('id', 'provider', 'expiry')

    def __init__(self, item_ids, common_apis=None):
        super().__init__(common_apis)
        self.item_ids = tuple(item_ids)

    @property
    def conditions(self):
        return f'id IN ({", ".join("?" for _ in self.item_ids)})'

    def get_rows(self, table, keys):
        with self.connection.open():
            return self.get_cached_list_values(table, keys, self.item_ids, self.conditions) or ()

    @cached_property
    def stored_values(self):
        return self.get_stored_values()

    def get_stored_values(self):
        """ Saved values by (item ID, provider) """
        stored_values = {}
        for row in self.get_rows('ratings', self.value_keys):
            stored_values.setdefault((row['id'], row['provider']), {})[row['key']] = row['value']
        return stored_values

    @cached_property
    def expiries(self):
        return self.get_expiries()

    def get_expiries(self):
        """ Provider expiries by (item ID, provider) """
        return {
            (row['id'], row['provider']): row['expiry']
            for row in self.get_rows('ratings_provider', self.expiry_keys)
        }


class RatingsTop250Rank:
    """ The item's IMDb Top 250 rank, read from the cached list rather than saved per item """

    def __init__(self, tmdb_type, tmdb_id):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id

    @cached_property
    def values(self):
        return self.get_values()

    def get_values(self):
        top250 = FindQueriesDatabase().get_imdb_top250_list_cached(self.tmdb_type)
        if not top250:  # No provider supplies a Top 250 list
            return {}
        try:
            return {'top250': top250.index(try_int(self.tmdb_id)) + 1}  # Must be an int to match
        except ValueError:
            return {}


class RatingsProviderEntry:
    """ One provider's ratings for one item.

    Saved values are used until the provider's expiry. After it, saved values are used
    while they refresh, when the level allows it, until the stale grace has also passed.
    Otherwise the provider is asked online. An empty online result is not saved, so it is
    asked again next time, and falls back to saved values that are still within the grace.
    """

    def __init__(self, level, provider_id, supplier):
        self.level = level  # RatingsDict, which configures the item and lookup rules
        self.provider_id = provider_id
        self.supplier = supplier
        self.is_fetched = False  # Set once its online values are retrieved

    @cached_property
    def key(self):
        return (self.level.item_id, self.provider_id)

    @cached_property
    def stored_values(self):
        return self.level.stored_data.stored_values.get(self.key, {})

    @cached_property
    def stored_expiry(self):
        return self.level.stored_data.expiries.get(self.key)

    @cached_property
    def online_expiry(self):
        return self.level.expiry

    @cached_property
    def state(self):
        return self.get_state()

    def get_state(self):
        if self.stored_expiry is None:
            return 'missing'
        if self.stored_expiry >= self.level.current_time:
            return 'fresh'
        if self.stored_expiry + self.level.stale_grace >= self.level.current_time:
            return 'stale'
        return 'missing'

    @property
    def is_online_needed(self):
        return self.state == 'missing' or (self.state == 'stale' and not self.level.allow_stale)

    @property
    def is_resolved(self):
        """ Whether the values are known, so that they can be merged without waiting online """
        return self.is_fetched or not self.is_online_needed

    def fetch(self):
        """ Retrieve the online values, then mark the provider as finished """
        self.online_values
        self.is_fetched = True

    @cached_property
    def online_values(self):
        return self.get_online_values()

    def get_online_values(self):
        return {
            key: value
            for key, value in self.supplier.ratings.items()
            if value not in (None, '')
        }

    @cached_property
    def source(self):
        return self.get_source()

    def get_source(self):
        """ Where the values come from: 'fresh', 'stale', 'online', or None for no values """
        if self.state == 'fresh':
            return 'fresh'
        if not self.is_online_needed:
            return 'stale'
        if self.online_values:
            return 'online'
        if self.state == 'stale':
            return 'stale'

    @property
    def is_current(self):
        return self.source in ('fresh', 'online')

    @property
    def is_stale(self):
        return self.source == 'stale'

    @property
    def is_unsaved(self):
        return self.source == 'online'

    @property
    def values(self):
        if self.source == 'online':
            return self.online_values
        if self.source is None:
            return {}
        return self.stored_values

    @property
    def expiry(self):
        if self.source == 'online':
            return self.online_expiry
        if self.source is None:
            return
        return self.stored_expiry

    @property
    def saved_rows(self):
        return [
            (self.level.item_id, self.provider_id, key, value)
            for key, value in self.online_values.items()
        ]

    @property
    def saved_expiry_row(self):
        return (self.level.item_id, self.provider_id, self.online_expiry)
