import sys

class _Finder:
    from importlib.util import find_spec as _find_spec

    class SysPathLoader:
        from xbmcaddon import Addon as _Addon

        def __init__(self, addon_id):
            self._loaded = False
            self._path = self._Addon(addon_id).getAddonInfo('path')

        def __enter__(self):
            if self._path in sys.path:
                self._loaded = False
            else:
                sys.path.append(self._path)
                self._loaded = True

        def __exit__(self, *_args, **_kwargs):
            if self._loaded:
                sys.path.remove(self._path)

    basename = 'resources.lib'
    sys_path_loader = SysPathLoader('plugin.video.themoviedb.helper')

    @classmethod
    def find_spec(cls, fullname, path, target=None):
        basename, _, relname = fullname.partition('.')
        if basename != __name__:
            return None
        if not __access__.import_allowed(relname):
            msg = f'Import denied for module {fullname!r}'
            raise ImportError(msg, name=fullname, path=path)

        with cls.sys_path_loader:
            spec = cls._find_spec(f'{cls.basename}{relname and f".{relname}"}')
        if not spec:
            msg = f'No module named {fullname!r}'
            raise ModuleNotFoundError(msg, name=fullname, path=path)

        return __access__.set_spec_access(spec, basename, relname)


with _Finder.sys_path_loader:
    from resources.lib.addon.permissions import __access__

sys.meta_path.insert(0, _Finder)
