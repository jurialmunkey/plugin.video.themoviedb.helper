from tmdbhelper.lib.script.sync.mdblist.item import ItemSync
from tmdbhelper.lib.addon.plugin import get_infolabel, get_localized
from tmdbhelper.lib.addon.dialog import busy_decorator
from jurialmunkey.ftools import cached_property
from xbmcgui import Dialog


class ItemUserList(ItemSync):
    preconfigured = True

    def get_self(self):
        return self if self.is_allowed_type else None

    """
    lists
    """
    @cached_property
    def lists(self):
        return self.get_lists()

    def get_lists(self):
        from tmdbhelper.lib.api.mdblist.api import MDbListAPI
        try:
            response = MDbListAPI().get_request('lists', 'user')
            return [i for i in response if i and not i.get('dynamic')]
        except AttributeError:
            return

    """
    list_id
    """
    @cached_property
    def list_id(self):
        return self.get_list_id()

    def get_list_id(self):
        if self.remove:
            return get_infolabel("ListItem.Property(param.list_id)")
        if self.lists is None:  # No API credentials
            Dialog().ok('MDbList', f'{get_localized(32516)}\n{get_localized(32517)}')
            return
        if not self.lists:  # No static lists
            Dialog().ok('MDbList', get_localized(32518))
            return
        names = [i.get('name', '') for i in self.lists]
        x = Dialog().select(get_localized(32133), names)
        if x == -1:
            return
        return self.lists[x]['id']

    """
    overrides
    """

    def get_remove(self):
        if get_infolabel("ListItem.Property(param.info)") != 'mdblist_userlist':
            return False
        if get_infolabel("ListItem.Property(param.dynamic)"):
            return False
        return True

    def get_name(self):
        return get_localized(32519) if self.remove else get_localized(32514)

    @busy_decorator
    def modify_static_list(self):
        from tmdbhelper.lib.api.mdblist.api import MDbList
        return MDbList().modify_static_list(
            self.list_id,
            media_type=self.base_trakt_type,
            media_id=self.tmdb_id,
            media_provider='tmdb',
            action='remove' if self.remove else 'add'
        )

    def get_sync_response(self):
        if not self.list_id:
            return
        return self.modify_static_list()
