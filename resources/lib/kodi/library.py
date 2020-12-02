import xbmc
import xbmcgui
import xbmcvfs
import resources.lib.kodi.rpc as rpc
from resources.lib.addon.parser import try_int
from resources.lib.addon.plugin import ADDON
from resources.lib.files.utils import validify_filename, get_tmdb_id_nfo
from resources.lib.kodi.logger import _LibraryLogger
from resources.lib.kodi.update import BASEDIR_MOVIE, BASEDIR_TV, STRM_MOVIE, STRM_EPISODE, create_file, create_nfo, get_unique_folder, get_userlist, create_playlist
from resources.lib.kodi.cacher import _TVShowCache
from resources.lib.addon.timedate import is_future_timestamp, get_current_date_time
from resources.lib.tmdb.api import TMDb


def add_to_library(info, busy_spinner=True, library_adder=None, finished=True, **kwargs):
    if not info:
        return
    if not library_adder:
        library_adder = LibraryAdder(busy_spinner)
        library_adder._start()
    if info == 'movie' and kwargs.get('tmdb_id'):
        library_adder.add_movie(**kwargs)
    elif info == 'tv' and kwargs.get('tmdb_id'):
        library_adder.add_tvshow(**kwargs)
    elif info == 'trakt' and kwargs.get('list_slug'):
        library_adder.add_userlist(**kwargs)
    elif info == 'update':
        library_adder.update_tvshows(**kwargs)
    if not finished:
        return library_adder
    library_adder._finish()
    del library_adder


