class TMDbUserListMethods():
    def get_list_of_lists(self):
        if not self.authenticator.authorised_access:
            return []

        response = self.get_authorised_response_json(self.format_authorised_path('account/{account_id}/lists'))

        if not response or not response.get('results'):
            return []

        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath

        tmdb_imagepath = TMDbImagePath()

        def configure_item(i):
            i_name = i.get('name') or ''
            i_list_id = str(i.get('id') or '')
            i_user_id = self.authenticator.authorised_access.get('account_id')
            i_artwork = tmdb_imagepath.get_imagepath_fanart(i.get('backdrop_path'))

            item = {}
            item['label'] = i_name
            item['infolabels'] = {'plot': i.get('description')}
            item['infoproperties'] = {k: v for k, v in i.items() if v and type(v) not in [list, dict]}
            item['art'] = {
                'fanart': i_artwork,
                'poster': i_artwork,
            }
            item['params'] = {
                'info': 'tmdb_v4_list',
                'tmdb_type': 'both',
                'list_name': i_name,
                'list_id': i_list_id,
                'user_id': i_user_id,
                'plugin_category': i_name}
            item['unique_ids'] = {
                'list': i_list_id,
                'user': i_user_id}
            item['context_menu'] = []

            return item

        return [configure_item(i) for i in response['results'] if i]

    def get_basic_list(
        self, path, tmdb_type, key='results', params=None, base_tmdb_type=None, limit=None, filters={},
        sort_key=None, sort_key_order=None, paginated=True, length=None, **kwargs
    ):

        if not self.authenticator.authorised_access:
            return []

        from jurialmunkey.parser import try_int

        length = length or self.page_length
        path = self.format_authorised_path(path)

        def _get_page(page):
            kwargs['page'] = page
            return self.get_authorised_response_json(path, **kwargs)

        def _get_results(response):
            try:
                return response[key] or []
            except (KeyError, TypeError):
                return []

        def _get_response(page, length):
            results = []
            page = try_int(page, fallback=1)
            for x in range(try_int(length, fallback=1)):
                response = _get_page(page + x)
                results += _get_results(response)
                if int(response.get('total_pages') or 1) <= int(response.get('page') or 1):
                    break
            return response, results

        response, results = _get_response(kwargs.get('page'), length=length)
        results = sorted(results, key=lambda i: i.get(sort_key, 0), reverse=sort_key_order != 'asc') if sort_key else results

        add_infoproperties = [('total_pages', response.get('total_pages')), ('total_results', response.get('total_results'))]

        item_tmdb_type = None if tmdb_type == 'both' else tmdb_type

        items = [
            self.mapper.get_info(
                i, item_tmdb_type or i.get('media_type', ''),
                definition=params,
                base_tmdb_type=base_tmdb_type,
                iso_country=self.iso_country,
                add_infoproperties=add_infoproperties)
            for i in results if i]

        if filters:
            from tmdbhelper.lib.items.filters import is_excluded
            items = [i for i in items if not is_excluded(i, **filters)]

        if not paginated:
            return items

        return self.get_paginated_items(items, limit, kwargs['page'], response.get('total_pages'))
