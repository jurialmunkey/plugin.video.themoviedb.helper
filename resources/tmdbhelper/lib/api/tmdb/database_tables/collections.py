class TableDailyExport:
    conditions = None

    def __init__(self, parent):
        self.parent = parent

    @staticmethod
    def get_downloaded_list(export_list):
        from json import loads as json_loads
        from tmdbhelper.lib.files.downloader import Downloader
        from tmdbhelper.lib.addon.tmdate import get_datetime_now, get_timedelta
        datestamp = get_datetime_now() - get_timedelta(days=2)
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
        data = {i['id']: i['name'] for i in data if i} if data else {}
        if not data:
            return
        values = [(k, v) for k, v in data.items()]
        self.parent.set_cached_values(self.table, self.keys, values)
        return self.get_cached()


class TMDbDatabaseCollections:

    collections_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT'
        },
    }

    def get_collections(self):
        daily_export = TableDailyExport(self)
        daily_export.table = 'collections'
        daily_export.keys = ('id', 'name', )
        daily_export.export_list = 'collection'
        daily_export.conditions = 'name IS NOT NULL ORDER BY id'
        return daily_export.get_cached() or daily_export.set_cached()
