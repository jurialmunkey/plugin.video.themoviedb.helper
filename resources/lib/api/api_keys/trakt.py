from resources.lib.api.api_keys.permissions import third_party_permissions
from resources.lib.addon.plugin import get_setting, set_setting

if third_party_permissions(require=['deny']):
    CLIENT_ID = 'e6fde6173adf3c6af8fd1b0694b9b84d7c519cefc24482310e1de06c6abe5467'
    CLIENT_SECRET = '15119384341d9a61c751d8d515acbc0dd801001d4ebe85d3eef9885df80ee4d9'
else:
    CLIENT_ID = ''
    CLIENT_SECRET = ''

if third_party_permissions(require=['trakt']):
    def user_token_getter():
        return user_token_getter.getter('trakt_token', 'str')
    user_token_getter.getter = get_setting

    def user_token_setter(token=''):
        return user_token_setter.setter('trakt_token', token, 'str')
    user_token_setter.setter = set_setting
else:
    def user_token_getter():
        pass

    def user_token_setter(_token):
        pass

del third_party_permissions
del get_setting
del set_setting
