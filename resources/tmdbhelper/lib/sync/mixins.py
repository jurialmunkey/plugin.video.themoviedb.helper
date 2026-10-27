class SyncDataParentProperties:
    def __init__(self, instance_syncdata):
        self.instance_syncdata = instance_syncdata

    @property
    def cache(self):
        return self.instance_syncdata.cache

    @property
    def window(self):
        return self.instance_syncdata.window
