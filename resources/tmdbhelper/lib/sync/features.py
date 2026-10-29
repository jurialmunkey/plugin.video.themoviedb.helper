from tmdbhelper.lib.sync.providers.features import FEATURE_LABELS as PROVIDER_FEATURE_LABELS
from tmdbhelper.lib.sync.providers.features import SYNC_FEATURES as PROVIDER_SYNC_FEATURES
from tmdbhelper.lib.sync.providers.services import SERVICE_FEATURE_LABELS, SERVICE_SYNC_FEATURES


FEATURE_LABELS = {**PROVIDER_FEATURE_LABELS, **SERVICE_FEATURE_LABELS}
SYNC_FEATURES = {**PROVIDER_SYNC_FEATURES, **SERVICE_SYNC_FEATURES}
