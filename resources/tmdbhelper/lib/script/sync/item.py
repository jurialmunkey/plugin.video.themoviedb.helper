from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from xbmcgui import Dialog


class ItemSync:
    preconfigured = False
    allow_movies = True
    allow_shows = True
    allow_seasons = False
    allow_episodes = False
    localized_name_add = None
    localized_name_rem = None
    localized_name = None
    convert_episodes = False
    convert_seasons = False
    confirm_success = True
    is_available = True

    def __init__(self, tmdb_type, tmdb_id, season=None, episode=None):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = None if self.convert_seasons else season
        self.episode = None if self.convert_episodes else episode

    """
    kodi_log
    """

    @cached_property
    def kodi_log(self):
        return self.get_kodi_log()

    def get_kodi_log(self):
        from tmdbhelper.lib.addon.logger import kodi_log
        return kodi_log

    """
    query_database
    """

    @cached_property
    def query_database(self):
        return self.get_query_database()

    def get_query_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    """
    item_details
    """

    @cached_property
    def item_details(self):
        return self.get_item_details()

    def get_item_details(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        return ListItemDetails().get_item(
            self.tmdb_type,
            self.tmdb_id,
            self.season,
            self.episode
        )

    """
    item_name
    """

    @cached_property
    def item_name(self):
        return self.get_item_name()

    def get_item_name(self):
        try:
            item_name = self.item_details['label']
        except (KeyError, TypeError):
            return
        try:
            item_name = f'{item_name} ({self.item_details["infolabels"]["year"]})'
        except (KeyError, TypeError):
            pass
        return item_name

    """
    name_add
    """

    @cached_property
    def name_add(self):
        return self.get_name_add()

    def get_name_add(self):
        if not self.localized_name_add:
            return 'FIXME NAME ADD'
        return get_localized(self.localized_name_add)

    """
    name_remove
    """

    @cached_property
    def name_remove(self):
        return self.get_name_remove()

    def get_name_remove(self):
        if not self.localized_name_rem:
            return 'FIXME NAME REM'
        return get_localized(self.localized_name_rem)

    """
    name
    """

    @cached_property
    def name(self):
        return self.get_name()

    def get_name(self):
        if not self.preconfigured:
            if not self.remove:
                return self.name_add
            return self.name_remove
        if not self.localized_name:
            return 'FIXME NAME INT'
        return get_localized(self.localized_name)

    """
    is_sync
    """

    @cached_property
    def is_sync(self):
        return self.get_is_sync()

    def get_is_sync(self):
        return bool(self.sync_value)

    """
    sync_value
    """

    @cached_property
    def sync_value(self):
        return self.get_sync_value()

    def get_sync_value(self):
        raise  # Should be defined in derived class

    """
    remove
    """

    @cached_property
    def remove(self):
        return self.get_remove()

    def get_remove(self):
        return bool(self.is_sync)

    """
    is_allowed_type
    """

    @cached_property
    def is_allowed_type(self):
        return self.get_is_allowed_type()

    def get_is_allowed_type(self):
        if self.trakt_type == 'episode':
            return bool(self.allow_episodes)
        if self.trakt_type == 'season':
            return bool(self.allow_seasons)
        if self.trakt_type == 'show':
            return bool(self.allow_shows)
        if self.trakt_type == 'movie':
            return bool(self.allow_movies)
        return False

    """
    trakt_type
    """

    @cached_property
    def trakt_type(self):
        return self.get_trakt_type()

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

    @cached_property
    def base_trakt_type(self):
        return self.get_base_trakt_type()

    def get_base_trakt_type(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        if self.tmdb_type != 'tv':
            return
        return 'show'

    """
    item_id
    """

    @cached_property
    def item_id(self):
        return self.get_item_id()

    def get_item_id(self):
        return '.'.join([i for i in (self.tmdb_id, self.season, self.episode) if i])

    """
    status_code
    """

    @cached_property
    def status_code(self):
        return self.get_status_code()

    def get_status_code(self):
        return self.sync_response.status_code

    """
    status_code_message
    """

    @cached_property
    def status_code_message(self):
        return self.get_status_code_message()

    def get_status_code_message(self):
        return f'HTTP {self.status_code}'

    """
    dialog_message
    """

    @cached_property
    def dialog_message(self):
        return self.get_dialog_message()

    def get_dialog_message(self):
        if not self.sync_response:
            return
        if self.status_code == 420:
            dialog_message = f'{get_localized(32296)}\n{get_localized(32531)}'
        elif not self.is_successful_sync:
            dialog_message = f'{get_localized(32296)}\n{self.status_code_message}'
        elif self.confirm_success:
            dialog_message = get_localized(32297)
        else:
            return
        return dialog_message.format(
            self.dialog_header,
            self.item_name,
            self.tmdb_type,
            self.item_id
        )

    """
    sync_response
    """

    @cached_property
    def sync_response(self):
        return self.get_sync_response()

    def get_sync_response(self):
        """ Called after user selects choice """
        raise  # Should be defined in derived class

    """
    is_successful_sync
    """

    @cached_property
    def is_successful_sync(self):
        return self.get_is_successful_sync()

    def get_is_successful_sync(self):
        if not self.sync_response:
            return False
        if self.status_code not in [200, 201, 204]:
            return False
        return True

    """
    dialog_header
    """

    @cached_property
    def dialog_header(self):
        return self.get_dialog_header()

    def get_dialog_header(self):
        return self.name

    """
    methods
    """

    def refresh_containers(self):
        if not self.is_successful_sync:
            return
        from tmdbhelper.lib.script.method.kodi_utils import container_refresh
        container_refresh()

    def display_dialog(self):
        if not self.dialog_message:
            return
        Dialog().ok(self.dialog_header, self.dialog_message)

    def sync(self):
        self.display_dialog()
        self.refresh_containers()

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

        # Check that this type is available to sync
        if not self.is_available:
            return

        return self
