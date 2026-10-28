from xbmcgui import Dialog, DialogProgress
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized, get_setting
from tmdbhelper.lib.addon.settings import AddonSettingsDialog
from tmdbhelper.lib.files.futils import normalise_filesize
from tmdbhelper.lib.files.imagecache import ImageCacheMaintenance


class ImageCacheCleanup:
    """Foreground presentation of the same cleanup used by the service."""

    def __init__(self):
        self.folder = None
        self.folder_index = -1
        self.folder_removed = 0
        self.previous_removed = 0
        self.cancelled = False
        self.last_update = None

    @cached_property
    def title(self):
        return get_localized(32567)

    @cached_property
    def progress_dialog(self):
        return DialogProgress()

    def set_folder(self, folder):
        if folder == self.folder:
            return
        self.previous_removed += self.folder_removed
        self.folder_removed = 0
        self.folder = folder
        self.folder_index += 1

    def get_progress(self, stage, current, total):
        fraction = min(current / total, 1) if total else 0
        fraction = fraction / 2 if stage == 'scan' else (1 + fraction) / 2
        return int(100 * (self.folder_index + fraction) / len(ImageCacheMaintenance.folder_classes))

    def get_message(self, stage, current, total):
        folder = self.folder.replace('\\', '/').rstrip('/').rsplit('/', 1)[-1]
        status = get_localized(32568).format(folder, current, total) if stage == 'scan' else get_localized(32569).format(folder)
        reclaimed = get_localized(32570).format(normalise_filesize(self.previous_removed + self.folder_removed))
        return f'{status}\n{reclaimed}'

    def update_progress(self, folder, stage, current, total, removed):
        if self.progress_dialog.iscanceled():
            self.cancelled = True
            return False
        self.set_folder(folder)
        self.folder_removed = removed
        progress = self.get_progress(stage, current, total)
        # Avoid repainting for every file in a large directory.
        update_key = (folder, stage, progress)
        if update_key != self.last_update:
            self.progress_dialog.update(progress, self.get_message(stage, current, total))
            self.last_update = update_key
        return True

    def run(self):
        if not get_setting('image_cache_size', 'int'):
            Dialog().ok(self.title, get_localized(32573))
            return
        self.progress_dialog.create(self.title)
        try:
            removed = ImageCacheMaintenance(progress=self.update_progress).prune()
        finally:
            self.progress_dialog.close()
        message = get_localized(32572 if self.cancelled else 32571)
        Dialog().ok(self.title, message.format(normalise_filesize(removed)))


class ImageCacheSettings(AddonSettingsDialog):
    """Return to the cleanup button after Kodi saves and closes settings."""

    def __init__(self):
        super().__init__(10039, 32567)


def clean_image_cache(**kwargs):
    try:
        ImageCacheCleanup().run()
    finally:
        ImageCacheSettings().reopen()
