from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.plugin import convert_type, get_localized, get_setting
from tmdbhelper.lib.items.container import ContainerDirectory


class ListCalendar(ContainerDirectory):
    def _get_calendar_items(self, info, startdate, days, page=None, kodi_db=None, endpoint=None, user=True, **kwargs):
        from tmdbhelper.lib.addon.tmdate import get_calendar_name

        items = self.trakt_api.get_calendar_episodes_list(
            try_int(startdate),
            try_int(days),
            kodi_db=kodi_db,
            user=user,
            page=page,
            endpoint=endpoint)

        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = 'episodes'
        self.plugin_category = get_calendar_name(startdate=try_int(startdate), days=try_int(days))
        self.thumb_override = get_setting('calendar_art', 'int')
        return items

    def get_items(self, **kwargs):
        kwargs['user'] = kwargs.pop('user', '').lower() != 'false'
        return self._get_calendar_items(**kwargs)


class ListLibraryCalendar(ListCalendar):
    def get_items(self, **kwargs):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        kodi_db = get_kodi_library('tv')
        if not kodi_db:
            return
        return self._get_calendar_items(kodi_db=kodi_db, user=False, **kwargs)


class ListGenres(ContainerDirectory):
    def get_items(self, info, tmdb_type, **kwargs):
        items = self.trakt_api.get_list_of_genres(convert_type(tmdb_type, 'trakt'))
        self.plugin_category = get_localized(135)
        return items


class ListSortBy(ContainerDirectory):
    def get_items(self, info, **kwargs):
        from tmdbhelper.lib.api.trakt.sorting import get_sort_methods
        from tmdbhelper.lib.api.mapping import get_empty_item

        def _listsortby_item(i, **params):
            item = get_empty_item()
            item['label'] = item['infolabels']['title'] = f'{params.get("list_name")} - {i["name"]}'
            item['params'] = params
            item['params'].update(i['params'])
            return item

        kwargs['info'] = kwargs.pop('parent_info', None)
        items = get_sort_methods(kwargs['info'])
        items = [_listsortby_item(i, **kwargs) for i in items]
        return items
