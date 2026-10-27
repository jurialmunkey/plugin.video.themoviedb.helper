from tmdbhelper.lib.sync.trakt.datatype import TraktDataType


class SyncRatings(TraktDataType):
    keys = ('rating', 'rated_at')
    last_activities_key = 'rated_at'
    method = 'ratings'


class SyncFavorites(TraktDataType):
    keys = ('rank', 'listed_at', 'notes')
    last_activities_key = 'favorited_at'
    sync_kwgs = {'extended': 'full'}
    method = 'favorites'
    key_prefix = 'favorites'
