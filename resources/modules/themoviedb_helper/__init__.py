import pkgutil
import sys
from importlib.util import module_from_spec

from xbmcaddon import Addon

addon_path = Addon('plugin.video.themoviedb.helper').getAddonInfo('path')
if addon_path not in sys.path:
    sys.path.append(addon_path)

import resources.lib as base
from resources.lib.addon.logger import kodi_traceback
from resources.lib.addon.consts import PERMISSIONS

__all__ = []
__permissions__ = PERMISSIONS('general')

prefix = f'{base.__name__}.'
finder = None
name = None
ispkg = None
spec = None
module = None
short_name = None
long_name = None
sub_module = None

packages = []

for finder, name, ispkg in pkgutil.walk_packages(base.__path__, prefix=prefix):
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

for finder, name, ispkg in packages:
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
        long_name = f'{name}.{sub_module}'
        if long_name in sys.modules:
            setattr(module, sub_module, sys.modules[long_name])
            continue
        module.__dict__['__all__'].remove(sub_module)
        kodi_traceback(ImportError(f'{long_name}: Access denied'),
                       notification=False)

    __all__.append(short_name)
    globals()[short_name] = module

sys.path.remove(addon_path)

del sub_module
del long_name, 
del short_name
del module
del spec
del ispkg
del name
del finder
del prefix
del __permissions__
del PERMISSIONS
del kodi_traceback
del base
del addon_path
del Addon
del module_from_spec
del pkgutil
