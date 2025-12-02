from xbmcgui import Dialog, INPUT_ALPHANUM
from tmdbhelper.lib.addon.plugin import get_localized, convert_type
from jurialmunkey.ftools import cached_property

from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory
from tmdbhelper.lib.items.directories.lists_default import ItemCache


class ListGemini(ContainerDefaultCacheDirectory):

    cache_days = 0.25  # 6 hours default cache

    @cached_property
    def cache_name(self):
        return '_'.join(map(str, self.cache_name_tuple))

    @cached_property
    def cache_name_tuple(self):
        return (f'{self.__class__.__name__}', self.query, )

    @cached_property
    def gemini(self):
        from tmdbhelper.lib.api.gemini.api import Gemini
        return Gemini()

    @ItemCache('ItemContainer.db')
    def get_cached_response(self):
        return self.get_prompt_items()

    def get_prompt_items(self):
        from tmdbhelper.lib.addon.dialog import BusyDialog
        with BusyDialog():
            data = self.gemini.get_prompt_items(self.query)
        return data

    def get_items(self, query=None, **kwargs):
        if not self.gemini.api_key:
            Dialog().ok('Gemini', f"{get_localized(32150)}[CR]{get_localized(32151).format('https://aistudio.google.com/app/api-keys')}")
            return
        self.query = query or Dialog().input(get_localized(32044), type=INPUT_ALPHANUM)
        if not self.query:
            return
        items = self.get_cached_response()
        if not items:
            return
        self.container_content = convert_type('both', 'container', items=items)
        self.plugin_name = 'Gemini'
        return items
