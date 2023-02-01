from resources.lib.addon.permissions import handler
from resources.lib.addon.plugin import get_setting

if handler(require=['mdblist']):
    API_KEY = get_setting("mdblist_apikey", "str")
else:
    API_KEY = ''

del handler
del get_setting
