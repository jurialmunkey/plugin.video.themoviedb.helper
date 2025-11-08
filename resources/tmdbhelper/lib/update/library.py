from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting, get_localized, set_setting
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.tmdate import is_unaired_timestamp, get_current_date_time
from tmdbhelper.lib.files.futils import validify_filename, get_tmdb_id_nfo

from tmdbhelper.lib.update.update import BASEDIR_TV, STRM_EPISODE, create_file
from tmdbhelper.lib.update.common import LibraryCommonFunctions


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
        from tmdbhelper.lib.update.legacy import LibraryLegacyConversion
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
        from tmdbhelper.lib.update.items.movie import LibraryMovie
        add_movie = LibraryMovie(tmdb_id)
        if not add_movie.name:
            return
        add_movie.library_file = self.get_movie_info(info='file', imdb_id=add_movie.imdb_id, tmdb_id=add_movie.tmdb_id)
        self._log._add('movie', add_movie.tmdb_id, add_movie.log_message, path=add_movie.file)
        return add_movie.playlist_rule

    def add_tvshow(self, tmdb_id=None, force=False, **kwargs):
        from tmdbhelper.lib.update.items.tvshow import LibraryTvshow
        self.tv = LibraryTvshow(tmdb_id, force)

        # Return playlist rule if we don't need to check show this time
        if self._log._add('tv', tmdb_id, self.tv.cache.get_next_check()):
            return ('title', self.tv.cache.cache_info.get('name'))

        if not self.tv.sync_data:
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
        self.tv.cache.set_cache()

        # Return our playlist rule tuple
        return ('title', self.tv.tvshowtitle)

    def _add_season(self, season):
        folder = f'Season {season.number}'

        # Skip if we've added season before and it isn't the most recent season
        # We still add most recent season even if we added it before because it might currently be airing
        if self._log._add('tv', self.tv.tmdb_id, self.tv.cache.is_added_season(season.number), season=season.number):
            return

        # Add our episodes
        for x, episode in enumerate(season.episodes, 1):
            self._add_episode(episode, folder)
            self._update(x, len(season.episodes))

        # Store a season value of where we got up to
        if len(season.episodes) > 2 and season.premiered and not is_unaired_timestamp(season.premiered, self.hide_nodate):
            self.tv.cache.my_history['latest_season'] = try_int(season.number)

    def _add_episode(self, episode, folder):
        self.tv.cache.my_history['episodes'].append(episode.filename)

        # Skip episodes we added in the past
        if self._log._add('tv', self.tv.tmdb_id, self.tv.cache.is_added_episode(episode.filename), season=episode.season, episode=episode.number):
            return

        # Skip future episodes
        if self.hide_unaired and is_unaired_timestamp(episode.premiered, self.hide_nodate):
            self.tv.cache.my_history['skipped'].append(episode.filename)
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
