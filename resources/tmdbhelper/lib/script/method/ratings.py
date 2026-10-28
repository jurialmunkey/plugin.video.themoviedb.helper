from tmdbhelper.lib.addon.settings import AddonSettingsDialog
from tmdbhelper.lib.script.ratings.providers import RatingsProviderSelection, RatingsProviderOrderSelection


def configure_ratings_providers(return_settings=False, **kwargs):
    return configure_ratings_selection(RatingsProviderSelection(), return_settings)


def configure_ratings_provider_order(return_settings=False, **kwargs):
    return configure_ratings_selection(RatingsProviderOrderSelection(), return_settings)


def configure_ratings_selection(selection, return_settings):
    if not return_settings:
        return selection.select()
    try:
        return selection.select()
    finally:
        AddonSettingsDialog(32403, selection.setting_label).reopen()
