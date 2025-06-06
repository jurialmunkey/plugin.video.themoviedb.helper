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
