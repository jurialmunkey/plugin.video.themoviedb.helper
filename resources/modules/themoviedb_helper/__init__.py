import sys
from threading import Lock as _Lock

from xbmcaddon import Addon as _Addon


__all__ = []
__path__ = []
__protected_access__ = set()


def _import_module(name, package='resources.lib', excluding=(),
                   reload=False, recursive=True,
                   parent_module=None, parent_path=None,
                   module_finder=None):

    from importlib.machinery import ModuleSpec
    from importlib.util import LazyLoader, module_from_spec, resolve_name
    from pkgutil import iter_modules

    class NotAvailableLoader:
        def __init__(self, msg='Module not available'):
            self.msg = msg

        def create_module(self, _spec):
            return None

        def exec_module(self, _module):
            raise ImportError(self.msg)

    if not name:
        msg = 'Empty module name'
        raise ValueError(msg)

    is_root = (name == package)

    if is_root:
        absolute_name = package
        relative_name = ''
        export_name = __name__
    else:
        if not name.startswith(('.', f'{package}.')):
            name = f'.{name}'
        absolute_name = resolve_name(name, package)
        relative_name = absolute_name.partition(f'{package}.')[2]
        export_name = f'{__name__}.{relative_name}'

    if not reload:
        try:
            module = sys.modules[absolute_name]
            path = module.__spec__.submodule_search_locations
            index = module.__dict__.get('__all__')

            module = sys.modules[export_name]
            module.__spec__.submodule_search_locations = path
            if index:
                module.__all__ = index
            return module
        except KeyError:
            pass

    spec = None
    path = None
    module = None

    if is_root:
        parent_name = package
    elif '.' in absolute_name:
        parent_name, _, name = absolute_name.rpartition('.')

    if not parent_module and parent_name:
        parent_module = _import_module(parent_name, recursive=False)

    if parent_module:
        path = parent_path or parent_module.__spec__.submodule_search_locations
        if is_root:
            module = parent_module
            spec = module.__spec__
            parent_module = None

    if not module:
        if (not parent_module
                or '__all__' not in parent_module.__dict__
                or name not in parent_module.__all__):
            if parent_module and name in parent_module.__dict__:
                delattr(parent_module, name)
            spec = ModuleSpec(
                name=export_name,
                loader=NotAvailableLoader(f'Module {absolute_name!r} not available for import'),
                origin=None,
                loader_state=None,
                is_package=recursive,
            )
        elif excluding and relative_name.startswith(excluding):
            if name in parent_module.__all__:
                parent_module.__all__.remove(name)
            if name in parent_module.__dict__:
                delattr(parent_module, name)
            spec = ModuleSpec(
                name=export_name,
                loader=NotAvailableLoader(f'Module {absolute_name!r} excluded from import'),
                origin=None,
                loader_state=None,
                is_package=recursive,
            )

        if not spec:
            for finder in [module_finder] + sys.meta_path:
                if not finder or 'find_spec' not in finder.__dict__:
                    continue
                spec = finder.find_spec(absolute_name, path)
                if spec is not None:
                    break
            else:
                msg = f'No module named {absolute_name!r} in {path=!r}'
                raise ModuleNotFoundError(msg, name=absolute_name, path=path)

        spec.name = export_name
        spec.loader.name = export_name
        spec.loader = LazyLoader(spec.loader)
        module = module_from_spec(spec)
        sys.modules[export_name] = module
        spec.loader.exec_module(module)

    if parent_module:
        setattr(parent_module, name, module)
        __all__.append(relative_name)
        globals()[relative_name] = module
    elif is_root:
        __all__.extend(module.__all__)
        globals().update(module.__builtins__['globals']())

    if not recursive or not spec.submodule_search_locations:
        return module

    path = spec.submodule_search_locations
    prefix = f'{absolute_name}.'
    for module_info in iter_modules(path, prefix):
        _import_module(module_info.name, excluding=excluding,
                       recursive=module_info.ispkg,
                       parent_module=module, parent_path=path,
                       module_finder=module_info.module_finder)

    return module


_IMPORT_LOCK = _Lock()
with _IMPORT_LOCK:
    _PATH = _Addon('plugin.video.themoviedb.helper').getAddonInfo('path')
    if _PATH not in sys.path:
        sys.path.append(_PATH)
    else:
        _PATH = None

    from resources.lib.addon.permissions import handler as _handler

    __protected_access__.update(_handler(grant=['general', 'tmdb']))
    _import_module('api', excluding='api.api_keys')
    __protected_access__.clear()
    _import_module('resources.lib', reload=True, excluding='api')

    if _PATH:
        sys.path.remove(_PATH)
