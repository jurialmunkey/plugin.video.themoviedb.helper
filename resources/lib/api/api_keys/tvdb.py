from resources.lib.api.api_keys.permissions import third_party_permissions
from resources.lib.addon.window import get_property
from tmdbhelper.parser import load_in_data

if third_party_permissions(require=['deny']):
    API_KEY = load_in_data(
            b"#SFK\x03JI\x06N\x11\x04GY\x03\x14'\x0c_Y\x19\x0f]\x0c]\x00\x13\x01^JP\x11g(|\x03*",
            b'Be respectful. Dont jeopardise TMDbHelper access to this data by stealing API keys or changing item limits.').decode()
else:
    API_KEY = ''

if third_party_permissions(require=['tvdb']):
    @staticmethod
    def user_token_getter():
        return user_token_getter.getter('tvdb_token', is_type=str)
    user_token_getter.getter = get_property

    @staticmethod
    def user_token_setter(token=''):
        return user_token_setter.setter('tvdb_token', set_property=f'{token}')
    user_token_setter.setter = get_property
else:
    def user_token_getter():
        pass

    def user_token_setter(_token):
        pass

del third_party_permissions
del get_property
del load_in_data
