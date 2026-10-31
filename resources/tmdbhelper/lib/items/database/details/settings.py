from os.path import join
from xml.etree import ElementTree
from xbmcaddon import Addon
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDONPATH


class DetailsSettings:
    """Snapshot the settings that configure the item detail service.

    Every declared setting is included so that newly added settings restart the
    service by default. Settings the add-on writes as runtime state are excluded
    because they do not change how item details are retrieved.
    """

    state_settings = (
        'last_autoupdate', 'monitor_userlist', 'monitor_userslug',
        'tmdb_user_token', 'trakt_token',
    )

    @cached_property
    def names(self):
        return self.get_names()

    def get_names(self):
        tree = ElementTree.parse(join(ADDONPATH, 'resources', 'settings.xml'))
        return tuple(
            name for name in (i.get('id') for i in tree.iter('setting'))
            if name and name not in self.state_settings)

    def get_snapshot(self):
        addon = Addon()
        return {name: addon.getSetting(name) for name in self.names}
