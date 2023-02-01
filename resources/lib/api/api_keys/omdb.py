from resources.lib.addon.permissions import handler
from resources.lib.addon.plugin import get_setting

if handler(require=['omdb']):
    API_KEY = get_setting("omdb_apikey", "str")
else:
    API_KEY = ''

del handler
del get_setting
