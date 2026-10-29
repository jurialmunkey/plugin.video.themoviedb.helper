from jurialmunkey.ftools import cached_property


def is_provider_user_slug(user_slug):
    return bool(user_slug and user_slug.startswith('__api_') and user_slug.endswith('__'))


class MonitorListsSupplier:
    def __init__(self, provider):
        self.provider = provider

    @property
    def user_slug(self):
        return f'__api_{self.provider.provider_id}__'

    @cached_property
    def lists(self):
        return self.get_lists()

    def get_lists(self):
        raise NotImplementedError

    def get_list_items(self, list_slug):
        raise NotImplementedError

    def get_legacy_list_slug(self, user_slug, list_slug):
        """Translate a pre-provider reference, or return None when it is not owned."""
        return None
