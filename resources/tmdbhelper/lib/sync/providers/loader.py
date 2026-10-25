import importlib.util
import os
import sys
from threading import RLock
from xbmcvfs import translatePath
from tmdbhelper.lib.sync.providers.base import SyncProvider


class SyncProviderLoader:
    interface_version = 3
    module_lock = RLock()

    def __init__(self, addon):
        self.addon = addon

    @property
    def module_name(self):
        return f"_tmdbhelper_sync_{self.addon['addonid'].encode('utf-8').hex()}"

    def load_module(self):
        try:
            return sys.modules[self.module_name]
        except KeyError:
            pass
        path = translatePath(self.addon['path'])
        spec = importlib.util.spec_from_file_location(
            self.module_name, os.path.join(path, 'provider.py'),
            submodule_search_locations=[path])
        module = importlib.util.module_from_spec(spec)
        sys.modules[self.module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            del sys.modules[self.module_name]
            raise
        return module

    def validate_provider(self, provider):
        if not isinstance(provider, SyncProvider):
            raise TypeError('Provider must inherit SyncProvider')
        if provider.interface_version != self.interface_version:
            raise ValueError(f'Unsupported sync interface version: {provider.interface_version}')
        if not isinstance(provider.provider_id, str) or not provider.provider_id:
            raise ValueError('Provider must declare a non-empty provider_id')
        if not isinstance(provider.display_name, str) or not provider.display_name:
            raise ValueError('Provider must declare a non-empty display_name')
        if type(provider).is_authorized is SyncProvider.is_authorized:
            raise TypeError('Provider must implement is_authorized()')
        if provider.sync_classes and type(provider).get_last_activities is SyncProvider.get_last_activities:
            raise TypeError('Provider must implement get_last_activities()')
        if not provider.capabilities:
            raise ValueError('Provider must expose at least one capability')
        for factory in (*provider.sync_classes.values(), *provider.action_classes.values(), *provider.getter_classes.values()):
            if not callable(factory):
                raise TypeError('Provider factories must be callable')
        if provider.scrobbler_class is not None and not callable(provider.scrobbler_class):
            raise TypeError('Provider scrobbler must be callable')
        return provider

    def load(self):
        try:
            with self.module_lock:
                return self.validate_provider(self.load_module().Provider())
        except Exception as exc:
            raise RuntimeError(f"Unable to load sync provider {self.addon['addonid']}: {exc}") from exc
