class TableDailyExport:
    conditions = None

    def __init__(self, parent):
        self.parent = parent

    @staticmethod
    def get_downloaded_list(export_list):
        from json import loads as json_loads
        from tmdbhelper.lib.files.downloader import Downloader
        from tmdbhelper.lib.addon.tmdate import get_datetime_utcnow, get_timedelta
        datestamp = get_datetime_utcnow() - get_timedelta(days=1)
        datestamp = datestamp.strftime("%m_%d_%Y")
        download_url = f'https://files.tmdb.org/p/exports/{export_list}_ids_{datestamp}.json.gz'
        return [json_loads(i) for i in Downloader(download_url=download_url).get_gzip_text().splitlines()]

    @staticmethod
    def configure_list(data):
        return [{k: i[k] for k in i.keys()} for i in data] if data else []

    def get_cached(self):
        return self.parent.get_cached_values(self.table, self.keys, self.configure_list, conditions=self.conditions)

    def set_cached(self):
        data = self.get_downloaded_list(self.export_list)
        values = [tuple((i[x] for x in self.keys)) for i in data] if data else None
        if not values:
            return
        self.parent.set_cached_values(self.table, self.keys, values)
        return self.get_cached()
