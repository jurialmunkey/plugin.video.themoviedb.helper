from resources.lib.api.api_keys.permissions import third_party_permissions
from resources.lib.addon.plugin import get_setting

if third_party_permissions(require=['deny']):
    API_KEY = 'fcca59bee130b70db37ee43e63f8d6c1'
else:
    API_KEY = ''

if third_party_permissions(require=['fanarttv']):
    CLIENT_KEY = get_setting('fanarttv_clientkey', 'str')
else:
    CLIENT_KEY = ''

del third_party_permissions
del get_setting
