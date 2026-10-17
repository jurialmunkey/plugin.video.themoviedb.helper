from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.script.sync.request import ItemSync as BasicItemSync


class ItemSync(BasicItemSync):
    @cached_property
    def trakt_api(self):
        return self.get_trakt_api()

    def get_trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    @cached_property
    def trakt_slug(self):
        return self.get_trakt_slug()

    def get_trakt_slug(self):
        return self.query_database.get_trakt_id(self.tmdb_id, 'tmdb', self.base_trakt_type, output_type='slug')

    def get_post_response_args(self):
        return ('sync', self.method, )

    def get_post_response_type(self):
        if self.trakt_type == 'season':
            return 'episodes'
        return f'{self.trakt_type}s'

    def get_sync_item(self):
        if self.season is None:
            return self.trakt_api.get_response_json(f'{self.base_trakt_type}s', self.trakt_slug)
        if self.episode is None:
            return self.trakt_api.get_response_json('shows', self.trakt_slug, 'seasons', self.season)
        return self.trakt_api.get_response_json('shows', self.trakt_slug, 'seasons', self.season, 'episodes', self.episode)

    @busy_decorator
    def get_sync_response(self):
        """ Called after user selects choice """
        return self.trakt_api.post_response(*self.post_response_args, postdata=self.post_response_data)
