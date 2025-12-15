from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH
from tmdbhelper.lib.addon.dialog import BusyDialog
from jurialmunkey.ftools import cached_property
from xbmcgui import Dialog
from tmdbhelper.lib.script.discover.base import (
    DiscoverList,
    DiscoverMulti,
    DiscoverYear,
    DiscoverSave,
    DiscoverReset,
    DiscoverMain,
    DiscoverItem
)


NODE_FILENAME = 'TMDb Discover.json'


class DiscoverProviderItem(DiscoverItem):
    @cached_property
    def icon(self):
        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
        return TMDbImagePath().get_imagepath_origin(self.image)

    @cached_property
    def label2(self):
        return f"ID #{self.value}"
