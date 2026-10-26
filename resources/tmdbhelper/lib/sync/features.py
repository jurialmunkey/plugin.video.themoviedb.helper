from tmdbhelper.lib.sync.providers.features import FEATURE_LABELS as PROVIDER_FEATURE_LABELS
from tmdbhelper.lib.sync.providers.features import SYNC_FEATURES as PROVIDER_SYNC_FEATURES
from tmdbhelper.lib.sync.trakt.features import FEATURE_LABELS as TRAKT_FEATURE_LABELS
from tmdbhelper.lib.sync.trakt.features import SYNC_FEATURES as TRAKT_SYNC_FEATURES


FEATURE_LABELS = {**PROVIDER_FEATURE_LABELS, **TRAKT_FEATURE_LABELS}
SYNC_FEATURES = {**PROVIDER_SYNC_FEATURES, **TRAKT_SYNC_FEATURES}
