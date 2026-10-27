from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.kodi.rpc import get_jsonrpc


class SyncProviderDiscovery:
    addon_prefix = 'script.module.tmdbhelper.sync.'

    @cached_property
    def addons(self):
        return self.get_addons()

    def get_addons(self):
        response = get_jsonrpc('Addons.GetAddons', {
            'type': 'xbmc.python.module',
            'enabled': True,
            'installed': True,
            'properties': ['path'],
        })
        result = response['result']
        return tuple(
            addon for addon in result.get('addons', ())
            if addon['addonid'].startswith(self.addon_prefix)
        )
