from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.plugin import executebuiltin
from tmdbhelper.lib.addon.tmdate import get_timestring_zulu_now
from tmdbhelper.lib.sync.collectiondrops import get_collection_drop_store


class CollectionDropAction:
    def __init__(self, collection_id):
        self.collection_id = try_int(collection_id)
        if self.collection_id <= 0:
            raise ValueError('A positive TMDb collection ID is required')

    @cached_property
    def store(self):
        return self.get_store()

    @staticmethod
    def get_store():
        return get_collection_drop_store()

    def run(self):
        self.store.drop(self.collection_id, get_timestring_zulu_now())
        executebuiltin('Container.Refresh')


def drop_collection(collection_id=None, **kwargs):
    CollectionDropAction(collection_id).run()
