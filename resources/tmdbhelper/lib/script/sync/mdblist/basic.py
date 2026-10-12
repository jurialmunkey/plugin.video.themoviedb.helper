from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.script.sync.trakt.basic import ItemDropped as TraktItemDropped


class ItemDropped(TraktItemDropped):
    trakt_sync_url = 'sync/dropped'

    @cached_property
    def mdblist_api(self):
        from tmdbhelper.lib.api.mdblist.api import MDbListAPI
        return MDbListAPI()

    @cached_property
    def is_available(self):
        return bool(self.mdblist_api)

    def get_sync_item(self):
        return {'ids': {'tmdb': try_int(self.tmdb_id)}}

    def get_post_response_args(self):
        return (self.method, )

    @busy_decorator
    def get_sync_response(self):
        if not self.mdblist_api:
            return
        path = self.mdblist_api.get_request_url(*self.post_response_args)
        return self.mdblist_api.get_api_request(
            path,
            postdata=self.post_response_data,
            headers=self.mdblist_api.headers,
            method='json'
        )

    def get_is_successful_sync(self):
        if not super().get_is_successful_sync():
            return False
        try:
            return not self.sync_response.json()['not_found']['shows']
        except (AttributeError, KeyError, TypeError, ValueError):
            return False

    def get_status_code_message(self):
        try:
            if self.sync_response.json()['not_found']['shows']:
                return 'MDbList: not_found'
        except (AttributeError, KeyError, TypeError, ValueError):
            pass
        return super().get_status_code_message()

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        for method in ('sync/dropped', 'upnext', 'all_next_episodes', 'sync/watched'):
            self.syncdata.cache.del_item(table='lactivities', item_id=f'show.{method}')
            self.syncdata.window.get_property(f'syncdecorators.timerlock.sync_data.show.{method}', clear_property=True)
        self.syncdata.reset_lastactivities()
        self.delete_listdata()
