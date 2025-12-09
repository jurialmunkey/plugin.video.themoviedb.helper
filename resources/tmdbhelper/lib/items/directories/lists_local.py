from jurialmunkey.ftools import cached_property


class UncachedListLocalData:
    def __init__(self, response, page=1, limit=20):
        self.response = response
        self.limit = limit
        self.page = page

    @cached_property
    def item_count(self):
        return len(self.response)

    @cached_property
    def page_count(self):
        return (self.item_count + self.limit - 1) // self.limit  # Ceiling division

    @cached_property
    def item_a(self):
        return max(((self.page - 1) * self.limit), 0)

    @cached_property
    def item_z(self):
        return min((self.page * self.limit), self.item_count)

    @cached_property
    def json(self):
        return self.response[self.item_a:self.item_z]

    @cached_property
    def data(self):
        return {
            'json': self.json,
            'headers': {
                'x-pagination-page-count': self.page_count,
                'x-pagination-item-count': self.item_count,
            }
        } if self.response else {}
