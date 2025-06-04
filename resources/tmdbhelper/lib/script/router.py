# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import re
from jurialmunkey.window import get_property
from jurialmunkey.parser import reconfigure_legacy_params
from tmdbhelper.lib.addon.logger import kodi_log
from jurialmunkey.modimp import importmodule


REGEX_WINPROP_FINDALL = r'\$WINPROP\[(.*?)\]'  # $WINPROP[key] = Window(10000).getProperty(TMDbHelper.WinProp.{key})
REGEX_WINPROP_SUB = r'\$WINPROP\[{}\]'


def test_func(test_func, dialog_output=False, **kwargs):

    from timeit import default_timer as timer
    start_time = timer()

    def finalise(head='', data='', affix=''):
        total_time = timer() - start_time
        import xbmcgui
        from tmdbhelper.lib.files.futils import dumps_to_file
        xbmcgui.Dialog().textviewer(f'{head}', f'{data if dialog_output else bool(data)}')
        dump_data = {
            'func': test_func,
            'kwgs': kwargs,
            'time': f'{total_time:.3f} sec',
            'data': data,
        },
        dump_name = f'test_func_{test_func}{affix}.json'
        dumps_to_file(dump_data, 'log_data', dump_name, join_addon_data=True)

    def test_func_response(path, **kwargs):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        head = path
        data = TMDb().get_response_json(path, **kwargs)
        return finalise(head, data)

    def test_func_trakt_response(path, **kwargs):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        head = path
        data = TraktAPI().get_response(path, **kwargs)
        data = {'headers': dict(data.headers), 'request': data.json()}
        return finalise(head, data)

    def test_func_fanarttv(ftv_type, ftv_id, **kwargs):
        from tmdbhelper.lib.api.fanarttv.api import FanartTV
        data = FanartTV().get_request(
            ftv_type, ftv_id,
            cache_force=7,  # Force dummy request caching to prevent rerequesting 404s
            cache_fallback={'dummy': None},
            cache_days=30)
        head = f'{ftv_type} {ftv_id}'
        return finalise(head, data)

    def test_func_baseitem_factory(mediatype, tmdb_id, season=None, episode=None, cache_refresh=None, del_database_init=False, attr='data'):
        from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
        sync = BaseItemFactory(mediatype)
        sync.tmdb_id = int(tmdb_id)
        sync.season = int(season) if season is not None else None
        sync.episode = int(episode) if episode is not None else None
        sync.cache_refresh = cache_refresh
        sync.cache.del_database_init() if del_database_init else None
        data = getattr(sync, attr)
        head = f'{mediatype} {tmdb_id} {season} {episode}'
        return finalise(head, data)

    def test_func_baseview_factory(import_attr, tmdb_type, tmdb_id, season=None, episode=None, filters=None, limit=None):
        from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
        sync = BaseViewFactory(import_attr, tmdb_type, int(tmdb_id), season, episode, filters, limit)
        data = sync.data
        head = f'{(import_attr, tmdb_type, int(tmdb_id))}'
        return finalise(head, data)

    def test_func_tmdb_database(import_attr, **kwargs):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        tmdb_database = TMDb().tmdb_database
        data = getattr(tmdb_database, import_attr)(**kwargs)
        head = import_attr
        return finalise(head, data)

    def test_func_get_next_episodes(tmdb_id, season, episode, player=None, **kwargs):
        import xbmcgui
        from tmdbhelper.lib.player.details import get_next_episodes
        data = get_next_episodes(tmdb_id, season, episode, player)
        head = f'{(tmdb_id, season, episode)}'
        xbmcgui.Dialog().select(head, data, useDetails=True)

    def test_func_sync_next_episodes(import_attr, **kwargs):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        from tmdbhelper.lib.api.trakt.sync.datatype import SyncNextEpisodes
        sync = SyncNextEpisodes(TraktAPI().trakt_syncdata, 'show')
        func = getattr(sync, import_attr)
        head = import_attr
        data = func(**kwargs)
        return finalise(head, data, affix=import_attr)

    def test_func_get_response_sync(path, **kwargs):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        trakt_api = TraktAPI()
        path = trakt_api.get_request_url(path, **kwargs)
        data = trakt_api.get_api_request(path, headers=trakt_api.headers)
        data = data.json()
        head = path
        return finalise(head, data)

    routes = {
        'response': test_func_response,
        'trakt_response': test_func_trakt_response,
        'baseitem_factory': test_func_baseitem_factory,
        'baseview_factory': test_func_baseview_factory,
        'tmdb_database': test_func_tmdb_database,
        'fanarttv': test_func_fanarttv,
        'get_next_episodes': test_func_get_next_episodes,
        'sync_next_episodes': test_func_sync_next_episodes,
        'get_response_sync': test_func_get_response_sync,
    }

    return routes[test_func](**kwargs)


