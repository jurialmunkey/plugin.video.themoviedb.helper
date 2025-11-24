from xbmc import Monitor
from xbmcgui import Dialog
from contextlib import suppress
import jurialmunkey.window as window
from jurialmunkey.parser import try_int, parse_paramstring, reconfigure_legacy_params
from tmdbhelper.lib.addon.plugin import get_localized, executebuiltin
from tmdbhelper.lib.addon.dialog import BusyDialog
from tmdbhelper.lib.query.database.database import FindQueriesDatabase
from tmdbhelper.lib.window.event_loop import EventLoop
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.window.constants import (
    PREFIX_INSTANCE,
    PREFIX_ADDPATH,
    PREFIX_PATH,
    PREFIX_COMMAND,
    PREFIX_POSITION,
    PREFIX_CURRENT,
    SV_ROUTES
)
from tmdbhelper.lib.addon.logger import kodi_log


class PathConstructor:
    def __init__(self, tmdb_type=None, tmdb_id=None, season=None, episode=None, dbid=None, **kwargs):
        self.params = kwargs
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        self.dbid = dbid

    @cached_property
    def tmdb_type_path(self):
        if self.tmdb_type in ('season', 'episode'):
            return 'tv'
        return self.tmdb_type

    @cached_property
    def pstr_season(self):
        if self.tmdb_type_path != 'tv':
            return ''
        if self.season is None:
            return ''
        return f'&season={self.season}'

    @cached_property
    def pstr_affix(self):
        if not self.pstr_season:
            return ''
        if self.episode is None:
            return self.pstr_season
        return f'{self.pstr_season}&episode={self.episode}'

    @cached_property
    def info(self):
        try:
            return self.params.get('info') or {
                'collection': 'get_dbitem_movieset_details',
                'movie': 'get_dbitem_movie_details',
                'tv': 'get_dbitem_tvshow_details',
                'season': 'get_dbitem_season_details',
                'episode': 'get_dbitem_episode_details',
            }[self.tmdb_type]
        except KeyError:
            return

    @cached_property
    def path(self):

        if self.dbid and self.info in SV_ROUTES.keys():
            base = 'plugin://script.skinvariables/'
            pstr = f'info={self.info}&dbid={self.dbid}'
            return f'{base}?{pstr}'

        if self.tmdb_type and self.tmdb_id:
            base = 'plugin://plugin.video.themoviedb.helper/'
            pstr = f'info=details&tmdb_type={self.tmdb_type_path}&tmdb_id={self.tmdb_id}{self.pstr_affix}'
            return f'{base}?{pstr}'

        return ''

    @cached_property
    def is_valid(self):
        if not self.path:
            return False
        if self.path == window.get_property(PREFIX_CURRENT):  # Same path as current so skip as user double clicked
            return False
        return True


def PathConstructorFactory(path):
    try:
        base, pstr = path.split('?')
    except (AttributeError, IndexError):
        return
    if not pstr:
        return
    prms = parse_paramstring(pstr)
    prms = reconfigure_legacy_params(**prms)
    return PathConstructor(**prms)


class QueryConstructor:
    def __init__(self, query, tmdb_type, season=None, episode=None, separator=' / '):
        self.query = query
        self.tmdb_type = tmdb_type
        self.separator = separator
        self.season = season
        self.episode = episode

    @cached_property
    def queries(self):
        if self.separator and self.separator in self.query:
            return self.query.split(self.separator)
        return [self.query]

    @cached_property
    def choice(self):
        x = Dialog().select(get_localized(32236), self.queries) if len(self.queries) > 1 else 0
        return self.queries[x] if x != -1 else None

    @cached_property
    def tmdb_id(self):
        if self.choice is None:
            return
        with BusyDialog():
            return FindQueriesDatabase().get_tmdb_id_from_query(
                self.tmdb_type,
                self.choice,
                header=f'{self.choice} ({self.tmdb_type})',
                use_details=True,
                auto_single=True

            )

    @cached_property
    def path(self):
        if not self.tmdb_id:
            return Dialog().notification('TMDbHelper', get_localized(32310).format(self.choice))
        return PathConstructor(self.tmdb_type, self.tmdb_id, self.season, self.episode).path


