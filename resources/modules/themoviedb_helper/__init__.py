import pkgutil
import sys
from importlib.util import module_from_spec

from xbmcaddon import Addon

sys.path.append(Addon('plugin.video.themoviedb.helper').getAddonInfo('path'))

import resources.lib as base

__all__ = []

prefix = f'{base.__name__}.'
finder = None
name = None
ispkg = None
spec = None
module = None
short_name = None

for finder, name, ispkg in pkgutil.walk_packages(base.__path__, prefix=prefix):
    if ispkg:
        continue
    spec = finder.find_spec(name)
    if not spec:
        continue

    module = module_from_spec(spec)
    short_name = name[len(prefix):]
    sys.modules[f'{__name__}.{short_name}'] = module
    spec.loader.exec_module(module)

    __all__.append(short_name)
    globals()[short_name] = module

del short_name
del module
del spec
del ispkg
del name
del finder
del prefix
del PERMISSIONS
del base
del Addon
del module_from_spec
del pkgutil
