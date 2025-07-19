from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.script.sync.item import ItemSync as BasicItemSync


class ItemSync(BasicItemSync):
    trakt_sync_key = None
    trakt_sync_url = None

    """
    trakt_api
    """

    @cached_property
    def trakt_api(self):
        return self.get_trakt_api()

    def get_trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    """
    trakt_syncdata
    """

    @cached_property
    def trakt_syncdata(self):
        return self.get_trakt_syncdata()

    def get_trakt_syncdata(self):
        return self.trakt_api.trakt_syncdata

    """
    method
    """

    @cached_property
    def method(self):
        return self.get_method()

    def get_method(self):
        if not self.remove:
            return self.trakt_sync_url
        return f'{self.trakt_sync_url}/remove'

    """
    trakt_slug
    """

    @cached_property
    def trakt_slug(self):
        return self.get_trakt_slug()

    def get_trakt_slug(self):
        return self.query_database.get_trakt_id(self.tmdb_id, 'tmdb', self.base_trakt_type, output_type='slug')

    """
    post_response_args
    """

    @cached_property
    def post_response_args(self):
        return self.get_post_response_args()

    def get_post_response_args(self):
        return ('sync', self.method, )

    """
    post_response_data
    """

    @cached_property
    def post_response_data(self):
        return self.get_post_response_data()

    def get_post_response_data(self):
        return {f'{self.post_response_type}': self.post_response_item}

    """
    post_response_type
    """

    @cached_property
    def post_response_type(self):
        return self.get_post_response_type()

    def get_post_response_type(self):
        if self.trakt_type == 'season':
            return 'episodes'
        return f'{self.trakt_type}s'

    """
    post_response_item
    """

    @cached_property
    def post_response_item(self):
        return self.get_post_response_item()

    def get_post_response_item(self):
        if isinstance(self.sync_item, list):
            return self.sync_item
        return [self.sync_item]

    """
    sync_item
    """

    @cached_property
    def sync_item(self):
        return self.get_sync_item()

    def get_sync_item(self):
        if self.season is None:
            return self.trakt_api.get_response_json(f'{self.base_trakt_type}s', self.trakt_slug)
        if self.episode is None:
            return self.trakt_api.get_response_json('shows', self.trakt_slug, 'seasons', self.season)
        return self.trakt_api.get_response_json('shows', self.trakt_slug, 'seasons', self.season, 'episodes', self.episode)

    """
    methods
    """

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.trakt_syncdata.reset_lastactivities()

    """
    overrides
    """

    def get_sync_value(self):
        return self.trakt_syncdata.get_value(
            self.tmdb_type,
            self.tmdb_id,
            self.season,
            self.episode,
            self.trakt_sync_key
        )

    @busy_decorator
    def get_sync_response(self):
        """ Called after user selects choice """
        return self.trakt_api.post_response(*self.post_response_args, postdata=self.post_response_data)

    def sync(self):
        self.reset_lastactivities()
        super().sync()
