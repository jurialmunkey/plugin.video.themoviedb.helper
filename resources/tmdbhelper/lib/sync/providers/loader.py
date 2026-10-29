import importlib.util
import os
import sys
from threading import RLock
from xbmcvfs import translatePath
from tmdbhelper.lib.sync.providers.base import SyncProvider
from tmdbhelper.lib.sync.providers.features import ACTION_FEATURES, SYNC_FEATURES, WATCHED_GETTERS
from tmdbhelper.lib.sync.providers.ratings import RATINGS_MEDIATYPES, RatingsSupplier
from tmdbhelper.lib.sync.providers.imdb_top250 import IMDB_TOP250_MEDIATYPES, IMDbTop250Supplier
from tmdbhelper.lib.sync.providers.monitor_lists import MonitorListsSupplier
from tmdbhelper.lib.sync.providers.stats import StatsSupplier
from tmdbhelper.lib.sync.datatype import DataType
from tmdbhelper.lib.sync.providers.services import SERVICE_SYNC_FEATURES, ServiceDataType


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
    def validate_service_sync_classes(provider):
        for name, sync_class in provider.service_sync_classes.items():
            if name not in SERVICE_SYNC_FEATURES:
                raise ValueError(f'Unknown service sync type: {name}')
            if not isinstance(sync_class, type) or not issubclass(sync_class, ServiceDataType):
                raise TypeError(f'{name} must inherit ServiceDataType')
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
    def validate_service_action_classes(provider):
        for name, action_class in provider.service_action_classes.items():
            if not isinstance(name, str) or not name.startswith(provider.provider_id):
                raise ValueError('Service action names must start with the provider ID')
            if not callable(action_class):
                raise TypeError(f'Service action factory {name} must be callable')

    @staticmethod
    def validate_getter_classes(provider):
        if 'watched' in provider.capabilities:
            missing = set(WATCHED_GETTERS).difference(provider.getter_classes)
            if missing:
                raise ValueError(f'Watched providers must declare getters: {", ".join(sorted(missing))}')
        for name, getter_class in provider.getter_classes.items():
            if not callable(getter_class):
                raise TypeError(f'Getter factory {name} must be callable')

    @staticmethod
    def validate_ratings_classes(provider):
        for mediatype, supplier_class in provider.ratings_classes.items():
            if mediatype not in RATINGS_MEDIATYPES:
                raise ValueError(f'Unknown ratings media type: {mediatype}')
            if not isinstance(supplier_class, type) or not issubclass(supplier_class, RatingsSupplier):
                raise TypeError(f'Ratings supplier for {mediatype} must inherit RatingsSupplier')
            if not callable(supplier_class.get_ratings) or supplier_class.get_ratings is RatingsSupplier.get_ratings:
                raise TypeError(f'Ratings supplier for {mediatype} must implement get_ratings()')

    @staticmethod
    def validate_imdb_top250_classes(provider):
        for mediatype, supplier_class in provider.imdb_top250_classes.items():
            if mediatype not in IMDB_TOP250_MEDIATYPES:
                raise ValueError(f'Unknown IMDb Top 250 media type: {mediatype}')
            if mediatype not in provider.ratings_classes:
                raise ValueError(f'IMDb Top 250 supplier requires ratings support for {mediatype}')
            if not isinstance(supplier_class, type) or not issubclass(supplier_class, IMDbTop250Supplier):
                raise TypeError(f'IMDb Top 250 supplier for {mediatype} must inherit IMDbTop250Supplier')
            if not callable(supplier_class.get_items) or supplier_class.get_items is IMDbTop250Supplier.get_items:
                raise TypeError(f'IMDb Top 250 supplier for {mediatype} must implement get_items()')

    @staticmethod
    def validate_stats_class(provider):
        supplier_class = provider.stats_class
        if supplier_class is None:
            return
        if not isinstance(supplier_class, type) or not issubclass(supplier_class, StatsSupplier):
            raise TypeError('Stats supplier must inherit StatsSupplier')
        if not callable(supplier_class.get_items) or supplier_class.get_items is StatsSupplier.get_items:
            raise TypeError('Stats supplier must implement get_items()')

    @staticmethod
    def validate_monitor_lists_class(provider):
        supplier_class = provider.monitor_lists_class
        if supplier_class is None:
            return
        if not isinstance(supplier_class, type) or not issubclass(supplier_class, MonitorListsSupplier):
            raise TypeError('Monitor lists supplier must inherit MonitorListsSupplier')
        for method in ('get_lists', 'get_list_items'):
            implementation = getattr(supplier_class, method)
            if not callable(implementation) or implementation is getattr(MonitorListsSupplier, method):
                raise TypeError(f'Monitor lists supplier must implement {method}()')

    @staticmethod
    def validate_directory(provider):
        if provider.directory_item_class is not None:
            from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem
            if not isinstance(provider.directory_item_class, type) or not issubclass(provider.directory_item_class, BaseDirItem):
                raise TypeError('Provider directory item must inherit BaseDirItem')
            route = provider.directory_item_class().params['info']
            if route not in provider.list_routes:
                raise ValueError('Provider directory item must target a registered list route')
        for name, route in provider.list_routes.items():
            if not isinstance(name, str) or not name.startswith(f'{provider.provider_id}_'):
                raise ValueError(f'Provider list routes must start with {provider.provider_id}_: {name}')
            if set(route) != {'module_name', 'import_attr'}:
                raise ValueError(f'List route {name} must declare module_name and import_attr')
            if any(not isinstance(value, str) or not value for value in route.values()):
                raise ValueError(f'List route {name} must declare non-empty import names')

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
        if (
                (provider.sync_classes or provider.service_sync_classes)
                and type(provider).get_last_activities is SyncProvider.get_last_activities):
            raise TypeError('Provider must implement get_last_activities()')
        self.validate_sync_classes(provider)
        self.validate_service_sync_classes(provider)
        self.validate_action_classes(provider)
        self.validate_service_action_classes(provider)
        self.validate_getter_classes(provider)
        self.validate_ratings_classes(provider)
        self.validate_imdb_top250_classes(provider)
        self.validate_stats_class(provider)
        self.validate_monitor_lists_class(provider)
        self.validate_directory(provider)
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
                provider.migrate_settings()
                return provider
        except Exception as exc:
            raise RuntimeError(f"Unable to load sync provider {self.addon['addonid']}: {exc}") from exc
