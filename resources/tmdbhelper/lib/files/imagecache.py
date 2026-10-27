import re
import xbmcvfs
from collections import defaultdict
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.plugin import ADDONDATA, get_setting
from tmdbhelper.lib.files.futils import validate_join


class ImageCacheFolder:
    """One snapshot of a manipulation folder, pruned by modification time."""

    def __init__(self, folder, target_size, progress=None):
        self.folder = folder
        self.target_size = target_size
        self.progress = progress
        self.cancelled = False

    def report_progress(self, stage, current, total, removed=0):
        if self.progress is not None:
            self.cancelled = not self.progress(self.folder, stage, current, total, removed)
        return not self.cancelled

    def get_file_key(self, filename):
        return filename

    def get_file_entry(self, filename):
        path = validate_join(self.folder, filename)
        try:
            stat = xbmcvfs.Stat(path)
            return path, stat.st_size(), stat.st_mtime()
        except OSError as exc:
            kodi_log(f'Image cache stat failed: {path}\n{exc}', 2)

    def get_file_groups(self):
        groups = defaultdict(list)
        if not self.report_progress('scan', 0, 0):
            return groups
        if not xbmcvfs.exists(self.folder):
            return groups
        filenames = sorted(xbmcvfs.listdir(self.folder)[1])
        for index, filename in enumerate(filenames, 1):
            entry = self.get_file_entry(filename)
            if entry is not None:
                groups[self.get_file_key(filename)].append(entry)
            if not self.report_progress('scan', index, len(filenames)):
                break
        return groups

    @cached_property
    def file_groups(self):
        return self.get_file_groups()

    @staticmethod
    def get_group_size(group):
        return sum(entry[1] for entry in group)

    @staticmethod
    def get_group_modified(group):
        # Select the family when its oldest file would have been selected.
        return min(entry[2] for entry in group)

    @staticmethod
    def delete_file(entry):
        path, size, _ = entry
        try:
            if xbmcvfs.delete(path) or not xbmcvfs.exists(path):
                return size
        except OSError as exc:
            kodi_log(f'Image cache deletion failed: {path}\n{exc}', 2)
            return 0
        kodi_log(f'Image cache deletion failed: {path}', 2)
        return 0

    def delete_group(self, group):
        # Finish the entire family even if the target is reached partway through.
        return sum(self.delete_file(entry) for entry in group)

    def prune(self):
        if not self.target_size:
            return 0
        groups = self.file_groups.values()
        if self.cancelled:
            return 0
        total_size = sum(self.get_group_size(group) for group in groups)
        required_size = total_size - self.target_size
        removed = 0
        for group in sorted(groups, key=self.get_group_modified):
            if total_size <= self.target_size:
                break
            if not self.report_progress('prune', removed, required_size, removed):
                return removed
            deleted_size = self.delete_group(group)
            total_size -= deleted_size
            removed += deleted_size
        if total_size > self.target_size:
            kodi_log(f'Image cache remains above target: {self.folder} ({total_size} bytes)', 2)
        self.report_progress('done', 1, 1, removed)
        return removed


class BlurImageCacheFolder(ImageCacheFolder):
    def get_file_key(self, filename):
        match = re.match(r'^(?:temp_)?([0-9a-f]{32})(?:[-.]|$)', filename)
        return match[1] if match else filename


class ImageCacheMaintenance:
    folder_classes = (
        ('blur_v3', BlurImageCacheFolder),
        ('crop_v2', ImageCacheFolder),
        ('desaturate_v2', ImageCacheFolder),
        ('colors_v2', ImageCacheFolder),
    )

    def __init__(self, progress=None):
        self.progress = progress

    def prune(self):
        target_size = get_setting('image_cache_size', 'int') * 1024 * 1024
        if not target_size:
            return 0
        location = get_setting('image_location', 'str') or ADDONDATA
        removed = 0
        for folder, folder_class in self.folder_classes:
            cache_folder = folder_class(validate_join(location, f'{folder}/'), target_size, self.progress)
            removed += cache_folder.prune()
            if cache_folder.cancelled:
                break
        return removed
