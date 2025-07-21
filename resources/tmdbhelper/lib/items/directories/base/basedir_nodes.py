from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDONPATH, PLUGINPATH
from tmdbhelper.lib.addon.consts import NODE_BASEDIR
from tmdbhelper.lib.files.futils import get_files_in_folder, read_file


class BaseDirNodeItem:
    def __init__(self, filename, basedir):
        self.filename = filename
        self.basedir = basedir

    @cached_property
    def label(self):
        return self.meta.get('name') or ''

    @cached_property
    def data(self):
        return read_file(self.basedir + self.filename)

    @cached_property
    def meta(self):
        from json import loads
        return (loads(self.data) or {}) if self.data else {}

    @cached_property
    def art(self):
        return {
            'landscape': f'{ADDONPATH}/fanart.jpg',
            'icon': self.meta.get('icon') or ''
        }

    @cached_property
    def params(self):
        return {
            'info': 'dir_custom_node',
            'filename': self.filename,
            'basedir': self.basedir,
        }

    @cached_property
    def items(self):
        try:
            return self.meta['list']
        except (KeyError, TypeError):
            return []

    @cached_property
    def item(self):
        return {
            'label': self.label,
            'params': self.params,
            'path': PLUGINPATH,
            'art': self.art,
        } if self.meta else {}


class BaseDirNodeCustomItem:
    def __init__(self, name=None, path=None, icon=None, **kwargs):
        self.name = name or ''
        self.path = path or PLUGINPATH
        self.icon = icon or ''

    @cached_property
    def art(self):
        return {
            'landscape': f'{ADDONPATH}/fanart.jpg',
            'icon': self.icon
        }

    @cached_property
    def item(self):
        return {
            'label': self.name,
            'path': self.path,
            'art': self.art,
        }


class BaseDirNode:
    def __init__(self, filename=None, basedir=None, **kwargs):
        self.filename = filename
        self.basedir = basedir or NODE_BASEDIR

    @cached_property
    def files(self):
        return get_files_in_folder(self.basedir, r'.*\.json')

    @cached_property
    def basedir_topdir(self):
        return [
            i.item for i in (
                BaseDirNodeItem(filename, self.basedir)
                for filename in self.files
            ) if i and i.item
        ] if not self.filename else []

    @cached_property
    def basedir_subdir(self):
        return [
            i.item for i in (
                BaseDirNodeCustomItem(**item)
                for item in BaseDirNodeItem(
                    self.filename,
                    self.basedir
                ).items
            ) if i and i.item
        ] if self.filename in self.files else []

    def build_basedir(self):
        return self.basedir_subdir or self.basedir_topdir
