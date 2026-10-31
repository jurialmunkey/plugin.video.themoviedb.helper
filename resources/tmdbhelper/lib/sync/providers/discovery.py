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

    def get_addon_id(self, provider_id):
        return f'{self.addon_prefix}{provider_id}'

    def get_addon(self, provider_id):
        """Return the addon named after the provider ID, or None if it is not discovered."""
        addon_id = self.get_addon_id(provider_id)
        return next((addon for addon in self.addons if addon['addonid'] == addon_id), None)
