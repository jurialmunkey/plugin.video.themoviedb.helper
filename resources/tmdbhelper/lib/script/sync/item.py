from tmdbhelper.lib.addon.plugin import get_localized, executebuiltin
from tmdbhelper.lib.addon.dialog import BusyDialog
from jurialmunkey.parser import LazyProperty
from xbmcgui import Dialog


class ItemSyncAttributes:
    """
    kodi_log
    """
    @property
    def kodi_log(self):
        try:
            return self._kodi_log
        except AttributeError:
            self._kodi_log = self.get_kodi_log()
            return self._kodi_log

    @kodi_log.setter
    def kodi_log(self, value):
        self._kodi_log = value

    def get_kodi_log(self):
        from tmdbhelper.lib.addon.logger import kodi_log
        return kodi_log

    """
    trakt_api
    """
    @property
    def trakt_api(self):
        try:
            return self._trakt_api
        except AttributeError:
            self._trakt_api = self.get_trakt_api()
            return self._trakt_api

    @trakt_api.setter
    def trakt_api(self, value):
        self._trakt_api = value

    def get_trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    """
    trakt_syncdata
    """
    @property
    def trakt_syncdata(self):
        try:
            return self._trakt_syncdata
        except AttributeError:
            self._trakt_syncdata = self.get_trakt_syncdata()
            return self._trakt_syncdata

    @trakt_syncdata.setter
    def trakt_syncdata(self, value):
        self._trakt_syncdata = value

    def get_trakt_syncdata(self):
        return self.trakt_api.trakt_syncdata

    """
    trakt_sync_value
    """
    @property
    def trakt_sync_value(self):
        try:
            return self._trakt_sync_value
        except AttributeError:
            self._trakt_sync_value = self.get_trakt_sync_value()
            return self._trakt_sync_value

    @trakt_sync_value.setter
    def trakt_sync_value(self, value):
        self._trakt_sync_value = value

    def get_trakt_sync_value(self):
        return self.trakt_syncdata.get_value(self.tmdb_type, self.tmdb_id, self.season, self.episode, self.trakt_sync_key)

    """
    name_add
    """
    @property
    def name_add(self):
        try:
            return self._name_add
        except AttributeError:
            self._name_add = self.get_name_add()
            return self._name_add

    @name_add.setter
    def name_add(self, value):
        self._name_add = value

    def get_name_add(self):
        if not self.localized_name_add:
            return 'FIXME'
        return get_localized(self.localized_name_add)

    """
    name_remove
    """
    @property
    def name_remove(self):
        try:
            return self._name_remove
        except AttributeError:
            self._name_remove = self.get_name_remove()
            return self._name_remove

    @name_remove.setter
    def name_remove(self, value):
        self._name_remove = value

    def get_name_remove(self):
        if not self.localized_name_rem:
            return 'FIXME'
        return get_localized(self.localized_name_rem)

    """
    name
    """
    @property
    def name(self):
        try:
            return self._name
        except AttributeError:
            self._name = self.get_name()
            return self._name

    @name.setter
    def name(self, value):
        self._name = value

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
    @property
    def is_sync(self):
        try:
            return self._is_sync
        except AttributeError:
            self._is_sync = self.get_is_sync()
            return self._is_sync

    @is_sync.setter
    def is_sync(self, value):
        self._is_sync = value

    def get_is_sync(self):
        if self.trakt_sync_value:
            return True
        return False

    """
    remove
    """
    @property
    def remove(self):
        try:
            return self._remove
        except AttributeError:
            self._remove = self.get_remove()
            return self._remove

    @remove.setter
    def remove(self, value):
        self._remove = value

    def get_remove(self):
        if self.is_sync:
            return True
        return False

    """
    is_allowed_type
    """
    @property
    def is_allowed_type(self):
        try:
            return self._is_allowed_type
        except AttributeError:
            self._is_allowed_type = self.get_is_allowed_type()
            return self._is_allowed_type

    @is_allowed_type.setter
    def is_allowed_type(self, value):
        self._is_allowed_type = value

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
    @property
    def method(self):
        try:
            return self._method
        except AttributeError:
            self._method = self.get_method()
            return self._method

    @method.setter
    def method(self, value):
        self._method = value

    def get_method(self):
        if not self.remove:
            return self.trakt_sync_url
        return f'{self.trakt_sync_url}/remove'

    """
    trakt_type
    """
    @property
    def trakt_type(self):
        try:
            return self._trakt_type
        except AttributeError:
            self._trakt_type = self.get_trakt_type()
            return self._trakt_type

    @trakt_type.setter
    def trakt_type(self, value):
        self._trakt_type = value

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
    @property
    def base_trakt_type(self):
        try:
            return self._base_trakt_type
        except AttributeError:
            self._base_trakt_type = self.get_base_trakt_type()
            return self._base_trakt_type

    @base_trakt_type.setter
    def base_trakt_type(self, value):
        self._base_trakt_type = value

    def get_base_trakt_type(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        if self.tmdb_type != 'tv':
            return
        return 'show'

    """
    item_id
    """
    @property
    def item_id(self):
        try:
            return self._item_id
        except AttributeError:
            self._item_id = self.get_item_id()
            return self._item_id

    @item_id.setter
    def item_id(self, value):
        self._item_id = value

    def get_item_id(self):
        return '.'.join([i for i in (self.tmdb_id, self.season, self.episode) if i])

    """
    dialog_message
    """
    @property
    def dialog_message(self):
        try:
            return self._dialog_message
        except AttributeError:
            self._dialog_message = self.get_dialog_message()
            return self._dialog_message

    @dialog_message.setter
    def dialog_message(self, value):
        self._dialog_message = value

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
    @property
    def slug(self):
        try:
            return self._slug
        except AttributeError:
            self._slug = self.get_slug()
            return self._slug

    @slug.setter
    def slug(self, value):
        self._slug = value

    def get_slug(self):
        return self.trakt_api.get_id(self.tmdb_id, 'tmdb', self.base_trakt_type, output_type='slug')

    """
    sync_response
    """
    @property
    def sync_response(self):
        try:
            return self._sync_response
        except AttributeError:
            self._sync_response = self.get_sync_response()
            return self._sync_response

    @sync_response.setter
    def sync_response(self, value):
        self._sync_response = value

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
    @property
    def sync_item(self):
        try:
            return self._sync_item
        except AttributeError:
            self._sync_item = self.get_sync_item()
            return self._sync_item

    @sync_item.setter
    def sync_item(self, value):
        self._sync_item = value

    def get_sync_item(self):
        if self.season is None:
            return self.trakt_api.get_request_lc(f'{self.base_trakt_type}s', self.slug)
        if self.episode is None:
            return self.trakt_api.get_request_lc(f'{self.base_trakt_type}s', self.slug, 'seasons', self.season)
        return self.trakt_api.get_request_lc(f'{self.base_trakt_type}s', self.slug, 'seasons', self.season, 'episodes', self.episode)

    """
    is_successful_sync
    """
    @property
    def is_successful_sync(self):
        try:
            return self._is_successful_sync
        except AttributeError:
            self._is_successful_sync = self.get_is_successful_sync()
            return self._is_successful_sync

    @is_successful_sync.setter
    def is_successful_sync(self, value):
        self._is_successful_sync = value

    def get_is_successful_sync(self):
        if not self.sync_response:
            return False
        if self.sync_response.status_code not in [200, 201, 204]:
            return False
        return True

    """
    dialog_header
    """
    @property
    def dialog_header(self):
        try:
            return self._dialog_header
        except AttributeError:
            self._dialog_header = self.get_dialog_header()
            return self._dialog_header

    @dialog_header.setter
    def dialog_header(self, value):
        self._dialog_header = value

    def get_dialog_header(self):
        return self.name

    """
    self
    """
    @property
    def self(self):
        try:
            return self._self
        except AttributeError:
            self._self = self.get_self()
            return self._self

    @self.setter
    def self(self, value):
        self._self = value

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
