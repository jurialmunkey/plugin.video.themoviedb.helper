from resources.lib.addon.permissions import handler

if handler(require=['deny']):
    API_KEY = 'a07324c669cac4d96789197134ce272b'
else:
    API_KEY = ''

del handler
