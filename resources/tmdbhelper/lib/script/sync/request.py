from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.script.sync.item import ItemSync as BasicItemSync


class ItemSync(BasicItemSync):
    sync_key = None
    sync_url = None

    @cached_property
    def method(self):
        return self.get_method()

    def get_method(self):
        if not self.remove:
            return self.sync_url
        return f'{self.sync_url}/remove'

    @cached_property
    def post_response_args(self):
        return self.get_post_response_args()

    def get_post_response_args(self):
        raise NotImplementedError

    @cached_property
    def post_response_data(self):
        return self.get_post_response_data()

    def get_post_response_data(self):
        return {self.post_response_type: self.post_response_item}

    @cached_property
    def post_response_type(self):
        return self.get_post_response_type()

    def get_post_response_type(self):
        raise NotImplementedError

    @cached_property
    def post_response_item(self):
        return self.get_post_response_item()

    def get_post_response_item(self):
        if isinstance(self.sync_item, list):
            return self.sync_item
        return [self.sync_item]

    @cached_property
    def sync_item(self):
        return self.get_sync_item()

    def get_sync_item(self):
        raise NotImplementedError
