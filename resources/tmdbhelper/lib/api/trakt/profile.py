from tmdbhelper.lib.addon.plugin import KeyGetter
from jurialmunkey.ftools import cached_property


class TraktProfile:
    def __init__(self, trakt_api):
        self.trakt_api = trakt_api

    def get_key(self, dictionary, key):
        return KeyGetter(dictionary).get_key(key)

    @cached_property
    def meta(self):
        if not self.trakt_api.is_authorized:
            return
        return self.trakt_api.get_response_json('users/me')

    @cached_property
    def ids(self):
        return self.get_key(self.meta, 'ids')

    @cached_property
    def slug(self):
        return self.get_key(self.ids, 'slug')
