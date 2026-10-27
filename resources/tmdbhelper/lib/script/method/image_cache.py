from xbmc import Monitor
from xbmcgui import Dialog, DialogProgress, Window
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDON, executebuiltin, get_condvisibility, get_infolabel, get_localized, get_setting
from tmdbhelper.lib.addon.logger import kodi_log
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


class ImageCacheSettings:
    """Return to the cleanup button after Kodi saves and closes settings."""

    @cached_property
    def window(self):
        return Window(10140)

    def focus_label(self, label, first_control):
        # Read labels without wrapping native spin/slider controls in Python.
        for control_id in range(first_control, first_control + 100):
            if get_infolabel(f'Control.GetLabel({control_id})') == label:
                self.window.setFocusId(control_id)
                return True
        return False

    def reopen(self):
        addon_id = ADDON.getAddonInfo('id')
        executebuiltin(f'Addon.OpenSettings({addon_id})')
        monitor = Monitor()
        category_focused = False
        for _ in range(100):
            if get_condvisibility('Window.IsActive(addonsettings)') and self.window.getProperty('Addon.ID') == addon_id:
                # Kodi allocates category controls from 100 and setting controls from 200.
                if not category_focused:
                    category_focused = self.focus_label(get_localized(10039), 100)
                elif self.focus_label(get_localized(32567), 200):
                    return
            if monitor.waitForAbort(0.05):
                return
        kodi_log('Image cache cleanup: timed out restoring the settings position', 2)


def clean_image_cache(**kwargs):
    try:
        ImageCacheCleanup().run()
    finally:
        ImageCacheSettings().reopen()
