from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.base.lists_base import BaseDirList
from tmdbhelper.lib.items.directories.lists_default import ListDefault, ListProperties
from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
from tmdbhelper.lib.sync.providers.tmdb.directories.item import get_menu_items
from tmdbhelper.lib.sync.providers.tmdb.directories.mapper import TMDbDirectoryItemMapper


class TMDbBaseDirList(BaseDirList):
    def __init__(self, items):
        self.items = items

    @property
    def basedir(self):
        return self.items


class TMDbDirectoryProperties(ListProperties):
    plugin_name = 'TMDb'
    container_content = ''
    item_mapper_class = TMDbDirectoryItemMapper

    @cached_property
    def entries(self):
        return self.get_entries()

    def get_entries(self):
        if not self.provider.is_user_authorized:
            return []
        return TMDbBaseDirList(get_menu_items()).get_basedir(self.tmdb_type)

    @cached_property
    def type_art(self):
        return len({entry.type for entry in self.entries}) > 1

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        return [self.get_mapped_item(entry) for entry in self.entries]

    def get_mapped_item(self, item, add_infoproperties=None):
        mapper = self.item_mapper_class(item, add_infoproperties)
        mapper.type_art = self.type_art
        return mapper.item


class ListTMDbDirectory(ListDefault):
    list_properties_class = TMDbDirectoryProperties
    kodi_details = False

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.provider = SyncProviderRegistry().get_provider('tmdb')
        list_properties.plugin_name = 'TMDb'
        list_properties.pagination = False
        return list_properties

    def get_items(self, tmdb_type=None, **kwargs):
        self.list_properties.tmdb_type = tmdb_type if tmdb_type not in ('both', 'None') else None
        return self.get_items_finalised()
