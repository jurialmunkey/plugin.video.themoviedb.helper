from tmdbhelper.lib.addon.settings import AddonSettingsDialog


class SyncProviderSettings(AddonSettingsDialog):
    """Return to the provider control after Kodi saves and closes settings."""

    def __init__(self, label):
        super().__init__(32403, label)

    def select(self, selection):
        try:
            return selection.select()
        finally:
            self.reopen()
