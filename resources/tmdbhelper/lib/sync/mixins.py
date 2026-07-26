class SyncDataParentProperties:
    def __init__(self, instance_syncdata):
        self.instance_syncdata = instance_syncdata

    @property
    def cache(self):
        return self.instance_syncdata.cache

    @property
    def window(self):
        return self.instance_syncdata.window

    @property
    def trakt_api(self):
        return self.instance_syncdata.trakt_api

    @property
    def mdblist_api(self):
        return self.instance_syncdata.mdblist_api
