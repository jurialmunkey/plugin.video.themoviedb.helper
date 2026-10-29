from tmdbhelper.lib.script.actions.trakt.item import ItemAction
from tmdbhelper.lib.addon.plugin import get_infolabel, get_localized
from tmdbhelper.lib.addon.dialog import busy_decorator
from jurialmunkey.ftools import cached_property
from xbmcgui import Dialog


class ItemUserList(ItemAction):
    preconfigured = True
    sync_url = 'items'

    @cached_property
    def userlist(self):
        return self.get_userlist()

    @cached_property
    def userlist_slug(self):
        return self.get_userlist_slug()

    @property
    def userlist_user(self):
        return self.get_userlist_user()

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

        from tmdbhelper.lib.update.monitor import MonitorUserLists
        if list_user_slug_tuple and not MonitorUserLists().is_monitored(*list_user_slug_tuple):
            return

        if confirm and not Dialog().yesno(get_localized(20444), get_localized(32362)):
            return

        from tmdbhelper.lib.script.method.library import add_to_library
        add_to_library(tmdb_type, tmdb_id=tmdb_id)

    """
    overrides
    """

    def get_remove(self):
        return (get_infolabel("ListItem.Property(param.info)") == 'trakt_userlist'
                and get_infolabel("ListItem.Property(param.owner)") == 'true')

    def get_name(self):
        return get_localized(32355) if self.remove else get_localized(32298)

    @cached_property
    def users_lists(self):
        return self.get_users_lists()

    @busy_decorator
    def get_users_lists(self):
        from tmdbhelper.lib.sync.providers.directories import get_provider_list_container
        container_class = get_provider_list_container('trakt_mylists', 'trakt')
        if container_class is None:
            return []
        container = container_class(-1, '')
        container.trakt_api = self.trakt_api
        users_lists = container.get_items(tmdb_type='both') or []
        users_lists.append({'label': get_localized(32299)})
        return users_lists

    @cached_property
    def users_lists_choices(self):
        return [i.get('label') for i in self.users_lists]

    def get_userlist(self):
        """ Get an existing Trakt list and returns tuple of list and user slug """
        if self.remove:
            return (
                get_infolabel("ListItem.Property(param.list_slug)"),
                get_infolabel("ListItem.Property(param.user_slug)"))
        x = Dialog().contextmenu(self.users_lists_choices)
        if x == -1:
            return
        if self.users_lists[x].get('label') == get_localized(32299):
            return self.add_list()
        return (
            self.users_lists[x].get('params', {}).get('list_slug'),
            self.users_lists[x].get('params', {}).get('user_slug'))

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


class ItemLikeList:
    def __init__(self, user_slug, list_slug, confirmation=False, delete=False):
        self.user_slug = user_slug
        self.list_slug = list_slug
        self.confirmation = confirmation
        self.delete = delete

    @cached_property
    def trakt_api(self):
        return self.get_trakt_api()

    def get_trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    @cached_property
    def response(self):
        return self.get_response()

    def get_response(self):
        request = self.trakt_api.delete_response if self.delete else self.trakt_api.post_response
        return request('users', self.user_slug, 'lists', self.list_slug, 'like')

    @cached_property
    def is_successful(self):
        return self.get_is_successful()

    def get_is_successful(self):
        return self.response is not None and self.response.status_code == 204

    @cached_property
    def dialog_message(self):
        return self.get_dialog_message()

    def get_dialog_message(self):
        affix = get_localized(32320 if self.delete else 32321)
        body = [
            get_localized(32316 if self.is_successful else 32317).format(affix),
            get_localized(32168).format(self.list_slug, self.user_slug),
        ]
        if not self.is_successful and self.response is not None:
            body.append(get_localized(32318).format(self.response.status_code))
        return '\n'.join(body)

    def sync(self):
        successful = self.is_successful
        if self.confirmation:
            Dialog().ok(get_localized(32315), self.dialog_message)
        if successful:
            return self.response