class Script(object):
    def __init__(self, *args):
        self.params = {}
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                for i in re.findall(REGEX_WINPROP_FINDALL, value):
                    value = re.sub(
                        REGEX_WINPROP_SUB.format(i),
                        re.escape(get_property(f'WinProp.{i}')),
                        value)
                    value = re.sub(r'\\(.)', r'\1', value)  # Unescape
                self.params[key] = value.strip('\'').strip('"') if value else None
            else:
                self.params[arg] = True
        self.params = reconfigure_legacy_params(**self.params)

    routing_table = {
        'test_func':
            lambda **kwargs: test_func(**kwargs),

        # Node Maker
        'make_node':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.make_node', 'make_node')(**kwargs),

        # Kodi Utils
        'split_value':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.kodi_utils', 'split_value')(**kwargs),
        'kodi_setting':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.kodi_utils', 'kodi_setting')(**kwargs),

        # Context Menu
        'related_lists':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.context_menu', 'related_lists')(**kwargs),

        # TMDb Utils
        'sync_tmdb':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.tmdb', 'sync_tmdb')(**kwargs),
        'refresh_details':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.tmdb', 'refresh_item')(**kwargs),
        'delete_itemtype':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.tmdb', 'delete_itemtype')(**kwargs),

        # Trakt Utils
        'like_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'like_list')(**kwargs),
        'delete_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'delete_list')(**kwargs),
        'rename_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'rename_list')(**kwargs),
        'sync_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'sync_trakt')(**kwargs),
        'sort_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'sort_list')(**kwargs),
        'invalidate_trakt_sync':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'invalidate_trakt_sync')(**kwargs),
        'get_trakt_stats':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'get_stats')(**kwargs),
        'authenticate_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'authenticate_trakt')(**kwargs),
        'revoke_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'revoke_trakt')(**kwargs),

        # Image Functions
        'blur_image':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.image_functions', 'blur_image')(**kwargs),
        'image_colors':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.image_functions', 'image_colors')(**kwargs),

        # User Configuration
        'provider_allowlist':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.settings', 'configure_provider_allowlist')(),

        # Player Configuration
        'play':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.players', 'play_external')(**kwargs),
        'play_using':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.players', 'play_using')(**kwargs),
        'update_players':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.players', 'update_players')(),
        'set_defaultplayer':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.players', 'set_defaultplayer')(**kwargs),
        'set_chosenplayer':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.players', 'set_chosenplayer')(**kwargs),
        'configure_players':
            lambda **kwargs: importmodule('tmdbhelper.lib.player.configure', 'configure_players')(**kwargs),

        # Library Integration
        'add_to_library':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.library', 'add_to_library')(**kwargs),
        'user_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.library', 'add_user_list')(**kwargs),
        'library_autoupdate':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.library', 'run_autoupdate')(**kwargs),
        'monitor_userlist':
            lambda **kwargs: importmodule('tmdbhelper.lib.update.userlist', 'monitor_userlist')(),

        # Window Management
        'add_path':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.manager', 'WindowManager')(**kwargs).router(),
        'add_tmdb':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.manager', 'WindowManager')(**kwargs).router(),
        'add_dbid':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.manager', 'WindowManager')(**kwargs).router(),
        'add_query':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.manager', 'WindowManager')(**kwargs).router(),
        'close_dialog':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.manager', 'WindowManager')(**kwargs).router(),
        'reset_path':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.manager', 'WindowManager')(**kwargs).router(),
        'call_id':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.manager', 'WindowManager')(**kwargs).router(),
        'call_path':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.manager', 'WindowManager')(**kwargs).router(),
        'call_update':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.manager', 'WindowManager')(**kwargs).router(),
        'recommendations':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.recommendations', 'WindowRecommendationsManager')(**kwargs).router(),
        'wikipedia':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.kodi_utils', 'do_wikipedia_gui')(**kwargs),

        # Maintenance and Logging
        'log_request':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.logging', 'log_request')(**kwargs),
        'log_sync':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.logging', 'log_sync')(**kwargs),
        'recache_kodidb':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.maintenance', 'recache_kodidb')(confirmation=True),
        'build_awards':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.build_awards', 'build_awards')(**kwargs),
        'restart_service':
            lambda **kwargs: importmodule('tmdbhelper.lib.monitor.service', 'restart_service_monitor')()
    }

    def router(self):
        if not self.params:
            return
        routes_available = set(self.routing_table.keys())
        params_given = set(self.params.keys())
        route_taken = set.intersection(routes_available, params_given).pop()
        kodi_log(['lib.script.router - route_taken\t', route_taken], 0)
        return self.routing_table[route_taken](**self.params)
