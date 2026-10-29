from threading import local


class CalendarPageFetcher:
    """Reuse an independent TMDb client on each page-pool worker."""

    def __init__(self, discover, date):
        self.discover = discover
        self.date = date
        self.clients = local()

    def get_api(self):
        try:
            return self.clients.api
        except AttributeError:
            from tmdbhelper.lib.api.tmdb.api import TMDb
            self.clients.api = TMDb(
                api_key=self.discover.tmdb_api.api_key,
                language=self.discover.tmdb_api.language)
            return self.clients.api

    def get_page(self, page):
        response = self.discover.get_response(self.date, page, tmdb_api=self.get_api())
        return {item['id'] for item in response['results']}
