from resources.lib.api.api_keys.permissions import third_party_permissions

if third_party_permissions(require=['deny']):
    API_KEY = 'a07324c669cac4d96789197134ce272b'
else:
    API_KEY = ''

del third_party_permissions
