from xbmc import Monitor
from jurialmunkey.ftools import cached_property


class MDbListSyncPage:
    pagination_key = 'cursor'
    progress_message = 'Retrieving next_cursor'

    def __init__(self, response, get_items):
        self.response = response
        self.get_data_list_by_type = get_items

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        return self.response.json()

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        items = self.get_data_list_by_type(self.data)
        if not isinstance(items, list):
            raise ValueError('MDbList sync page must contain a list of items')
        return items

    @cached_property
    def pagination(self):
        return self.get_pagination()

    def get_pagination(self):
        return self.data.get('pagination', {})

    @cached_property
    def has_more(self):
        return self.get_has_more()

    def get_has_more(self):
        return self.pagination.get('has_more', self.response.headers.get('x-has-more', '').lower() == 'true')

    @cached_property
    def next_cursor(self):
        return self.get_next_cursor()

    def get_next_cursor(self):
        return self.pagination.get('next_cursor') or self.get_header_next_cursor(self.response)

    @staticmethod
    def get_header_next_cursor(response):
        try:
            if response.headers['x-has-more']:
                return response.headers['x-next-cursor']
        except KeyError:
            return

    @cached_property
    def has_next_page(self):
        return self.get_has_next_page()

    def get_has_next_page(self):
        if not self.next_cursor and self.has_more:
            raise ValueError('MDbList sync page is missing the next cursor')
        return bool(self.next_cursor)

    def get_next_page(self, **kwargs):
        return self.next_cursor


class MDbListSyncPageOffset(MDbListSyncPage):
    pagination_key = 'offset'
    progress_message = 'Retrieving next page'

    def get_has_more(self):
        return self.pagination.get('has_more', False)

    def get_has_next_page(self):
        return self.has_more

    def get_next_page(self, offset=0, **kwargs):
        return offset + len(self.items) if self.has_next_page else None


class MDbListSyncCollection:
    progress_message = 'Retrieving next_cursor'

    def __init__(self, instance_datatype, *args, **kwargs):
        self.instance_datatype = instance_datatype
        self.args = args
        self.kwargs = self.get_request_kwargs(**kwargs)

    @cached_property
    def data(self):
        return self.get_data()

    def get_request_kwargs(self, **kwargs):
        return kwargs

    def get_response_sync_data(self):
        return self.instance_datatype.get_response_sync_data(*self.args, **self.kwargs)

    def get_response_items(self, response):
        if response is None:
            return

        try:
            data = self.instance_datatype.get_data_list_by_type(response.json())
        except AttributeError:
            return

        if not isinstance(data, list):
            return
        return data

    def update_page_progress(self):
        dialog = self.instance_datatype.dialog_progress_bg
        dialog.update(dialog.increment(), message=self.progress_message)

    def extend_data(self, data, response):
        next_cursor = MDbListSyncPage.get_header_next_cursor(response)
        if not next_cursor:
            return data

        self.update_page_progress()
        kwargs = dict(self.kwargs, cursor=next_cursor)
        collection = self.__class__(self.instance_datatype, *self.args, **kwargs)
        data.extend(collection.data or [])
        return data

    def get_data(self):
        response = self.get_response_sync_data()
        data = self.get_response_items(response)
        if data is None:
            return
        return self.extend_data(data, response)


class MDbListSyncCollectionSnapshot(MDbListSyncCollection):
    sync_page_class = MDbListSyncPage

    def __init__(self, instance_datatype, *args, **kwargs):
        super().__init__(instance_datatype, *args, **kwargs)
        self.monitor = Monitor()
        self.pages = set()

    @property
    def progress_message(self):
        return self.sync_page_class.progress_message

    def get_response_page(self, response):
        if response is None or response.status_code != 200:
            return

        page = self.sync_page_class(response, self.instance_datatype.get_data_list_by_type)
        if not page.items and page.has_next_page:
            return
        return page

    def get_response_sync_page(self):
        response = self.get_response_sync_data()
        return self.get_response_page(response)

    def set_next_page(self, page):
        next_page = page.get_next_page(**self.kwargs)
        if next_page in self.pages:
            return False

        self.pages.add(next_page)
        self.kwargs[self.sync_page_class.pagination_key] = next_page
        self.update_page_progress()
        return True

    def get_data(self):
        data = []
        while not self.monitor.abortRequested():
            page = self.get_response_sync_page()
            if page is None:
                return

            data.extend(page.items)
            if not page.has_next_page:
                return data
            if not self.set_next_page(page):
                return


class MDbListSyncCollectionOffset(MDbListSyncCollectionSnapshot):
    sync_page_class = MDbListSyncPageOffset

    def get_request_kwargs(self, offset=0, **kwargs):
        return dict(kwargs, offset=offset)
