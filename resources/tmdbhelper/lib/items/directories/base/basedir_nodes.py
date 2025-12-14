from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import parse_paramstring
from tmdbhelper.lib.addon.plugin import ADDONPATH, PLUGINPATH, get_localized
from tmdbhelper.lib.addon.consts import NODE_BASEDIR
from tmdbhelper.lib.files.futils import get_files_in_folder, read_file
from urllib.parse import urlencode


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
    def __init__(self, name=None, path=None, icon=None, file=None, **kwargs):
        self.name = name or ''
        self.path = path or PLUGINPATH
        self.icon = icon or ''
        self.file = file or ''

    @cached_property
    def context_menu(self):
        if not self.file:
            return []
        return [
            (
                get_localized(32152),
                f'RunScript(plugin.video.themoviedb.helper,remove_node,file={self.file},name={self.name})'
            )
        ]

    @cached_property
    def art(self):
        return {
            'landscape': f'{ADDONPATH}/fanart.jpg',
            'icon': self.icon
        }

    @cached_property
    def paramstring(self):
        try:
            return self.path.split('?')[1]
        except (IndexError, TypeError, AttributeError):
            return ''

    @cached_property
    def paramstring_params(self):
        return parse_paramstring(self.paramstring)

    @cached_property
    def paramstring_noinfo(self):
        paramstring_noinfo = self.paramstring_params.copy()
        paramstring_noinfo.pop('info', None)
        return urlencode(paramstring_noinfo)

    @cached_property
    def infoproperties(self):
        infoproperties = {f'paramstring_{k}': v for k, v in self.paramstring_params.items()}
        infoproperties['paramstring'] = self.paramstring
        infoproperties['paramstring_noinfo'] = self.paramstring_noinfo
        return infoproperties

    @cached_property
    def item(self):
        return {
            'label': self.name,
            'path': self.path,
            'art': self.art,
            'infoproperties': self.infoproperties,
            'context_menu': self.context_menu,
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
                BaseDirNodeCustomItem(**item, file=self.filename if self.basedir == NODE_BASEDIR else None)
                for item in BaseDirNodeItem(
                    self.filename,
                    self.basedir
                ).items
            ) if i and i.item
        ] if self.filename in self.files else []

    def build_basedir(self):
        return self.basedir_subdir or self.basedir_topdir
