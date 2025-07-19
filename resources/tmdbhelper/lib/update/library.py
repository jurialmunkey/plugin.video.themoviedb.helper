import xbmcvfs
import tmdbhelper.lib.api.kodi.rpc as rpc
from jurialmunkey.ftools import cached_property
from xbmcgui import DialogProgressBG
from tmdbhelper.lib.addon.plugin import get_setting, get_localized, set_setting
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.tmdate import is_unaired_timestamp, get_current_date_time
from tmdbhelper.lib.files.futils import validify_filename, get_tmdb_id_nfo
from tmdbhelper.lib.update.logger import _LibraryLogger
from tmdbhelper.lib.update.update import BASEDIR_MOVIE, BASEDIR_TV, STRM_MOVIE, STRM_EPISODE, create_file, create_nfo, get_unique_folder
from tmdbhelper.lib.update.cacher import _TVShowCache
from tmdbhelper.lib.update.common import LibraryCommonFunctions
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory


def add_to_library(info, busy_spinner=True, library_adder=None, finished=True, **kwargs):
    if not info:
        return
    if not library_adder:
        library_adder = LibraryAdder(busy_spinner)
        library_adder._start()
        if not get_setting('legacy_conversion'):
            library_adder.legacy_conversion()
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


class LibraryAdder(LibraryCommonFunctions):
    def __init__(self, busy_spinner=True):
        self.kodi_db_movies = rpc.get_kodi_library('movie', cache_refresh=True)
        self.kodi_db_tv = rpc.get_kodi_library('tv', cache_refresh=True)
        self.p_dialog = DialogProgressBG() if busy_spinner else None
        self.auto_update = get_setting('auto_update')
        self._log = _LibraryLogger()
        self.tv = None
        self.hide_unaired = True
        self.hide_nodate = True
        self.debug_logging = True
        self.clean_library = False
        self._msg_start = get_localized(32166)
        self._msg_title = 'TMDbHelper Library'

    def get_tv_folder_nfos(self):
        nfos = []
        nfos_append = nfos.append  # For speed since we can't do a list comp easily here
        for f in xbmcvfs.listdir(BASEDIR_TV)[0]:
            tmdb_id = get_tmdb_id_nfo(BASEDIR_TV, f)
            nfos_append({'tmdb_id': tmdb_id, 'folder': f}) if tmdb_id else None
        return nfos

    def _legacy_conversion(self, folder, tmdb_id):
        # Get details

        sync = BaseItemFactory('tvshow')
        sync.tmdb_id = tmdb_id

        try:
            details_name = sync.data['infolabels']['tvshowtitle']
            details_year = sync.data['infolabels']['premiered'][:4]
        except (KeyError, TypeError, AttributeError):
            return

        if not details_name or not details_year:
            return

        # Get new name and compare to old name
        name = f'{details_name} ({details_year})'
        if folder == name:
            return  # Skip if already converted

        # Convert name
        basedir = BASEDIR_TV.replace('\\', '/')
        old_folder = f'{basedir}{validify_filename(folder)}/'
        new_folder = f'{basedir}{validify_filename(name)}/'
        xbmcvfs.rename(old_folder, new_folder)

    def legacy_conversion(self, confirm=True):
        """ Converts old style tvshow folders without years so that they have years """
        nfos = self.get_tv_folder_nfos()

        # Update each show in folder
        nfos_total = len(nfos)
        for x, i in enumerate(nfos):
            folder, tmdb_id = i['folder'], i['tmdb_id']
            self._update(x, nfos_total, message=f'{get_localized(32167)} {folder}...')
            self._legacy_conversion(folder, tmdb_id)

        # Mark as complete and set to clean library
        set_setting('legacy_conversion', True)
        self.clean_library = True

    def update_tvshows(self, force=False, **kwargs):
        nfos = self.get_tv_folder_nfos()

        # Update each show in folder
        nfos_total = len(nfos)
        for x, i in enumerate(nfos):
            self._update(x, nfos_total, message=f'{get_localized(32167)} {i["folder"]}...')
            self.add_tvshow(tmdb_id=i['tmdb_id'], force=force)

        # Update last updated stamp
        set_setting('last_autoupdate', f'Last updated {get_current_date_time()}', 'str')

    def add_movie(self, tmdb_id=None, **kwargs):
        if not tmdb_id:
            return

        # Get movie details
        sync = BaseItemFactory('movie')
        sync.tmdb_id = tmdb_id

        try:
            details_name = sync.data['infolabels']['title']
            details_year = sync.data['infolabels']['premiered'][:4]
            details_imdb = sync.data['unique_ids']['imdb']
        except (KeyError, TypeError, AttributeError):
            pass

        if not details_name or not details_year:
            return

        name = f'{details_name} ({details_year})'

        # Only add strm if not in library
        file = self.kodi_db_movies.get_info(info='file', imdb_id=details_imdb, tmdb_id=tmdb_id)

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

        if not self.tv.details:
            return  # Skip if no details found on TMDb
        if not self.tv.name:
            return  # Skip if we don't have a folder name for some reason

        self.tv.make_nfo()
        self.tv.set_next()

        # Add seasons
        for x, season in enumerate(self.tv.seasons):
            self._update(x, len(self.tv.seasons), message=f'{get_localized(32167)} {self.tv.name} - {get_localized(20373)} {season.number}...')  # Update our progress dialog
            self._add_season(season)

        # Store details about what we did into the cache
        self.tv._cache.set_cache()

        # Return our playlist rule tuple
        return ('title', self.tv.tvshowtitle)

    def _add_season(self, season):
        folder = f'Season {season.number}'

        # Skip if we've added season before and it isn't the most recent season
        # We still add most recent season even if we added it before because it might currently be airing
        if self._log._add('tv', self.tv.tmdb_id, self.tv._cache.is_added_season(season.number), season=season.number):
            return

        # Add our episodes
        for x, episode in enumerate(season.episodes, 1):
            self._add_episode(episode, folder)
            self._update(x, len(season.episodes))

        # Store a season value of where we got up to
        if len(season.episodes) > 2 and season.premiered and not is_unaired_timestamp(season.premiered, self.hide_nodate):
            self.tv._cache.my_history['latest_season'] = try_int(season.number)

    def _add_episode(self, episode, folder):
        self.tv._cache.my_history['episodes'].append(episode.filename)

        # Skip episodes we added in the past
        if self._log._add('tv', self.tv.tmdb_id, self.tv._cache.is_added_episode(episode.filename), season=episode.season, episode=episode.number):
            return

        # Skip future episodes
        if self.hide_unaired and is_unaired_timestamp(episode.premiered, self.hide_nodate):
            self.tv._cache.my_history['skipped'].append(episode.filename)
            self._log._add('tv', self.tv.tmdb_id, 'unaired episode', season=episode.season, episode=episode.number, air_date=episode.premiered)
            return

        # Check if item has already been added
        file = self.tv.get_episode_db_info(episode.season, episode.number, info='file')
        if file:
            self._log._add('tv', self.tv.tmdb_id, 'found in library', season=episode.season, episode=episode.number, path=file)
            return

        # Add our strm file
        file = create_file(STRM_EPISODE.format(self.tv.tmdb_id, episode.season, episode.number), episode.filename, self.tv.name, folder, basedir=BASEDIR_TV)
        self._log._add('tv', self.tv.tmdb_id, 'added strm file', season=episode.season, episode=episode.number, path=file)


