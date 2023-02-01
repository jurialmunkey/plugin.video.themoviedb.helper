from resources.lib.addon.permissions import handler
from resources.lib.addon.plugin import get_setting

if handler(require=['deny']):
    API_KEY = 'fcca59bee130b70db37ee43e63f8d6c1'
else:
    API_KEY = ''

if handler(require=['fanarttv']):
    CLIENT_KEY = get_setting('fanarttv_clientkey', 'str')
else:
    CLIENT_KEY = ''

del handler
del get_setting
