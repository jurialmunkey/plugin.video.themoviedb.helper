import xbmc


class UpdateMonitor(xbmc.Monitor):
    """
    Monitors updating Kodi library
    """

    @staticmethod
    def run_library_tagger():
        from tmdbhelper.lib.addon.thread import SafeThread
        from tmdbhelper.lib.update.builder.tags import library_tagger
        SafeThread(target=library_tagger).start()

    def onScanFinished(self, library):
        if library == 'video':
            self.run_library_tagger()