class _MixinGetDetailsKey:
    def get_details_key(self, key, subkey='infolabels', fallback=''):
        try:
            return self.details[subkey][key]
        except (KeyError, TypeError, AttributeError):
            return fallback


class _Episode(_MixinGetDetailsKey):
    def __init__(self, tmdb_id, details):
        self.tmdb_id = tmdb_id
        self.details = details

    @cached_property
    def filename(self):
        return validify_filename(f'S{try_int(self.season):02d}E{try_int(self.number):02d} - {self.name}')

    @cached_property
    def number(self):
        return self.get_details_key('episode', fallback=0)

    @cached_property
    def season(self):
        return self.get_details_key('season', fallback=0)

    @cached_property
    def name(self):
        return self.get_details_key('title')

    @cached_property
    def premiered(self):
        return self.get_details_key('premiered')


class _Season(_MixinGetDetailsKey):
    def __init__(self, tmdb_id, details):
        self.tmdb_id = tmdb_id
        self.details = details

    @cached_property
    def number(self):
        return self.get_details_key('season', fallback=0)

    @cached_property
    def premiered(self):
        return self.get_details_key('premiered')

    @cached_property
    def episodes(self):
        try:
            sync = BaseViewFactory('episodes', 'tv', int(self.tmdb_id), season=self.number)
        except TypeError:
            return []
        if not sync.data:
            return []
        return [i for i in (_Episode(self.tmdb_id, episode) for episode in sync.data) if i.number != 0]


class _TVShow(_MixinGetDetailsKey):
    def __init__(self, tmdb_id, force=False):
        self._cache = _TVShowCache(tmdb_id, force)
        self.tmdb_id = tmdb_id

    @cached_property
    def name(self):
        name = f'{self.tvshowtitle} ({self.year})' if self.year else self.tvshowtitle
        return get_unique_folder(name, self.tmdb_id, BASEDIR_TV)

    @cached_property
    def tvshowtitle(self):
        return self.get_details_key('tvshowtitle')

    @cached_property
    def year(self):
        return self.get_details_key('year')

    @cached_property
    def tvdb_id(self):
        return self.get_details_key('tvdb', subkey='unique_ids')

    @cached_property
    def imdb_id(self):
        return self.get_details_key('imdb', subkey='unique_ids')

    @cached_property
    def details(self):
        sync = BaseItemFactory('tvshow')
        sync.tmdb_id = self.tmdb_id
        return sync.data

    @cached_property
    def dbid(self):
        return rpc.get_kodi_library('tv').get_info(
            info='dbid',
            imdb_id=self.imdb_id,
            tmdb_id=self.tmdb_id,
            tvdb_id=self.tvdb_id
        )

    def get_episode_db_info(self, season, episode, info='dbid'):
        if not self.dbid:
            return
        return rpc.KodiLibrary(dbtype='episode', tvshowid=self.dbid, logging=False).get_info(
            info=info,
            season=season,
            episode=episode
        )

    @cached_property
    def seasons(self):
        try:
            sync = BaseViewFactory('seasons', 'tv', int(self.tmdb_id))
        except TypeError:
            return []
        if not sync.data:
            return []
        return [i for i in (_Season(self.tmdb_id, season) for season in sync.data) if i.number != 0]

    def make_nfo(self):
        create_nfo('tv', self.tmdb_id, self.name, basedir=BASEDIR_TV)

    def set_next(self):
        self._cache.create_new_cache(self.name)
        self._cache.set_next_check(  # TODO: FIX ME
            next_aired=self.details.get('next_episode_to_air', {}),
            last_aired=self.details.get('last_episode_to_air', {}),
            status=self.details.get('status'))
