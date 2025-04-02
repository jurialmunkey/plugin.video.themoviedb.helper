class TMDbUserItemMethods():
    def confirm_sync_item(self, response, header, tmdb_type, tmdb_id, season=None, episode=None):
        from xbmcgui import Dialog
        message = f'TMDb ID: {tmdb_id}\nTMDb Type: {tmdb_type}\n'
        if season is not None:
            message = f'{message}Season: {season}\n'
        if episode is not None:
            message = f'{message}Episode: {episode}\n'
        if not response:
            Dialog().ok(header, message + 'Failed!')
            return
        Dialog().ok(header, message + 'Status message: {}'.format(response.get('status_message')))

    @staticmethod
    def refresh_listing(response, remove=False):
        if not remove or not response or not response.get('success'):
            return  # Only refresh if removing from a list as thats when we're likely to be inside the list
        from jurialmunkey.window import get_property
        from tmdbhelper.lib.addon.plugin import executebuiltin
        from tmdbhelper.lib.addon.tmdate import set_timestamp
        get_property('Widgets.Reload', set_property=f'{set_timestamp(0, True)}')
        executebuiltin('Container.Refresh')

    def sync_item(self, route, tmdb_type, tmdb_id, *args, confirmation=True, remove=False, **kwargs):
        from tmdbhelper.lib.addon.plugin import get_localized
        url_path = self.format_authorised_path(f'account/{{account_id}}/{route}')
        postdata = {"media_id": tmdb_id, "media_type": tmdb_type, f"{route}": False if remove else True}
        response = self.get_authorised_response_json_v3(url_path, postdata=postdata, method='json')
        if confirmation:
            self.confirm_sync_item(response, f'{get_localized(1210) if remove else get_localized(15019)} {route}', tmdb_type, tmdb_id)
        self.refresh_listing(response, remove)
        return response

    def sync_list_item(self, list_id, tmdb_type, tmdb_id, *args, confirmation=True, remove=False, list_name=None, **kwargs):
        from tmdbhelper.lib.addon.plugin import get_localized
        url_path = f'list/{list_id}/items'
        postdata = {'items': [{"media_id": tmdb_id, "media_type": tmdb_type}]}
        response = self.get_authorised_response_json(url_path, postdata=postdata, method='json_delete' if remove else 'json')
        if confirmation:
            self.confirm_sync_item(response, f'{list_name or list_id} - {get_localized(1210) if remove else get_localized(15019)}', tmdb_type, tmdb_id)
        self.refresh_listing(response, remove)
        return response

    def check_item_status(self, route, tmdb_type, tmdb_id, *args, **kwargs):
        response = self.get_authorised_response_json_v3(f'{tmdb_type}/{tmdb_id}/account_states')
        if not response:
            return False
        if route not in response:
            return False
        return response[route]

    def check_list_item_status(self, list_id, tmdb_type, tmdb_id, *args, **kwargs):
        url_path = f'list/{list_id}/item_status'
        response = self.get_authorised_response_json(url_path, media_id=tmdb_id, media_type=tmdb_type)
        return response

    def confirm_modify(self, tmdb_type, tmdb_id, list_name, remove=False):
        from xbmcgui import Dialog, DLG_YESNO_YES_BTN
        from tmdbhelper.lib.addon.plugin import get_localized
        if remove:
            header = get_localized(32527).format(list_name)
            message = f'TMDb ID: {tmdb_id}\nTMDb Type: {tmdb_type}\nTMDb List: {list_name}'
            yesbttn = get_localized(1210)
        else:
            header = get_localized(32528).format(list_name)
            message = f'TMDb ID: {tmdb_id}\nTMDb Type: {tmdb_type}\nTMDb List: {list_name}'
            yesbttn = get_localized(15019)

        if Dialog().yesno(header, message, yeslabel=yesbttn, nolabel=get_localized(222), defaultbutton=DLG_YESNO_YES_BTN):
            return True

    def modify_list(self, tmdb_type, tmdb_id, *args, confirmation=True, **kwargs):
        from xbmcgui import Dialog
        from tmdbhelper.lib.addon.plugin import get_localized

        u_lists = self.get_list_of_lists()
        d_items = [i['label'] for i in u_lists]

        x = Dialog().select(get_localized(32524), d_items)
        if x == -1:
            return

        list_id = u_lists[x]['params']['list_id']
        list_name = u_lists[x]['params']['list_name']

        remove = True if self.check_list_item_status(list_id, tmdb_type, tmdb_id) else False
        if not self.confirm_modify(tmdb_type=tmdb_type, tmdb_id=tmdb_id, list_name=list_name, remove=remove):
            return

        return self.sync_list_item(list_id, tmdb_type, tmdb_id, *args, confirmation=confirmation, remove=remove, list_name=list_name, **kwargs)

    def add_favorite(self, tmdb_type, tmdb_id, *args, confirmation=True, **kwargs):
        return self.sync_item('favorite', tmdb_type, tmdb_id, *args, confirmation=confirmation, **kwargs)

    def add_watchlist(self, tmdb_type, tmdb_id, *args, confirmation=True, **kwargs):
        return self.sync_item('watchlist', tmdb_type, tmdb_id, *args, confirmation=confirmation, **kwargs)

    def del_favorite(self, tmdb_type, tmdb_id, *args, confirmation=True, **kwargs):
        return self.sync_item('favorite', tmdb_type, tmdb_id, *args, confirmation=confirmation, remove=True, **kwargs)

    def del_watchlist(self, tmdb_type, tmdb_id, *args, confirmation=True, **kwargs):
        return self.sync_item('watchlist', tmdb_type, tmdb_id, *args, confirmation=confirmation, remove=True, **kwargs)

    def modify_watchlist(self, tmdb_type, tmdb_id, *args, confirmation=True, **kwargs):
        from tmdbhelper.lib.addon.plugin import get_localized
        remove = True if self.check_item_status('watchlist', tmdb_type, tmdb_id) else False
        if not self.confirm_modify(tmdb_type=tmdb_type, tmdb_id=tmdb_id, list_name=get_localized(32193), remove=remove):
            return
        return self.sync_item('watchlist', tmdb_type, tmdb_id, *args, confirmation=confirmation, remove=remove, **kwargs)

    def modify_favorite(self, tmdb_type, tmdb_id, *args, confirmation=True, **kwargs):
        from tmdbhelper.lib.addon.plugin import get_localized
        remove = True if self.check_item_status('favorite', tmdb_type, tmdb_id) else False
        if not self.confirm_modify(tmdb_type=tmdb_type, tmdb_id=tmdb_id, list_name=get_localized(1036), remove=remove):
            return
        return self.sync_item('favorite', tmdb_type, tmdb_id, *args, confirmation=confirmation, remove=remove, **kwargs)
