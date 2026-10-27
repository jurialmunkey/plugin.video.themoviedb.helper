from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.script.sync.menu import Menu as BasicMenu
from tmdbhelper.lib.sync.datasync import SyncDataFactory
from tmdbhelper.lib.script.actions.discovery import ActionDiscovery


class Menu(BasicMenu):
    @cached_property
    def syncdata(self):
        return self.get_syncdata()

    def get_syncdata(self):
        return SyncDataFactory()

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        return self.action_discovery.get_items(*self.item_args)

    @cached_property
    def action_discovery(self):
        return self.get_action_discovery()

    def get_action_discovery(self):
        return ActionDiscovery(self.syncdata)

    @property
    def item_args(self):
        return (self.tmdb_type, self.tmdb_id, self.season, self.episode)

    def item_get_self(self, item):
        return item.get_self()

    def choose(self):
        if not self.choices:
            return -1
        if len(self.choices) == 1:
            return 0
        from xbmcgui import Dialog
        return Dialog().select(get_localized(32549), [self.get_choice_name(item) for item in self.choices])

    @staticmethod
    def get_choice_name(item):
        from tmdbhelper.lib.script.sync.provider import ItemSync
        service_name = item.sync_provider.display_name if isinstance(item, ItemSync) else item.service_name
        return f'{item.name} ({service_name})'

    def select(self, sync_type=None):
        if sync_type and sync_type not in self.items:
            return
        return super().select(sync_type)


def sync_item(tmdb_type, tmdb_id, season=None, episode=None, sync_type=None):
    Menu(tmdb_type, tmdb_id, season, episode).select(sync_type)
