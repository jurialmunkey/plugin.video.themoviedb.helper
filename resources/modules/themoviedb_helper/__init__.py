import pkgutil
import sys
from importlib.util import module_from_spec
from threading import Lock

from xbmcaddon import Addon

addon_path = Addon('plugin.video.themoviedb.helper').getAddonInfo('path')
finder = None
name = None
ispkg = None
spec = None
module = None
short_name = None
long_name = None
sub_module = None
packages = []

import_lock = Lock()
with import_lock:
    if addon_path not in sys.path:
        sys.path.append(addon_path)
    else:
        addon_path = None

    import resources.lib as base
    from resources.lib.addon.logger import kodi_traceback
    from resources.lib.api.api_keys.permissions import third_party_permissions

    __all__ = []
    __permissions__ = third_party_permissions(grant=['general', 'tmdb'])
    prefix = f'{base.__name__}.'

    for finder, name, ispkg in pkgutil.walk_packages(base.__path__,
                                                     prefix=prefix):
        if ispkg:
            packages.append((finder, name, ispkg))
            continue
        spec = finder.find_spec(name)
        if not spec:
            continue

        module = module_from_spec(spec)
        short_name = name[len(prefix):]
        long_name = f'{__name__}.{short_name}'

        try:
            sys.modules[long_name] = module
            spec.loader.exec_module(module)
        except ImportError:
            del sys.modules[long_name]
            continue

        __all__.append(short_name)
        globals()[short_name] = module

    for finder, name, ispkg in reversed(packages):
        spec = finder.find_spec(name)
        if not spec:
            continue

        spec.submodule_search_locations = None
        module = module_from_spec(spec)
        short_name = name[len(prefix):]
        long_name = f'{__name__}.{short_name}'

        try:
            sys.modules[long_name] = module
            spec.loader.exec_module(module)
            if '__all__' not in module.__dict__:
                raise ImportError(f'__all__ not defined for package {name}')
        except ImportError:
            del sys.modules[long_name]
            continue

        for sub_module in module.__dict__['__all__']:
            long_name = f'{__name__}.{name[len(prefix):]}.{sub_module}'
            if long_name in sys.modules:
                setattr(module, sub_module, sys.modules[long_name])
                continue
            module.__dict__['__all__'].remove(sub_module)
            kodi_traceback(ImportError(f'{long_name}: Access denied'),
                           notification=False)

        __all__.append(short_name)
        globals()[short_name] = module

    del __permissions__
    if addon_path:
        sys.path.remove(addon_path)

del import_lock
del packages
del sub_module
del long_name
del short_name
del module
del spec
del ispkg
del name
del finder
del prefix
del third_party_permissions
del kodi_traceback
del base
del addon_path
del Addon
del Lock
del module_from_spec
del pkgutil
