from jurialmunkey.ftools import cached_property


class PlayerDetails:

    external_id_types = ('tmdb', 'tvdb', 'imdb', 'slug', 'trakt')

    def __init__(self, tmdb_type, tmdb_id, season=None, episode=None, translation=False):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        self.translation = translation

    @cached_property
    def lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        lidc = ListItemDetails()
        lidc.cache_refresh = 'langs' if self.translation else None
        lidc.extendedinfo = True
        return lidc

    @cached_property
    def details(self):
        details = self.get_details()
        details.set_details(details=self.external_ids, reverse=True)
        return details

    def get_details(self, language=None):
        from tmdbhelper.lib.items.listitem import ListItem
        details = self.lidc.get_item(self.tmdb_type, self.tmdb_id, self.season, self.episode)
        return ListItem(**details) if details else None

    @cached_property
    def find_queries_db(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    @cached_property
    def trakt_type(self):
        return 'movie' if self.tmdb_type == 'movie' else 'show'

    @cached_property
    def trakt_slug(self):
        return self.find_queries_db.get_trakt_id(
            id_type='tmdb',
            id_value=self.tmdb_id,
            item_type=self.trakt_type,
            output_type='slug'
        )

    @cached_property
    def trakt_details(self):
        if not self.trakt_slug:
            return
        return self.trakt_api.get_response_json(f'{self.trakt_type}s', self.trakt_slug)

    @cached_property
    def trakt_details_ids(self):
        if not self.trakt_details:
            return {}
        return self.trakt_details.get('ids') or {}

    @cached_property
    def trakt_episode_details(self):
        if not self.trakt_slug:
            return
        if self.season is None:
            return
        if self.episode is None:
            return
        return self.trakt_api.get_response_json(
            'shows', self.trakt_slug,
            'seasons', self.season,
            'episodes', self.episode
        )

    @cached_property
    def trakt_episode_details_ids(self):
        if not self.trakt_episode_details:
            return {}
        return self.trakt_episode_details.get('ids') or {}

    @property
    def trakt_uid_generator(self):
        return ((i, self.trakt_details_ids.get(i)) for i in self.external_id_types)

    @cached_property
    def trakt_movie_uids(self):
        trakt_movie_uids = {k: v for k, v in self.trakt_uid_generator if k and v}
        trakt_movie_uids['tmdb'] = self.tmdb_id
        return trakt_movie_uids

    @cached_property
    def trakt_tvshow_uids(self):
        trakt_tvshow_uids = {f'tvshow.{k}': v for k, v in self.trakt_uid_generator if k and v}
        trakt_tvshow_uids['tvshow.tmdb'] = self.tmdb_id
        return trakt_tvshow_uids

    @property
    def trakt_episode_uid_generator(self):
        return ((i, self.trakt_episode_details_ids.get(i)) for i in self.external_id_types)

    @cached_property
    def trakt_episode_uids(self):
        trakt_episode_uids = self.trakt_tvshow_uids
        trakt_episode_uids.update({k: v for k, v in self.trakt_episode_uid_generator if k and v})
        trakt_episode_uids['tmdb'] = self.tmdb_id
        return trakt_episode_uids

    @cached_property
    def trakt_uids(self):
        if self.trakt_type == 'movie':
            return self.trakt_movie_uids
        return self.trakt_episode_uids

    @cached_property
    def external_ids(self):
        if not self.trakt_details_ids:
            return {}
        return {'unique_ids': self.trakt_uids}
