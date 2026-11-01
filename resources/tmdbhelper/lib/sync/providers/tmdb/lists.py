class TMDbUserLists:
    """Account list requests shared by browsing, actions, sync, and monitoring."""

    def __init__(self, provider):
        self.provider = provider

    def format_path(self, path):
        return self.provider.user_api.format_authorised_path(path)

    def get_account_path(self, tmdb_type, list_type):
        return self.format_path(f'account/{{account_id}}/{tmdb_type}/{list_type}')

    def get_response(self, path, page=1, **kwargs):
        if not self.provider.is_user_authorized:
            return
        response = self.provider.user_api.get_authorised_response_json(path, page=page, **kwargs)
        if not response or response.get('success') is False:
            return
        if response['page'] != page:
            raise ValueError(f'TMDb list returned page {response["page"]} instead of {page}')
        return response

    def get_items(self, path, **kwargs):
        items = []
        page = 1
        while True:
            response = self.get_response(path, page=page, **kwargs)
            if response is None:
                return
            items.extend(response['results'])
            if page >= response['total_pages']:
                return items
            page += 1

    def get_account_items(self, tmdb_type, list_type):
        if not self.provider.is_user_authorized:
            return
        return self.get_items(self.get_account_path(tmdb_type, list_type), sort_by='created_at.desc')

    def get_owned_lists(self):
        if not self.provider.is_user_authorized:
            return
        return self.get_items(self.format_path('account/{account_id}/lists'))

    def get_list_items(self, list_id):
        return self.get_items(f'list/{list_id}')
