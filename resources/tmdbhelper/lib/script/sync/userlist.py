from tmdbhelper.lib.script.sync.item import ItemSync
from tmdbhelper.lib.addon.plugin import get_infolabel, get_localized, get_setting
from tmdbhelper.lib.addon.dialog import BusyDialog
from xbmcgui import Dialog


class ItemMDbListAttributes:
    """
    lists
    """
    @property
    def lists(self):
        try:
            return self._lists
        except AttributeError:
            self._lists = self.get_lists()
            return self._lists

    @lists.setter
    def lists(self, value):
        self._lists = value

    def get_lists(self):
        from tmdbhelper.lib.api.mdblist.api import MDbList
        if not get_setting('mdblist_apikey', 'str'):
            return
        response = MDbList().get_request('lists', 'user')
        return [i for i in response if i and not i.get('dynamic')]

    """
    list_id
    """
    @property
    def list_id(self):
        try:
            return self._list_id
        except AttributeError:
            self._list_id = self.get_list_id()
            return self._list_id

    @list_id.setter
    def list_id(self, value):
        self._list_id = value

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


class ItemMDbList(ItemSync, ItemMDbListAttributes):
    preconfigured = True

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

    def get_sync_response(self):
        from tmdbhelper.lib.api.mdblist.api import MDbList
        if not self.list_id:
            return
        with BusyDialog():
            data = MDbList().modify_static_list(
                self.list_id,
                media_type=self.base_trakt_type,
                media_id=self.tmdb_id,
                media_provider='tmdb',
                action='remove' if self.remove else 'add'
            )
        return data


class ItemUserList(ItemSync):
    preconfigured = True
    trakt_sync_url = 'items'

    @property
    def userlist(self):
        try:
            return self._userlist
        except AttributeError:
            self._userlist = self.get_userlist()
            return self._userlist

    @userlist.setter
    def userlist(self, value):
        self._userlist = value

    @property
    def userlist_slug(self):
        try:
            return self._userlist_slug
        except AttributeError:
            self._userlist_slug = self.get_userlist_slug()
            return self._userlist_slug

    @userlist_slug.setter
    def userlist_slug(self, value):
        self._userlist_slug = value

    @property
    def userlist_user(self):
        try:
            return self._userlist_user
        except AttributeError:
            self._userlist_user = self.get_userlist_user()
            return self._userlist_user

    @userlist_user.setter
    def userlist_user(self, value):
        self._userlist_user = value

    """
    methods
    """

    def add_list(self):
        """ Create a new Trakt list and returns tuple of list and user slug """
        name = Dialog().input(get_localized(32356))
        if not name:
            return
        response = self.trakt_api.post_response('users/me/lists', postdata={'name': name})
        if not response or not response.json():
            return
        return (
            response.json().get('ids', {}).get('slug'),
            response.json().get('user', {}).get('ids', {}).get('slug'))

    def add_to_library(self, tmdb_type, tmdb_id, list_user_slug_tuple=None, confirm=True):
        """ Add item to library
        Pass optional slug tuple (list, user) to check if in monitored lists
        """
        from tmdbhelper.lib.update.userlist import get_monitor_userlists
        from tmdbhelper.lib.update.library import add_to_library
        if list_user_slug_tuple and list_user_slug_tuple not in get_monitor_userlists():
            return
        if confirm and not Dialog().yesno(get_localized(20444), get_localized(32362)):
            return
        add_to_library(tmdb_type, tmdb_id=tmdb_id)

    """
    overrides
    """

    def get_remove(self):
        if get_infolabel("ListItem.Property(param.owner)") == 'true':
            return True
        return False

    def get_name(self):
        return get_localized(32355) if self.remove else get_localized(32298)

    def get_userlist(self):
        """ Get an existing Trakt list and returns tuple of list and user slug """
        if self.remove:
            return (
                get_infolabel("ListItem.Property(param.list_slug)"),
                get_infolabel("ListItem.Property(param.user_slug)"))
        with BusyDialog():
            list_sync = self.trakt_api.get_list_of_lists('users/me/lists') or []
            list_sync.append({'label': get_localized(32299)})
        x = Dialog().contextmenu([i.get('label') for i in list_sync])
        if x == -1:
            return
        if list_sync[x].get('label') == get_localized(32299):
            return self.add_list()
        return (
            list_sync[x].get('params', {}).get('list_slug'),
            list_sync[x].get('params', {}).get('user_slug'))

    def get_userlist_slug(self):
        if not self.userlist:
            return
        return self.userlist[0]

    def get_userlist_user(self):
        if not self.userlist:
            return
        return self.userlist[1]

    def get_post_response_args(self):
        return ('users', self.userlist_user, 'lists', self.userlist_slug, self.method, )

    def sync(self):
        """ Entry point """
        if self.is_successful_sync:
            self.add_to_library(self.tmdb_type, self.tmdb_id, list_user_slug_tuple=(self.userlist_slug, self.userlist_user, ))
        self.display_dialog()
        self.refresh_containers()
