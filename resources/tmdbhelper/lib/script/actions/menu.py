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
        from tmdbhelper.lib.script.actions.trakt.userlist import ItemUserList
        from tmdbhelper.lib.script.actions.trakt.rating import ItemRating
        from tmdbhelper.lib.script.actions.trakt.comments import ItemComments
        from tmdbhelper.lib.script.actions.trakt.favorites import ItemFavorites
        return {name: ('trakt_api', self.trakt_api, action_class) for name, action_class in (
            ('userlist', ItemUserList), ('rating', ItemRating), ('comments', ItemComments),
            ('favorites', ItemFavorites))}

    def get_mdblist_actions(self):
        from tmdbhelper.lib.script.actions.mdblist.userlist import ItemUserList
        return {'mdblistuser': ('mdblist_api', self.mdblist_api, ItemUserList)}

    def get_item(self, name, *args):
        api_attribute, api, action_class = self.actions[name]
        item = action_class(*args)
        setattr(item, api_attribute, api)
        return item

    def invalidate_caches(self, features):
        if 'ratings' in features:
            self.trakt_api.invalidate_user_ratings()