class LibraryAdder():
    def __init__(self, busy_spinner=True):
        self.kodi_db_movies = rpc.get_kodi_library('movie')
        self.kodi_db_tv = rpc.get_kodi_library('tv')
        self.p_dialog = xbmcgui.DialogProgressBG() if busy_spinner else None
        self.auto_update = ADDON.getSettingBool('auto_update')
        self._log = _LibraryLogger()
        self.tv = None
        self.hide_unaired = ADDON.getSettingBool('hide_unaired_episodes')
        # self.debug_logging = ADDON.getSettingBool('debug_logging')
        self.debug_logging = True

    def _start(self):
        if self.p_dialog:
            self.p_dialog.create('TMDbHelper', ADDON.getLocalizedString(32166))

    def _finish(self, update=True):
        if self.p_dialog:
            self.p_dialog.close()
        if self.debug_logging:
            self._log._out()
        if update and self.auto_update:
            xbmc.executebuiltin('UpdateLibrary(video)')

    def _update(self, count, total, **kwargs):
        if self.p_dialog:
            self.p_dialog.update((((count + 1) * 100) // total), **kwargs)

    def update_tvshows(self, force=False, **kwargs):
        nfos = []

        # Get TMDb IDs from nfo files in folder
        nfos_append = nfos.append  # For speed since we can't do a list comp easily here
        for f in xbmcvfs.listdir(BASEDIR_TV)[0]:
            tmdb_id = get_tmdb_id_nfo(BASEDIR_TV, f)
            nfos_append({'tmdb_id': tmdb_id, 'folder': f}) if tmdb_id else None

        # Update each show in folder
        nfos_total = len(nfos)
        for x, i in enumerate(nfos):
            self._update(x, nfos_total, message=u'{} {}...'.format(ADDON.getLocalizedString(32167), i['folder']))
            self.add_tvshow(tmdb_id=i['tmdb_id'], force=force)

        # Update last updated stamp
        ADDON.setSettingString('last_autoupdate', u'Last updated {}'.format(get_current_date_time()))

    def add_userlist(self, user_slug=None, list_slug=None, confirm=True, force=False, **kwargs):
        request = get_userlist(user_slug=user_slug, list_slug=list_slug, confirm=confirm, busy_spinner=self.p_dialog)
        if not request:
            return
        i_total = len(request)
        i_added = {'movie': [], 'show': []}

        for x, i in enumerate(request):
            self._update(x, i_total, message=u'Updating {}...'.format(i.get(i.get('type'), {}).get('title')))
            playlist_rule = self._add_userlist_item(i, force=force)
            if not playlist_rule:
                continue
            i_added[i.get('type')].append(playlist_rule)

        if i_added.get('movie'):
            self._update(1, 3, message=ADDON.getLocalizedString(32349))
            create_playlist(i_added['movie'], 'movies', user_slug, list_slug)
        if i_added.get('show'):
            self._update(2, 3, message=ADDON.getLocalizedString(32350))
            create_playlist(i_added['show'], 'tvshows', user_slug, list_slug)

    def _add_userlist_item(self, i, force=False):
        i_type = i.get('type')
        if i_type == 'movie':
            func = self.add_movie
        elif i_type == 'show':
            func = self.add_tvshow
        else:
            return

        item = i.get(i_type, {})
        tmdb_id = item.get('ids', {}).get('tmdb')

        if not tmdb_id:
            self._log._add(
                'tv' if i_type == 'show' else 'movie', item.get('ids', {}).get('slug'),
                'skipped item in Trakt user list with missing TMDb ID')
            return

        return func(tmdb_id, force=force)

    def add_movie(self, tmdb_id=None, **kwargs):
        if not tmdb_id:
            return

        # Get movie details
        details = TMDb().get_request_sc('movie', tmdb_id, append_to_response='external_ids')
        if not details or not details.get('title'):
            return
        imdb_id = details.get('external_ids', {}).get('imdb_id')
        name = u'{} ({})'.format(details['title'], details['release_date'][:4]) if details.get('release_date') else details['title']

        # Only add strm if not in library
        file = self.kodi_db_movies.get_info(info='file', imdb_id=imdb_id, tmdb_id=tmdb_id)
        if not file:
            file = create_file(STRM_MOVIE.format(tmdb_id), name, name, basedir=BASEDIR_MOVIE)
            create_nfo('movie', tmdb_id, name, basedir=BASEDIR_MOVIE)
            self._log._add('movie', tmdb_id, 'added strm file', path=file)
        else:
            self._log._add('movie', tmdb_id, 'item in library', path=file)

        # Return our playlist rule
        return ('filename', file.replace('\\', '/').split('/')[-1])

    def add_tvshow(self, tmdb_id=None, force=False, **kwargs):
        self.tv = _TVShow(tmdb_id, force)

        # Return playlist rule if we don't need to check show this time
        if self._log._add('tv', tmdb_id, self.tv._cache.get_next_check()):
            return ('title', self.tv._cache.cache_info.get('name'))

        if not self.tv.get_details():
            return  # Skip if no details found on TMDb
        if not self.tv.get_name():
            return  # Skip if we don't have a folder name for some reason

        self.tv.get_dbid()
        self.tv.make_nfo()
        self.tv.set_next()

        # Add seasons
        for x, season in enumerate(self.tv.get_seasons()):
            self._update(x, self.tv.s_total, message=u'{} {} - {} {}...'.format(
                ADDON.getLocalizedString(32167), self.tv.details.get('name'),
                xbmc.getLocalizedString(20373), season.get('season_number', 0)))  # Update our progress dialog
            self._add_season(season)

        # Store details about what we did into the cache
        self.tv._cache.set_cache()

        # Return our playlist rule tuple
        return ('title', self.tv.details.get('name'))

    def _add_season(self, season, blacklist=[0]):
        number = season.get('season_number', 0)
        folder = u'Season {}'.format(number)

        # Skip blacklisted seasons
        if try_int(number) in blacklist:  # TODO: Optional whitelist also
            self._log._add('tv', self.tv.tmdb_id, 'skipped special season', season=number)
            return

        # Skip if we've added season before and it isn't the most recent season
        # We still add most recent season even if we added it before because it might currently be airing
        if self._log._add('tv', self.tv.tmdb_id, self.tv._cache.is_added_season(number), season=number):
            return

        # Add our episodes
        for x, episode in enumerate(self.tv.get_episodes(number), 1):
            self._add_episode(episode, number, folder)
            self._update(x, self.tv.e_total)

        # Store a season value of where we got up to
        if self.tv.e_total > 2 and season.get('air_date') and not is_future_timestamp(season.get('air_date'), "%Y-%m-%d", 10):
            self.tv._cache.my_history['latest_season'] = try_int(number)

    def _add_episode(self, episode, season, folder):
        number = episode.get('episode_number')
        filename = validify_filename(u'S{:02d}E{:02d} - {}'.format(try_int(season), try_int(number), episode.get('name')))
        self.tv._cache.my_history['episodes'].append(filename)

        # Skip episodes we added in the past
        if self._log._add('tv', self.tv.tmdb_id, self.tv._cache.is_added_episode(filename), season=season, episode=number):
            return

        # Skip future episodes
        if self.hide_unaired and is_future_timestamp(episode.get('air_date'), "%Y-%m-%d", 10):
            self.tv._cache.my_history['skipped'].append(filename)
            self._log._add('tv', self.tv.tmdb_id, 'unaired episode', season=season, episode=number, air_date=episode.get('air_date'))
            return

        # Check if item has already been added
        file = self.tv.get_episode_db_info(season, number, info='file')
        if file:
            self._log._add('tv', self.tv.tmdb_id, 'found in library', season=season, episode=number, path=file)
            return

        # Add our strm file
        file = create_file(STRM_EPISODE.format(self.tv.tmdb_id, season, number), filename, self.tv.name, folder, basedir=BASEDIR_TV)
        self._log._add('tv', self.tv.tmdb_id, 'added strm file', season=season, episode=number, path=file)


class _TVShow():
    def __init__(self, tmdb_id, force=False):
        self._cache = _TVShowCache(tmdb_id, force)
        self.tmdb_id = tmdb_id
        self.details = None
        self.name = None

    def get_details(self):
        self.details = TMDb().get_request_sc('tv', self.tmdb_id, append_to_response='external_ids')
        if not self.details:
            return
        self.tvdb_id = self.details.get('external_ids', {}).get('tvdb_id')
        self.imdb_id = self.details.get('external_ids', {}).get('imdb_id')
        return self.details

    def get_name(self):
        self.name = get_unique_folder(self.details.get('name'), self.tmdb_id, BASEDIR_TV)
        return self.name

    def get_dbid(self, kodi_db=None):
        kodi_db = kodi_db or rpc.get_kodi_library('tv')
        self.dbid = kodi_db.get_info(info='dbid', imdb_id=self.imdb_id, tmdb_id=self.tmdb_id, tvdb_id=self.tvdb_id)
        return self.dbid

    def get_episode_db_info(self, season, episode, info='dbid'):
        if not self.dbid:
            return
        return rpc.KodiLibrary(dbtype='episode', tvshowid=self.dbid, logging=False).get_info(
            info=info, season=season, episode=episode)

    def get_seasons(self):
        self.seasons = self.details.get('seasons', [])
        self.s_total = len(self.seasons)
        return self.seasons

    def get_episodes(self, season):
        self.e_total = 0
        self.season_details = TMDb().get_request('tv', self.tmdb_id, 'season', season, cache_refresh=True)
        if not self.season_details:
            return []
        self.episodes = [i for i in self.season_details.get('episodes', []) if i.get('episode_number', 0) != 0]
        self.e_total = len(self.episodes)
        return self.episodes

    def make_nfo(self):
        create_nfo('tv', self.tmdb_id, self.name, basedir=BASEDIR_TV)

    def set_next(self):
        self._cache.create_new_cache(self.details.get('name', ''))
        self._cache.set_next_check(
            next_aired=self.details.get('next_episode_to_air', {}),
            last_aired=self.details.get('last_episode_to_air', {}),
            status=self.details.get('status'))
