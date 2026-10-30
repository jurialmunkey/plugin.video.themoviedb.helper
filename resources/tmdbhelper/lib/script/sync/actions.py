from tmdbhelper.lib.script.sync.provider import ItemSync


class ItemWatched(ItemSync):
    sync_types = ('SyncWatched', 'SyncPlayback')
    show_sync_types = ('SyncNextEpisodes', 'SyncAllNextEpisodes')
    allow_seasons = True
    allow_episodes = True
    preconfigured = True
    localized_name = 16103
    remove = False


class ItemUnwatched(ItemWatched):
    localized_name = 16104
    remove = True


class ItemWatchlist(ItemSync):
    sync_types = ('SyncWatchlist',)
    localized_name_add = 32291
    localized_name_rem = 32292
    sync_key = 'watchlist_listed_at'


class ItemCollection(ItemSync):
    sync_types = ('SyncCollection',)
    localized_name_add = 32289
    localized_name_rem = 32290
    allow_episodes = True
    sync_key = 'collection_last_collected_at'


class ItemDropped(ItemSync):
    sync_types = ('SyncHiddenDropped',)
    show_sync_types = ('SyncNextEpisodes', 'SyncAllNextEpisodes')
    allow_movies = False
    allow_shows = True
    allow_seasons = True
    allow_episodes = True
    localized_name_add = 32046
    localized_name_rem = 32047
    convert_episodes = True
    convert_seasons = True
    sync_key = 'dropped_hidden_at'
