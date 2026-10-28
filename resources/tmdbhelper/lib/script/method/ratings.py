from tmdbhelper.lib.addon.settings import AddonSettingsDialog
from tmdbhelper.lib.script.ratings.providers import RatingsProviderSelection


def configure_ratings_providers(return_settings=False, **kwargs):
    selection = RatingsProviderSelection()
    if not return_settings:
        return selection.select()
    try:
        return selection.select()
    finally:
        AddonSettingsDialog(32080, 32581).reopen()
