from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.script.sync.item import ItemSync as BasicItemSync


class ItemSync(BasicItemSync):

    tmdb_list_type = None
    convert_episodes = True
    convert_seasons = True

    """
    tmdb_user_api
    """

    @cached_property
    def tmdb_user_api(self):
        return self.get_tmdb_user_api()

    def get_tmdb_user_api(self):
        from tmdbhelper.lib.api.tmdb.users import TMDbUser
        return TMDbUser()

    """
    account_states
    """

    @cached_property
    def account_states(self):
        return self.get_account_states()

    def get_account_states(self):
        request_args = (self.tmdb_type, self.tmdb_id, 'account_states')
        return self.tmdb_user_api.get_authorised_response_json_v3(*request_args)

    """
    post_response_path
    """

    @cached_property
    def post_response_path(self):
        return self.get_post_response_path()

    def get_post_response_path(self):
        request_path = f'account/{{account_id}}/{self.tmdb_list_type}'
        return self.tmdb_user_api.format_authorised_path(request_path)

    """
    post_response_data
    """

    @cached_property
    def post_response_data(self):
        return self.get_post_response_data()

    def get_post_response_data(self):
        post_response_data = {
            "media_id": self.tmdb_id,
            "media_type": self.tmdb_type,
        }
        post_response_data[self.tmdb_list_type] = bool(not self.remove)
        return post_response_data

    """
    overrides
    """

    def get_status_code_message(self):
        try:
            return self.sync_response['status_message']
        except (KeyError, TypeError, AttributeError):
            return 'Undefined error'

    def get_status_code(self):
        """https://www.themoviedb.org/documentation/api/status-codes"""
        try:
            status_code = self.sync_response['status_code']
        except (KeyError, TypeError, AttributeError):
            return
        if status_code in (1, 12, 13):
            return 200
        return status_code

    @busy_decorator
    def get_sync_response(self):
        """ Called after user selects choice """
        return self.tmdb_user_api.get_authorised_response_json_v3(
            self.post_response_path,
            postdata=self.post_response_data,
            method='json'
        )

    def get_sync_value(self):
        if not self.account_states:
            return False
        if self.tmdb_list_type not in self.account_states:
            return False
        return self.account_states[self.tmdb_list_type]
