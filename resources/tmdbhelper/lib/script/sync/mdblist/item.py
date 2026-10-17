from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.script.sync.request import ItemSync as BasicItemSync


class ItemSync(BasicItemSync):
    activity_methods = ()

    @cached_property
    def mdblist_api(self):
        return self.get_mdblist_api()

    def get_mdblist_api(self):
        from tmdbhelper.lib.api.mdblist.api import MDbListAPI
        return MDbListAPI()

    @cached_property
    def is_available(self):
        return self.get_is_available()

    def get_is_available(self):
        return bool(self.mdblist_api)

    def get_name(self):
        return f'{super().get_name()} (MDbList)'

    def get_self(self):
        if not self.is_available:
            return
        return super().get_self()

    def get_sync_item(self):
        item = {'ids': {'tmdb': try_int(self.tmdb_id)}}
        if self.season is not None:
            season = {'number': try_int(self.season)}
            if self.episode is not None:
                season['episodes'] = [{'number': try_int(self.episode)}]
            item['seasons'] = [season]
        return item

    def get_post_response_type(self):
        return f'{self.base_trakt_type}s'

    def get_post_response_args(self):
        return (self.method, )

    @busy_decorator
    def get_sync_response(self):
        if not self.is_available:
            return
        path = self.mdblist_api.get_request_url(*self.post_response_args)
        return self.mdblist_api.get_api_request(
            path,
            postdata=self.post_response_data,
            headers=self.mdblist_api.headers,
            method='json'
        )

    @cached_property
    def response_data(self):
        return self.get_response_data()

    def get_response_data(self):
        if self.sync_response is None or self.status_code == 204:
            return {}
        try:
            return self.sync_response.json()
        except ValueError:
            return {'error': 'Invalid JSON response'}

    def get_is_successful_sync(self):
        if not super().get_is_successful_sync():
            return False
        if self.status_code == 204:
            return True
        if not self.response_data:
            return False
        return not (
            self.response_data.get('error')
            or self.response_data.get('errors')
            or any(self.response_data.get('not_found', {}).values())
        )

    def get_status_code_message(self):
        if self.response_data.get('error') or self.response_data.get('errors'):
            return f'MDbList: {self.response_data.get("error") or self.response_data["errors"]}'
        if any(self.response_data.get('not_found', {}).values()):
            return 'MDbList: not_found'
        return super().get_status_code_message()

    def invalidate_activity(self, method, item_type=None):
        item_id = f'{item_type or self.base_trakt_type}.{method}'
        self.syncdata.cache.del_item(table='lactivities', item_id=item_id)
        self.syncdata.window.get_property(f'syncdecorators.timerlock.sync_data.{item_id}', clear_property=True)

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        for method in self.activity_methods:
            self.invalidate_activity(method)
        self.syncdata.reset_lastactivities()
