from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.plugin import convert_type, PLUGINPATH, get_plugin_category, get_localized, get_setting, encode_url
from tmdbhelper.lib.items.container import ContainerDirectory


class ListComments(ContainerDirectory):
    def get_items(self, info, tmdb_type, tmdb_id, sort=None, **kwargs):
        """ Get a mix of watchlisted and inprogress """
        from tmdbhelper.lib.api.mapping import get_empty_item

        if tmdb_type not in ['movie', 'tv']:
            return
        trakt_type = convert_type(tmdb_type, 'trakt')
        slug = self.trakt_api.get_id(tmdb_id, 'tmdb', trakt_type, 'slug')
        items = self.trakt_api.get_request_sc(f'{trakt_type}s', slug, 'comments', sort, limit=50)

        def _map_item(i):
            item = get_empty_item()
            plot = i.get('comment') or ''
            rate = i.get('user_stats', {}).get('rating')
            date = i.get('created_at')[:10]
            plot = f'{plot}\n{get_localized(563)} {rate}/10' if rate else plot
            plot = f'{plot}\n{date}'
            item['infolabels']['plot'] = plot
            item['label'] = item['infolabels']['title'] = i.get('user', {}).get('name') or i.get('user', {}).get('username')
            item['infolabels']['premiered'] = date
            item['infolabels']['rating'] = rate
            item['params'] = {'comment_id': i.get('id'), 'parent_id': i.get('parent_id'), 'user_slug': i.get('user', {}).get('ids', {}).get('slug')}
            return item

        items = [_map_item(i) for i in items if i]

        return items


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
            for k, v in i['params'].items():
                item['params'][k] = v
            return item

        kwargs['info'] = kwargs.pop('parent_info', None)
        items = get_sort_methods(kwargs['info'])
        items = [_listsortby_item(i, **kwargs) for i in items]
        return items
