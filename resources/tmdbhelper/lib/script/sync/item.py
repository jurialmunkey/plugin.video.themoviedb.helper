from tmdbhelper.lib.addon.plugin import get_localized, executebuiltin
from tmdbhelper.lib.addon.dialog import BusyDialog
from jurialmunkey.parser import LazyProperty
from xbmcgui import Dialog


class ItemSyncAttributes:
    """
    kodi_log
    """
    kodi_log = LazyProperty('kodi_log')

    def get_kodi_log(self):
        from tmdbhelper.lib.addon.logger import kodi_log
        return kodi_log

    """
    trakt_api
    """
    trakt_api = LazyProperty('trakt_api')

    def get_trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    """
    trakt_syncdata
    """
    trakt_syncdata = LazyProperty('trakt_syncdata')

    def get_trakt_syncdata(self):
        return self.trakt_api.trakt_syncdata

    """
    trakt_sync_value
    """
    trakt_sync_value = LazyProperty('trakt_sync_value')

    def get_trakt_sync_value(self):
        return self.trakt_syncdata.get_value(self.tmdb_type, self.tmdb_id, self.season, self.episode, self.trakt_sync_key)

    """
    name_add
    """
    name_add = LazyProperty('name_add')

    def get_name_add(self):
        if not self.localized_name_add:
            return 'FIXME'
        return get_localized(self.localized_name_add)

    """
    name_remove
    """
    name_remove = LazyProperty('name_remove')

    def get_name_remove(self):
        if not self.localized_name_rem:
            return 'FIXME'
        return get_localized(self.localized_name_rem)

    """
    name
    """
    name = LazyProperty('name')

    def get_name(self):
        if not self.preconfigured:
            if not self.remove:
                return self.name_add
            return self.name_remove
        if not self.localized_name:
            return 'FIXME'
        return get_localized(self.localized_name)

    """
    is_sync
    """
    is_sync = LazyProperty('is_sync')

    def get_is_sync(self):
        if self.trakt_sync_value:
            return True
        return False

    """
    remove
    """
    remove = LazyProperty('remove')

    def get_remove(self):
        if self.is_sync:
            return True
        return False

    """
    is_allowed_type
    """
    is_allowed_type = LazyProperty('is_allowed_type')

    def get_is_allowed_type(self):
        if self.season is None:
            return True
        if self.episode is None:
            if self.allow_seasons:
                return True
            return False
        if self.allow_episodes:
            return True
        return False

    """
    method
    """
    method = LazyProperty('method')

    def get_method(self):
        if not self.remove:
            return self.trakt_sync_url
        return f'{self.trakt_sync_url}/remove'

    """
    trakt_type
    """
    trakt_type = LazyProperty('trakt_type')

    def get_trakt_type(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        if self.tmdb_type != 'tv':
            return
        if self.season is None:
            return 'show'
        if self.episode is None:
            return 'season'
        return 'episode'

    """
    base_trakt_type
    """
    base_trakt_type = LazyProperty('base_trakt_type')

    def get_base_trakt_type(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        if self.tmdb_type != 'tv':
            return
        return 'show'

    """
    item_id
    """
    item_id = LazyProperty('item_id')

    def get_item_id(self):
        return '.'.join([i for i in (self.tmdb_id, self.season, self.episode) if i])

    """
    dialog_message
    """
    dialog_message = LazyProperty('dialog_message')

    def get_dialog_message(self):
        if self.sync_response.status_code == 420:
            dialog_message = f'{get_localized(32296)}\n{get_localized(32531)}'
        elif not self.is_successful_sync:
            dialog_message = f'{get_localized(32296)}\nHTTP {self.sync_response.status_code}'
        else:
            dialog_message = get_localized(32297)
        return dialog_message.format(self.dialog_header, self.tmdb_type, 'TMDb', self.item_id)

    """
    slug
    """
    slug = LazyProperty('slug')

    def get_slug(self):
        return self.trakt_api.get_id(self.tmdb_id, 'tmdb', self.base_trakt_type, output_type='slug')

    """
    sync_response
    """
    sync_response = LazyProperty('sync_response')

    def get_sync_response(self):
        """ Called after user selects choice """
        with BusyDialog():
            return self.trakt_api.post_response(*self.post_response_args, postdata=self.post_response_data)

    """
    post_response_args
    """
    post_response_args = LazyProperty('post_response_args')

    def get_post_response_args(self):
        return ('sync', self.method, )

    """
    post_response_data
    """
    post_response_data = LazyProperty('post_response_data')

    def get_post_response_data(self):
        return {f'{self.post_response_type}': self.post_response_item}

    """
    post_response_type
    """
    post_response_type = LazyProperty('post_response_type')

    def get_post_response_type(self):
        if self.trakt_type == 'season':
            return 'episodes'
        return f'{self.trakt_type}s'

    """
    post_response_item
    """
    post_response_item = LazyProperty('post_response_item')

    def get_post_response_item(self):
        if isinstance(self.sync_item, list):
            return self.sync_item
        return [self.sync_item]

    """
    sync_item
    """
    sync_item = LazyProperty('sync_item')

    def get_sync_item(self):
        if self.season is None:
            return self.trakt_api.get_request_lc(f'{self.base_trakt_type}s', self.slug)
        if self.episode is None:
            return self.trakt_api.get_request_lc(f'{self.base_trakt_type}s', self.slug, 'seasons', self.season)
        return self.trakt_api.get_request_lc(f'{self.base_trakt_type}s', self.slug, 'seasons', self.season, 'episodes', self.episode)

    """
    is_successful_sync
    """
    is_successful_sync = LazyProperty('is_successful_sync')

    def get_is_successful_sync(self):
        if not self.sync_response:
            return False
        if self.sync_response.status_code not in [200, 201, 204]:
            return False
        return True

    """
    dialog_header
    """
    dialog_header = LazyProperty('dialog_header')

    def get_dialog_header(self):
        return self.name

    """
    self
    """

    def get_self(self):
        """ Method to see if we should return item in menu or not """

        # Check that we allow this content type
        if not self.is_allowed_type:
            return

        # Allow early exit for preconfigured items (e.g. watched history to give both choices)
        if self.preconfigured:
            return self

        # Just check property to check sync now
        if not self.is_sync:
            pass

        return self


class ItemSync(ItemSyncAttributes):
    preconfigured = False
    allow_seasons = False
    allow_episodes = False
    localized_name_add = None
    localized_name_rem = None
    localized_name = None
    trakt_sync_key = None
    trakt_sync_url = None

    def __init__(self, tmdb_type, tmdb_id, season=None, episode=None):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode

    def refresh_containers(self):
        if not self.is_successful_sync:
            return
        from jurialmunkey.window import get_property
        from tmdbhelper.lib.addon.tmdate import set_timestamp
        executebuiltin('Container.Refresh')
        get_property('Widgets.Reload', set_property=f'{set_timestamp(0, True)}')

    def display_dialog(self):
        Dialog().ok(self.dialog_header, self.dialog_message)

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.trakt_syncdata.reset_lastactivities()

    def sync(self):
        self.reset_lastactivities()
        self.display_dialog()
        self.refresh_containers()
