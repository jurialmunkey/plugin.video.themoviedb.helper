from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.files.futils import validate_join
import xbmcvfs
import json


class CommonContainerAPIs():
    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    @cached_property
    def tmdb_imagepath(self):
        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
        return TMDbImagePath()

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    @cached_property
    def ftv_api(self):
        from tmdbhelper.lib.api.fanarttv.api import FanartTV
        from tmdbhelper.lib.addon.plugin import get_setting
        if not get_setting('fanarttv_lookup'):
            return
        return FanartTV()

    @cached_property
    def tvdb_api(self):
        from tmdbhelper.lib.api.tvdb.api import TVDb
        return TVDb()

    @cached_property
    def mdblist_api(self):
        from tmdbhelper.lib.api.mdblist.api import MDbListAPI
        return MDbListAPI()

    @cached_property
    def omdb_api(self):
        from tmdbhelper.lib.api.omdb.api import OMDb
        from tmdbhelper.lib.addon.plugin import get_setting
        if not get_setting('omdb_apikey', 'str'):
            return
        return OMDb()

    @cached_property
    def query_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()


class CommonRatingsAPIs(CommonContainerAPIs):

    tmdb_id = None
    tmdb_type = None
    season = None
    episode = None

    tvdb_awards_keys = {
        'Academy Awards': 'academy',
        'Golden Globe Awards': 'goldenglobe',
        'MTV Movie & TV Awards': 'mtv',
        'Critics\' Choice Awards': 'criticschoice',
        'Primetime Emmy Awards': 'emmy',
        'Screen Actors Guild Awards': 'sag',
        'BAFTA Awards': 'bafta'
    }

    @cached_property
    def all_awards(self):
        return self.get_awards_data()

    @staticmethod
    def get_awards_data():
        try:
            filepath = validate_join('special://home/addons/plugin.video.themoviedb.helper/resources/jsondata/', 'awards.json')
            with xbmcvfs.File(filepath, 'r') as file:
                return json.load(file)
        except (IOError, json.JSONDecodeError):
            kodi_log('ERROR: Failed to load awards data!')
            return {'movie': {}, 'tv': {}}

    @cached_property
    def tvdb_awards(self):
        return self.get_tvdb_awards()

    def get_tvdb_awards(self):
        info = {}
        try:
            awards = self.all_awards[self.tmdb_type][str(self.tmdb_id)]
        except(KeyError, TypeError, AttributeError):
            return info
        for t in ['awards_won', 'awards_nominated']:
            item_awards = awards.get(t)
            if not item_awards:
                continue
            all_awards, all_awards_cr = [], []
            for cat, lst in item_awards.items():
                all_awards_cr.append(f'[CR]{cat}' if all_awards else cat)
                all_awards_cr += lst
                all_awards += [(f'{cat} {i}') for i in lst]
                try:
                    info[f'{self.tvdb_awards_keys[cat]}_{t}'] = len(lst)
                except(KeyError, TypeError, AttributeError):
                    continue
            if all_awards:
                info[f'total_{t}'] = len(all_awards)
                info[t] = ' / '.join(all_awards)
                info[f'{t}_cr'] = '[CR]'.join(all_awards_cr)
        return info

    def configure_sync(self, sync, season=None, episode=None):
        sync.common_apis.mdblist_api = self.mdblist_api
        sync.common_apis.trakt_api = self.trakt_api
        sync.common_apis.tmdb_api = self.tmdb_api
        sync.common_apis.omdb_api = self.omdb_api
        sync.tmdb_type = self.tmdb_type
        sync.tmdb_id = self.tmdb_id
        sync.season = season
        sync.episode = episode
        return sync

    @cached_property
    def detailed_ratings(self):
        return self.get_detailed_ratings()

    def get_detailed_ratings(self):
        from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ratings import RatingsDict
        sync = RatingsDict()
        sync = self.configure_sync(sync)
        return sync.data or {}

    @cached_property
    def season_ratings(self):
        return self.get_season_ratings()

    def get_season_ratings(self):
        from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ratings import RatingsSeasonsDict
        sync = RatingsSeasonsDict()
        sync = self.configure_sync(sync, self.season)
        return sync.data or {}

    @cached_property
    def episode_ratings(self):
        return self.get_episode_ratings()

    def get_episode_ratings(self):
        from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ratings import RatingsEpisodesDict
        sync = RatingsEpisodesDict()
        sync = self.configure_sync(sync, self.season, self.episode)
        return sync.data or {}

    @cached_property
    def all_ratings(self):
        return self.get_all_ratings()

    @cached_property
    def all_ratings_no_awards(self):
        return self.get_all_ratings(awards=False)

    def get_all_ratings(self, awards=True):
        info = {}
        info.update(self.detailed_ratings)
        info.update(self.season_ratings)
        info.update(self.episode_ratings)
        info.update(self.tvdb_awards) if awards else None
        return info
