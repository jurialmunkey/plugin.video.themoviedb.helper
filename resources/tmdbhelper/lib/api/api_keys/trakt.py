from tmdbhelper.lib.addon.permissions import __access__
from tmdbhelper.lib.api.api_keys.tokenhandler import TokenHandler
from tmdbhelper.lib.addon.plugin import get_setting

DEFAULT_CLIENT_ID = 'e6fde6173adf3c6af8fd1b0694b9b84d7c519cefc24482310e1de06c6abe5467'
DEFAULT_CLIENT_SECRET = '15119384341d9a61c751d8d515acbc0dd801001d4ebe85d3eef9885df80ee4d9'

USER_CLIENT_ID = get_setting('trakt_apikey', 'str')
USER_CLIENT_SECRET = get_setting('trakt_secret', 'str')

if __access__.has_access('internal'):
    CLIENT_ID = USER_CLIENT_ID or DEFAULT_CLIENT_ID
    CLIENT_SECRET = USER_CLIENT_SECRET or DEFAULT_CLIENT_SECRET
    USER_TOKEN = TokenHandler('trakt_token', store_as='setting')

elif __access__.has_access('trakt'):
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    USER_TOKEN = TokenHandler('trakt_token', store_as='setting')

else:
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    USER_TOKEN = TokenHandler()
