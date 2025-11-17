from tmdbhelper.lib.addon.plugin import get_setting, get_localized, set_setting
from jurialmunkey.ftools import cached_property


# CHECK : library_autoupdate


class MonitorUserLists:

    separator = ' | '

    @cached_property
    def monitored_lists(self):
        list_slugs = (get_setting('monitor_userlist', 'str') or '').split(self.separator)
        user_slugs = (get_setting('monitor_userslug', 'str') or '').split(self.separator)
        return list(zip(list_slugs, user_slugs))

    @cached_property
    def lists_trakt_watchlist(self):
        return [
            {
                'label': f'{get_localized(32193)} {get_localized(20342)}',
                'params': {'user_slug': 'me', 'list_slug': 'watchlist/movies'}
            },
            {
                'label': f'{get_localized(32193)} {get_localized(20343)}',
                'params': {'user_slug': 'me', 'list_slug': 'watchlist/shows'}
            }
        ]

    @cached_property
    def lists_trakt_static_owned(self):
        from tmdbhelper.lib.items.directories.trakt.lists_static import ListTraktStaticOwned
        return ListTraktStaticOwned(-1, '').get_items(tmdb_type='both') or []

    @cached_property
    def lists_trakt_static_liked(self):
        from tmdbhelper.lib.items.directories.trakt.lists_static import ListTraktStaticLiked
        return ListTraktStaticLiked(-1, '').get_items(tmdb_type='both') or []

    @cached_property
    def lists_mdblist_user(self):
        if not get_setting('mdblist_apikey', 'str'):
            return []
        from tmdbhelper.lib.items.directories.mdblist.lists_lists import ListMDbListListsUser
        return ListMDbListListsUser(-1, '').get_items() or []

    @cached_property
    def lists_mdblist_formatted(self):
        return [j for j in (self.format_mdblist_item(i) for i in self.lists_mdblist_user) if j]

    @staticmethod
    def format_mdblist_item(i):
        try:
            i['params']['user_slug'] = '__api_mdblist__'
            i['params']['list_slug'] = str(i['params']['list_id'])
            i['label'] = f'MDbList: {i.get("label")}'
            return i
        except (KeyError, TypeError):
            return

    @cached_property
    def user_lists(self):
        user_lists = []
        user_lists += self.lists_trakt_watchlist
        user_lists += self.lists_trakt_static_owned
        user_lists += self.lists_trakt_static_liked
        user_lists += self.lists_mdblist_formatted
        return user_lists

    @cached_property
    def dialog_list(self):
        return [i['label'] for i in self.user_lists]

    @staticmethod
    def get_item_tuple(i):
        try:
            return (i['params']['list_slug'], i['params']['user_slug'])
        except (KeyError, TypeError):
            return

    def get_item_tuple_index(self, x):
        return self.get_item_tuple(self.user_lists[x])

    @cached_property
    def dialog_preselected(self):
        return [
            x for x, i in enumerate(self.user_lists)
            if self.get_item_tuple(i) in self.monitored_lists
        ]

    @cached_property
    def multiselect_indices(self):
        from xbmcgui import Dialog
        return Dialog().multiselect(get_localized(32312), self.dialog_list, preselect=self.dialog_preselected)

    @cached_property
    def multiselect_tuples(self):
        # if get_userlist(user_slug, list_slug, confirm=50):  # TODO CHECK NOT OVER
        return [i for i in (self.get_item_tuple_index(x) for x in self.multiselect_indices) if i and self.check_limit(*i)]

    @staticmethod
    def check_limit(list_slug, user_slug):
        from tmdbhelper.lib.update.builder.userlist import LibraryBuilderUserList
        library = LibraryBuilderUserList()
        library.confirm = 50
        library.list_slug = list_slug
        library.user_slug = user_slug
        if library.request and library.is_confirmed:
            return True
        return False

    def multiselect_update(self):
        list_slugs, user_slugs = zip(*self.multiselect_tuples)
        list_slugs = self.separator.join(list(list_slugs))
        user_slugs = self.separator.join(list(user_slugs))
        set_setting('monitor_userlist', list_slugs, 'str')
        set_setting('monitor_userslug', user_slugs, 'str')
        self.library_update()

    def library_update(self):
        from xbmcgui import Dialog
        if not Dialog().yesno(get_localized(653), get_localized(32132)):
            return
        MonitorUserLists().library_autoupdate()

    def library_autoupdate(self, forced=False):
        # Log message
        from tmdbhelper.lib.addon.logger import kodi_log
        kodi_log(u'UPDATING LIBRARY', 1)

        # Notify user
        from xbmcgui import Dialog
        Dialog().notification('TMDbHelper', f'{get_localized(32167)}...')

        # Clean library if forcing to make sure dead entries removed
        from xbmc import executebuiltin
        executebuiltin('CleanLibrary("video")', True) if forced else None

        # Update monitored lists and NFO folders
        from tmdbhelper.lib.update.builder.update import LibraryBuilderUpdate
        from tmdbhelper.lib.update.builder.userlist import LibraryBuilderUserList
        with LibraryBuilderUserList() as parent_library:
            parent_library.forced = forced
            parent_library.confirm = 0

            for list_slug, user_slug in self.monitored_lists:
                library = LibraryBuilderUserList()
                library = parent_library.get_builder(library)
                library.confirm = 0
                library.create(user_slug=user_slug, list_slug=list_slug)

            library = LibraryBuilderUpdate()
            library = parent_library.get_builder(library)
            library.confirm = 0
            library.create()
