class SyncDataParentProperties:
    @property
    def cache(self):
        return self.instance_syncdata.cache

    @property
    def window(self):
        return self.instance_syncdata.window

    @property
    def get_response_json(self):
        return self.instance_syncdata.get_response_json

    @property
    def trakt_api(self):
        return self.instance_syncdata.trakt_api
