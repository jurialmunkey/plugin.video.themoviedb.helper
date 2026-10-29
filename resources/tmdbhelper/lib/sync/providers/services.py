from tmdbhelper.lib.sync.datatype import DataType


SERVICE_FEATURE_LABELS = {'ratings': 563, 'favorites': 1036}
SERVICE_SYNC_FEATURES = {'SyncRatings': 'ratings', 'SyncFavorites': 'favorites'}


class ServiceDataType(DataType):
    """Account data supplied independently of selected sync providers."""

    @classmethod
    def invalidate_cache(cls, provider):
        pass
