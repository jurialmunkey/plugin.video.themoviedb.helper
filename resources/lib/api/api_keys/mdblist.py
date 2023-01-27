from resources.lib.api.api_keys.permissions import third_party_permissions
from resources.lib.addon.plugin import get_setting

if third_party_permissions(require=['mdblist']):
    API_KEY = get_setting("mdblist_apikey", "str")
else:
    API_KEY = ''

del third_party_permissions
del get_setting