class WindowManager(EventLoop):

    position = 0
    added_path = None
    current_path = None
    return_info = False
    first_run = True
    exit = False

    def __init__(self, **kwargs):
        self.window_id = try_int(kwargs.get('call_auto'), fallback=None)
        self.params = kwargs

    @cached_property
    def xbmc_monitor(self):
        return Monitor()

    @cached_property
    def kodi_id(self):
        if self.window_id < 10000:
            return self.window_id + 10000
        return self.window_id

    @property
    def base_id(self):
        if self.first_run:  # On first run the base window won't be open yet so don't check for it
            return
        return self.window_id

    def reset_properties(self):
        self.position = 0
        self.added_path = None
        self.current_path = None
        window.get_property(PREFIX_COMMAND, clear_property=True)
        window.get_property(PREFIX_CURRENT, clear_property=True)
        window.get_property(PREFIX_POSITION, clear_property=True)
        window.get_property(f'{PREFIX_PATH}0', clear_property=True)
        window.get_property(f'{PREFIX_PATH}1', clear_property=True)
        kodi_log(f'Window Manager [ACTION] reset_properties', 2)

    def set_properties(self, position=1, path=None):
        self.position = position
        self.added_path = path or ''
        window.get_property(PREFIX_CURRENT, set_property=path)
        window.get_property(f'{PREFIX_PATH}{position}', set_property=path)
        window.get_property(PREFIX_POSITION, set_property=position)
        kodi_log(f'Window Manager [ACTION] set_properties {position}\n{path}', 2)

    def add_origin(self):
        if not self.origin_path:
            return
        self.position += 1
        self.set_properties(self.position, self.origin_path)
        self.params['return'] = True
        kodi_log(f'Window Manager [ACTION] add_origin {self.position}\n{self.origin_path}', 2)

    @cached_property
    def origin_path_kwgs(self):
        origin_path_kwgs = {
            'tmdb_type': self.params.get('origin_tmdb_type'),
            'tmdb_id': self.params.get('origin_tmdb_id'),
            'dbid': self.params.get('origin_dbid'),
            'season': self.params.get('origin_season'),
            'episode': self.params.get('origin_episode'),
        }
        return {k: v for k, v in origin_path_kwgs.items() if v}

    @cached_property
    def origin_path(self):
        return PathConstructor(**self.origin_path_kwgs).path

    @property
    def is_running(self):
        return bool(window.get_property(PREFIX_INSTANCE))

    def call_auto(self):
        kodi_log(f'Window Manager [ACTION] call_auto', 2)
        # Already instance running and has window open so let's exit
        if self.is_running:
            kodi_log(f'Window Manager [ACTION] call_auto running...', 2)
            return
        # Reset properties back to init
        self.reset_properties()
        # Add a return origin if available
        self.add_origin()
        kodi_log(f'Window Manager [ACTION] call_auto event_loop', 2)
        # Start up our service to monitor the windows
        return self.event_loop()

    def add_path(self, path):
        return self.add_path_to_history(PathConstructorFactory(path))

    def add_tmdb(self, tmdb_id, tmdb_type, season=None, episode=None):
        return self.add_path_to_history(PathConstructor(tmdb_id=tmdb_id, tmdb_type=tmdb_type, season=season, episode=episode))

    def add_dbid(self, dbid, tmdb_type):
        return self.add_path_to_history(PathConstructor(dbid=dbid, tmdb_type=tmdb_type))

    def add_path_to_history(self, path_constructor):
        kodi_log(f'Window Manager [ACTION] add_path_to_history', 2)
        if not path_constructor or not path_constructor.is_valid:
            return
        kodi_log(f'Window Manager [ACTION] add_path_to_history adding {path_constructor.path}', 2)
        window.wait_for_property(PREFIX_ADDPATH, path_constructor.path, True, poll=0.3)
        kodi_log(f'Window Manager [ACTION] add_path_to_history added!', 2)
        self.call_auto()

    def add_query(self, query, tmdb_type, season=None, episode=None, separator=' / '):
        kodi_log(f'Window Manager [ACTION] add_query {query} {tmdb_type}', 2)
        path = QueryConstructor(query, tmdb_type, season, episode, separator).path
        return self.add_path(path) if path else None

    def close_dialog(self):
        kodi_log(f'Window Manager [ACTION] close_dialog', 2)
        window.wait_for_property(PREFIX_COMMAND, 'exit', True, poll=0.3)
        self._call_exit()
        self._on_exit()
        self.call_window()

    def get_playmedia_builtin(self):
        params = [f'\"{self.params["playmedia"]}\"', f'playlist_type_hint={self.params.get("playlist_type_hint") or "1"}']
        for k in ('resume', 'noresume', 'isdir', ):
            if not self.params.get(k):
                continue
            params.append(k)
        for k in ('playoffset', ):
            if not self.params.get(k):
                continue
            params.append(f'{k}={self.params[k]}')
        params = ','.join(params)
        return f'PlayMedia({params})'

    def call_window(self):
        if self.params.get('executebuiltin'):
            kodi_log(f'Window Manager [ACTION] call_window executebuiltin\n{self.params}', 2)
            return executebuiltin(f'{self.params["executebuiltin"]}')
        if self.params.get('playmedia'):
            kodi_log(f'Window Manager [ACTION] call_window playmedia\n{self.params}', 2)
            return executebuiltin(self.get_playmedia_builtin())
        if self.params.get('call_id'):
            kodi_log(f'Window Manager [ACTION] call_window call_id\n{self.params}', 2)
            return executebuiltin(f'ActivateWindow({self.params["call_id"]})')
        if self.params.get('call_path'):
            kodi_log(f'Window Manager [ACTION] call_window call_path\n{self.params}', 2)
            return executebuiltin(f'ActivateWindow(videos, {self.params["call_path"]}, return)')
        if self.params.get('call_update'):
            kodi_log(f'Window Manager [ACTION] call_window call_update\n{self.params}', 2)
            return executebuiltin(f'Container.Update({self.params["call_update"]})')

    def router(self):
        with suppress(KeyError):
            return self.add_path(self.params['add_path'])
        with suppress(KeyError):
            return self.add_dbid(self.params['add_dbid'], self.params['tmdb_type'])
        with suppress(KeyError):
            return self.add_tmdb(self.params['add_tmdb'], self.params['tmdb_type'], self.params.get('season'), self.params.get('episode'))
        with suppress(KeyError):
            return self.add_query(self.params['add_query'], self.params['tmdb_type'], self.params.get('season'), self.params.get('episode'))
        if self.params.get('close_dialog') or self.params.get('reset_path'):
            return self.close_dialog()
        return self.call_window()
