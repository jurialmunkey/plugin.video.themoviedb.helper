from tmdbhelper.lib.api.kodi.rpc import get_jsonrpc
from tmdbhelper.lib.sync.providers.loader import SyncProviderLoader


class SyncProviderAddon:
    def __init__(self, addon_id):
        self.addon_id = addon_id

    def get_addon(self):
        response = get_jsonrpc('Addons.GetAddons', {
            'type': 'xbmc.python.module',
            'enabled': 'all',
            'installed': True,
            'properties': ['path', 'enabled'],
        })
        return next((addon for addon in response['result'].get('addons', ())
                     if addon['addonid'] == self.addon_id), None)

    def get_provider(self):
        addon = self.get_addon()
        if addon is not None and addon['enabled']:
            return SyncProviderLoader(addon).load()
