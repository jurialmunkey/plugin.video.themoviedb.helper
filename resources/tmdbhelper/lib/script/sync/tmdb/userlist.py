from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.script.sync.tmdb.item import ItemSync as TMDbItemSync


class ItemUserListChoice:

    label = ''
    label2 = ''
    infolabels = {}
    infoproperties = {}
    art = {}
    params = {}
    unique_ids = {}

    def __init__(self, item_user_list):
        self.item_user_list = item_user_list

    @property
    def tmdb_imagepath(self):
        return self.item_user_list.tmdb_imagepath

    @property
    def tmdb_user_api(self):
        return self.item_user_list.tmdb_user_api

    @cached_property
    def item(self):
        return {
            'label': self.label,
            'label2': self.label2,
            'infolabels': self.infolabels,
            'infoproperties': self.infoproperties,
            'art': self.art,
            'params': self.params,
            'unique_ids': self.unique_ids,
        }

    @cached_property
    def listitem(self):
        from tmdbhelper.lib.items.listitem import ListItem
        return ListItem(**self.item).get_listitem()


class ItemUserListChoiceNew(ItemUserListChoice):
    label = get_localized(32299)
    remove = False

    @cached_property
    def list_name(self):
        from xbmcgui import Dialog
        return Dialog().input('List name')

    @cached_property
    def list_description(self):
        from xbmcgui import Dialog
        return Dialog().input('List description')

    @cached_property
    def list_public(self):
        from xbmcgui import Dialog
        return 'true' if Dialog().yesno(
            get_localized(32137),
            get_localized(32136),
            yeslabel=get_localized(29935),
            nolabel=get_localized(32135)
        ) else 'false'

    @cached_property
    def list_id(self):
        if not self.post_response:
            return
        return self.post_response['id']

    @cached_property
    def post_response_data(self):
        if not self.list_name:
            return {}
        post_response_data = {
            'name': self.list_name,
            'description': self.list_description,
            'iso_3166_1': 'US',
            'iso_639_1': 'en',
            'public': self.list_public
        }
        return post_response_data

    @cached_property
    def post_response(self):
        if not self.post_response_data:
            return
        self.label = f'{self.label} {self.list_name}'
        return self.tmdb_user_api.get_authorised_response_json(
            'list',
            postdata=self.post_response_data,
            method='json')


class ItemUserListChoiceYours(ItemUserListChoice):
    def __init__(self, meta, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = meta

    @staticmethod
    def get_object_key(obj, key):
        try:
            return obj[key]
        except (KeyError, AttributeError, TypeError, IndexError):
            return

    @cached_property
    def remove(self):
        url_path = f'list/{self.list_id}/item_status'
        response = self.tmdb_user_api.get_authorised_response_json(
            url_path,
            media_id=self.item_user_list.tmdb_id,
            media_type=self.item_user_list.tmdb_type
        )
        return bool(response)

    @cached_property
    def name(self):
        return self.get_object_key(self.meta, 'name')

    @cached_property
    def label(self):
        label = get_localized(32527) if self.remove else get_localized(32528)
        return label.format(self.name)

    @cached_property
    def label2(self):
        return ' | '.join(tuple((
            i for i in (
                self.number_of_items,
                self.plot,
            ) if i
        )))

    @cached_property
    def account_id(self):
        return self.get_object_key(self.meta, 'account_object_id')

    @cached_property
    def number_of_items(self):
        number_of_items = self.get_object_key(self.meta, 'number_of_items')
        return f'{number_of_items} {get_localized(32134)}' if number_of_items else None

    @cached_property
    def list_id(self):
        return self.get_object_key(self.meta, 'id')

    @cached_property
    def plot(self):
        return self.get_object_key(self.meta, 'description')

    @cached_property
    def fanart(self):
        fanart = self.get_object_key(self.meta, 'backdrop_path')
        fanart = self.tmdb_imagepath.get_imagepath_fanart(fanart)
        return fanart

    @cached_property
    def infolabels(self):
        return {
            'plot': self.plot
        }

    @cached_property
    def infoproperties(self):
        infoproperties = {
            k: v for k, v in self.meta.items()
            if v and not isinstance(v, (list, dict))
        }
        return infoproperties

    @cached_property
    def art(self):
        return {
            'fanart': self.fanart,
            'thumb': self.fanart,
        }

    @cached_property
    def params(self):
        return {
            'info': 'tmdb_v4_list',
            'tmdb_type': 'both',
            'list_name': self.name,
            'list_id': self.list_id,
            'user_id': self.account_id,
            'plugin_category': self.name,
        }

    @cached_property
    def unique_ids(self):
        return {
            'list': self.list_id,
            'user': self.account_id,
        }


class ItemUserList(TMDbItemSync):
    localized_name_add = 32298
    localized_name_rem = 32355

    @cached_property
    def tmdb_imagepath(self):
        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
        return TMDbImagePath()

    @cached_property
    def user_lists_response(self):
        if not self.tmdb_user_api.authenticator.authorised_access:
            return
        path = self.tmdb_user_api.format_authorised_path('account/{account_id}/lists')
        return self.tmdb_user_api.get_authorised_response_json(path)

    @cached_property
    def user_lists_results(self):
        try:
            return self.user_lists_response['results'] or []
        except (KeyError, TypeError, AttributeError):
            return []

    @cached_property
    def user_lists(self):
        user_lists = [
            ItemUserListChoiceYours(i, self)
            for i in self.user_lists_results if i
        ]
        if not user_lists:
            return []
        user_lists.append(ItemUserListChoiceNew(self))
        return user_lists

    @cached_property
    def post_response_data(self):
        return {
            'items': [{
                "media_id": self.tmdb_id,
                "media_type": self.tmdb_type
            }]
        }

    @cached_property
    def post_response_path(self):
        return f'list/{self.choice.list_id}/items'

    @cached_property
    def post_response_method(self):
        return 'json_delete' if self.choice.remove else 'json'

    @cached_property
    def choice(self):
        from xbmcgui import Dialog
        x = Dialog().select(
            get_localized(32524),
            [i.listitem for i in self.user_lists],
            useDetails=True)
        if x == -1:
            return
        if not self.user_lists[x].list_id:
            return
        self.name = self.user_lists[x].label  # Update dialog confirmation name
        return self.user_lists[x]

    """
    overrides
    """

    @cached_property
    def is_available(self):
        """ Whether option is show in menu """
        return bool(self.user_lists)  # Check we have lists to add

    @busy_decorator
    def get_sync_response(self):
        """ Called after user selects choice """
        if not self.choice:
            return
        return self.tmdb_user_api.get_authorised_response_json(
            self.post_response_path,
            postdata=self.post_response_data,
            method=self.post_response_method)

    def get_sync_value(self):
        return
