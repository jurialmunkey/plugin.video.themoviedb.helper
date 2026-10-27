import importlib.util
import os
import sys
from threading import RLock
from xbmcvfs import translatePath
from tmdbhelper.lib.sync.providers.base import SyncProvider
from tmdbhelper.lib.sync.providers.features import ACTION_FEATURES, SYNC_FEATURES, WATCHED_GETTERS
from tmdbhelper.lib.sync.datatype import DataType


class SyncProviderLoader:
    interface_version = 3
    module_lock = RLock()

    def __init__(self, addon):
        self.addon = addon

    @property
    def module_name(self):
        return self.addon['addonid'].split('.', 2)[2].replace('.', '_')

    @property
    def module_path(self):
        return os.path.join(translatePath(self.addon['path']), 'resources', 'lib', self.module_name)

    def load_module(self):
        try:
            return sys.modules[self.module_name]
        except KeyError:
            pass
        spec = importlib.util.spec_from_file_location(
            self.module_name, os.path.join(self.module_path, '__init__.py'),
            submodule_search_locations=[self.module_path])
        module = importlib.util.module_from_spec(spec)
        sys.modules[self.module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            for name in tuple(sys.modules):
                if name == self.module_name or name.startswith(f'{self.module_name}.'):
                    del sys.modules[name]
            raise
        return module

    @staticmethod
    def validate_sync_classes(provider):
        for name, sync_class in provider.sync_classes.items():
            if name not in SYNC_FEATURES:
                raise ValueError(f'Unknown sync type: {name}')
            if not isinstance(sync_class, type) or not issubclass(sync_class, DataType):
                raise TypeError(f'{name} must inherit DataType')
            if not isinstance(getattr(sync_class, 'method', None), str) or not sync_class.method:
                raise ValueError(f'{name} must declare a non-empty method')

    @staticmethod
    def validate_action_classes(provider):
        for name, action_class in provider.action_classes.items():
            if name not in ACTION_FEATURES:
                raise ValueError(f'Unknown sync action: {name}')
            if not callable(action_class):
                raise TypeError(f'Action factory {name} must be callable')

    @staticmethod
    def validate_getter_classes(provider):
        if 'watched' in provider.capabilities:
            missing = set(WATCHED_GETTERS).difference(provider.getter_classes)
            if missing:
                raise ValueError(f'Watched providers must declare getters: {", ".join(sorted(missing))}')
        for name, getter_class in provider.getter_classes.items():
            if not callable(getter_class):
                raise TypeError(f'Getter factory {name} must be callable')

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
        self.validate_sync_classes(provider)
        self.validate_action_classes(provider)
        self.validate_getter_classes(provider)
        if not provider.capabilities:
            raise ValueError('Provider must expose at least one capability')
        if provider.scrobbler_class is not None and not callable(provider.scrobbler_class):
            raise TypeError('Provider scrobbler must be callable')
        return provider

    def load(self):
        try:
            with self.module_lock:
                provider = self.validate_provider(self.load_module().Provider())
                provider.addon_id = self.addon['addonid']
                return provider
        except Exception as exc:
            raise RuntimeError(f"Unable to load sync provider {self.addon['addonid']}: {exc}") from exc
