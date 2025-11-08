import xbmcvfs
import tmdbhelper.lib.api.kodi.rpc as rpc
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting, get_localized, set_setting
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.tmdate import is_unaired_timestamp, get_current_date_time
from tmdbhelper.lib.files.futils import validify_filename, get_tmdb_id_nfo

from tmdbhelper.lib.update.update import BASEDIR_MOVIE, BASEDIR_TV, STRM_MOVIE, STRM_EPISODE, create_file, create_nfo, get_unique_folder
from tmdbhelper.lib.update.cacher import _TVShowCache
from tmdbhelper.lib.update.common import LibraryCommonFunctions
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory


class LibraryLegacyConversion:

    def __init__(self, folder, tmdb_id):
        self.old_folder_name = folder
        self.tmdb_id = tmdb_id

    @cached_property
    def sync(self):
        sync = BaseItemFactory('tvshow')
        sync.tmdb_id = self.tmdb_id
        return sync

    @cached_property
    def new_folder_name(self):
        try:
            name = self.sync.data['infolabels']['tvshowtitle']
            year = self.sync.data['infolabels']['premiered'][:4]
        except (KeyError, TypeError, AttributeError):
            return
        if not name or not year:
            return
        return f'{name} ({year})'

    @cached_property
    def basedir(self):
        return BASEDIR_TV.replace('\\', '/')

    @cached_property
    def old_folder(self):
        return f'{self.basedir}{validify_filename(self.old_folder_name)}/'

    @cached_property
    def new_folder(self):
        return f'{self.basedir}{validify_filename(self.new_folder_name)}/'

    def rename(self):
        if not self.old_folder_name:
            return
        if not self.new_folder_name:
            return
        if self.old_folder_name == self.new_folder_name:
            return
        xbmcvfs.rename(self.old_folder, self.new_folder)


class LibraryAdder(LibraryCommonFunctions):

    tv = None
    hide_unaired = True
    hide_nodate = True

    log_folder = 'log_library'
    _msg_title = 'TMDbHelper Library'

    @cached_property
    def _msg_start(self):
        return get_localized(32166)

    @cached_property
    def auto_update(self):
        return get_setting('auto_update')

    @cached_property
    def listdir_basedir_tv(self):
        from xbmcvfs import listdir
        return listdir(BASEDIR_TV)[0]

    @cached_property
    def listdir_basedir_tv_nfos(self):
        return [
            i for i in (
                (get_tmdb_id_nfo(BASEDIR_TV, f), f)
                for f in self.listdir_basedir_tv
            ) if i[0] and i[1]
        ]

    def convert_legacy_folders(self):
        """ Converts old style tvshow folders without years so that they have years """

        if get_setting('legacy_conversion'):
            return

        # Update each show in folder
        for x, (tmdb_id, folder) in enumerate(self.listdir_basedir_tv_nfos):
            self._update(x, len(self.listdir_basedir_tv_nfos), message=f'{get_localized(32167)} {folder}...')
            LibraryLegacyConversion(folder, tmdb_id).rename()

        # Mark as complete and set to clean library
        set_setting('legacy_conversion', True)
        self.clean_library = True

    def update_tvshows(self, force=False, **kwargs):

        # Update each show in folder
        for x, (tmdb_id, folder) in enumerate(self.listdir_basedir_tv_nfos):
            self._update(x, len(self.listdir_basedir_tv_nfos), message=f'{get_localized(32167)} {folder}...')
            self.add_tvshow(tmdb_id=tmdb_id, force=force)

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


def add_to_library(info, busy_spinner=True, library_adder=None, finished=True, **kwargs):
    if not info:
        return

    if not library_adder:
        library_adder = LibraryAdder(busy_spinner)
        library_adder.convert_legacy_folders()

    routes = {
        'movie': library_adder.add_movie,
        'tv': library_adder.add_tvshow,
        'trakt': library_adder.add_userlist,
        'update': library_adder.update_tvshows,
    }

    try:
        routes[info](**kwargs)
    except KeyError:
        pass

    if not finished:
        return library_adder

    library_adder.__exit__()
