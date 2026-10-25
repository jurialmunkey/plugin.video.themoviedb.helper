from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.contains import CommonContainerAPIs


class ServiceActions(CommonContainerAPIs):
    @cached_property
    def actions(self):
        return self.get_actions()

    def get_actions(self):
        actions = {}
        if self.trakt_api.authenticator.is_authorized:
            actions.update(self.get_trakt_actions())
        if self.mdblist_api is not None:
            actions.update(self.get_mdblist_actions())
        return actions

    def get_trakt_actions(self):
        from .trakt.userlist import ItemUserList
        from .trakt.rating import ItemRating
        from .trakt.comments import ItemComments
        return {name: ('trakt_api', self.trakt_api, action_class) for name, action_class in (
            ('userlist', ItemUserList), ('rating', ItemRating), ('comments', ItemComments))}

    def get_mdblist_actions(self):
        from .mdblist.userlist import ItemUserList
        return {'mdblistuser': ('mdblist_api', self.mdblist_api, ItemUserList)}

    def get_item(self, name, *args):
        api_attribute, api, action_class = self.actions[name]
        item = action_class(*args)
        setattr(item, api_attribute, api)
        return item
