# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from jurialmunkey.ftools import cached_property
from hashlib import sha256
from time import monotonic
from jurialmunkey.window import get_property
from tmdbhelper.lib.files.futils import json_loads, json_dumps
from tmdbhelper.lib.files.locker import mutexlock


def blur_image(blur_image=None, prefix='ListItem', **kwargs):
    from tmdbhelper.lib.monitor.images import ImageFunctions
    blur_img = ImageFunctions(method='blur', artwork=blur_image, prefix=prefix)
    blur_img.setName('blur_img')
    blur_img.start()


def image_colors(image_colors=None, prefix='ListItem', **kwargs):
    from tmdbhelper.lib.monitor.images import ImageFunctions
    image_colors = ImageFunctions(method='colors', artwork=image_colors, prefix=prefix)
    image_colors.setName('image_colors')
    image_colors.start()


class GenreArtwork:

    tmdb_type = 'genre'

    @cached_property
    def sync_notifications(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return get_setting('sync_notifications')

    def run(self):
        for k, v in self.fanart.items():
            get_property(k, v)

    p_dialog_max = 0

    @cached_property
    def p_dialog(self):
        if not self.sync_notifications:
            return
        from tmdbhelper.lib.addon.dialog import ProgressDialog
        from tmdbhelper.lib.addon.plugin import get_localized
        return ProgressDialog(
            f'{self.tmdb_type.capitalize()} {get_localized(39123)}', f'{get_localized(32399)}...',
            total=self.p_dialog_max,
            logging=2
        )

    def get_item(self, name, tmdb_id, tmdb_type):
        params = self.get_params(tmdb_id, tmdb_type)
        item = {'name': name, 'items': self.get_directory(params)}
        self.p_dialog.update(f'{name} {tmdb_type}') if self.p_dialog else None
        return (tmdb_id, item)

    def get_item_data(self, i):
        return self.get_item(*i)

    def get_data_type(self, tmdb_type):
        data = getattr(self, f'items_{tmdb_type}')
        data = tuple((
            (name, tmdb_id, tmdb_type)
            for name, tmdb_id in data.items()
        ))

        from tmdbhelper.lib.addon.thread import ParallelThread
        with ParallelThread(data, self.get_item_data) as pt:
            items = pt.queue

        return {i[0]: i[1] for i in items if i}

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        self.p_dialog_max = len(self.items_movie) + len(self.items_tv)  # Init value outside of threading to avoid sqlite object reuse
        try:
            return {'movie': self.data_movie, 'tv': self.data_tv}
        finally:
            self.p_dialog.close() if self.p_dialog else None

    @cached_property
    def data_movie(self):
        return self.get_data_type('movie')

    @cached_property
    def data_tv(self):
        return self.get_data_type('tv')

    @staticmethod
    def get_shuffled_list(items):
        import random
        random.shuffle(items)
        return items

    def get_generator(self, items, key, base_key='art'):
        return (
            i[base_key][key]
            for i in self.get_shuffled_list(items)
            if i.get(base_key) and i[base_key].get(key)
        )

    @cached_property
    def fanart(self):
        return self.get_fanart()

    @cached_property
    def mutex_lockname(self):
        return self.get_mutex_lockname()

    def get_mutex_lockname(self):
        cache_key = json_dumps(self.get_cache_key())
        return f'TMDbHelper.Artwork.{sha256(cache_key.encode("utf-8")).hexdigest()}'

    def get_cache_key(self):
        from xbmcvfs import translatePath
        from tmdbhelper.lib.addon.plugin import ADDONDATA, get_language
        return (translatePath(ADDONDATA), self.tmdb_type, get_language())

    def get_fanart(self):
        return self.get_fanart_data(monotonic()) or {}

    @mutexlock
    def get_fanart_data(self, requested_at):
        # Only reuse a batch completed since this request began, preserving later refreshes.
        cached_fanart = self.get_cached_fanart(requested_at)
        if cached_fanart is not None:
            return cached_fanart
        fanart = self.get_formatted_dict('fanart')
        result = {'completed_at': monotonic(), 'fanart': fanart}
        get_property(self.mutex_lockname, set_property=json_dumps(result))
        return fanart

    def get_cached_fanart(self, requested_at):
        result = json_loads(get_property(self.mutex_lockname))
        if result and result['completed_at'] >= requested_at:
            return result['fanart']

    def get_formatted_dict(self, key):
        datadict = {
            f'{self.tmdb_type}.{tmdb_type}.{tmdb_id}.{key}': next(self.get_generator(data['items'], key), '')
            for tmdb_type in ('movie', 'tv') for tmdb_id, data in self.data[tmdb_type].items()
        }
        return datadict

    @staticmethod
    def get_params(tmdb_id, tmdb_type):
        params = {
            'info': 'discover',
            'tmdb_type': tmdb_type,
            'with_genres': tmdb_id,
            'with_id': 'True',
        }
        return params

    def get_directory(self, params):
        from tmdbhelper.lib.items.directories.tmdb.lists_discover import ListDiscover
        return ListDiscover(-1, '', **params).get_directory_items()

    @cached_property
    def query_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    @cached_property
    def items_movie(self):
        return self.query_database.get_genres('movie')

    @cached_property
    def items_tv(self):
        return self.query_database.get_genres('tv')


class ProviderArtwork(GenreArtwork):
    tmdb_type = 'provider'

    def __init__(self):
        self.iso_country = self.query_database.tmdb_api.iso_country

    def get_cache_key(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return (*super().get_cache_key(), self.iso_country, get_setting('provider_allowlist', 'str'))

    @cached_property
    def items_movie(self):
        items_movie = self.query_database.get_watch_providers('movie', self.iso_country, allowlist_only=True)
        items_movie = {i['provider_name']: i['provider_id'] for i in items_movie}
        return items_movie

    @cached_property
    def items_tv(self):
        items_tv = self.query_database.get_watch_providers('tv', self.iso_country, allowlist_only=True)
        items_tv = {i['provider_name']: i['provider_id'] for i in items_tv}
        return items_tv

    def get_params(self, tmdb_id, tmdb_type):
        params = {
            'info': 'discover',
            'tmdb_type': tmdb_type,
            'with_watch_providers': tmdb_id,
            'watch_region': self.iso_country,
            'with_id': 'True',
        }
        return params

    def get_directory(self, params):
        from tmdbhelper.lib.items.directories.tmdb.lists_discover import ListDiscover
        return ListDiscover(-1, '', **params).get_directory_items()


def genre_fanart(**kwargs):
    GenreArtwork().run()
