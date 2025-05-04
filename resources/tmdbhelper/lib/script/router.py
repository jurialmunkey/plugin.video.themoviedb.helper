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


def test_func():
    import xbmcgui
    from tmdbhelper.lib.api.tmdb.api import TMDb
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.files.futils import dumps_to_file
    from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
    from tmdbhelper.lib.addon.plugin import get_version
    head = ''
    data = ''

    # data = get_version()

    # from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
    # iddb = ItemDetailsDatabase()
    # iddb.clean_expired_items()

    tmdb_api = TMDb()
    # data = tmdb_api.tmdb_database.get_nextaired(100088)
    # data = tmdb_api.tmdb_database.get_tmdb_id('movie', imdb_id='tt0078748')
    # data = tmdb_api.tmdb_database.get_tmdb_id('tv', tvdb_id=81189)
    # data = tmdb_api.tmdb_database.get_tmdb_id('tv', imdb_id='tt0903747')
    # data = tmdb_api.tmdb_database.get_tmdb_id('movie', title='aLIEN', year=1979)
    # data = tmdb_api.tmdb_database.get_tmdb_id('tv', title='Breaking Bad', year=2008)
    # data = tmdb_api.tmdb_database.get_tmdb_id('collection', title='Alien Collection')
    # data = tmdb_api.tmdb_database.get_tmdb_id('company', title='Netflix')
    # data = tmdb_api.tmdb_database.get_tmdb_id('keyword', title='aliens')
    # data = tmdb_api.tmdb_database.get_tmdb_id('person', title='danny devito')
    # data = tmdb_api.tmdb_database.get_tmdb_id_from_query('person', 'danny dev', use_details=True)
    # data = tmdb_api.tmdb_database.get_watch_providers('tv', 'AU')
    # data = tmdb_api.tmdb_database.get_certification('tv', 'AU')
    # data = tmdb_api.tmdb_database.get_tmdb_id(query='the Terminator', use_multisearch=True)
    # data = tmdb_api.tmdb_database.get_watch_providers('movie', 'AU')
    # data = tmdb_api.tmdb_database.get_keywords()

    data = tmdb_api.get_response_json('find', 'tt20603288', external_source='imdb_id')

    # trakt_api = TraktAPI()
    # path = trakt_api.get_request_url('users/hidden/dropped')
    # data = trakt_api.get_api_request(path, headers=trakt_api.headers).json()

    # sync = BaseItemFactory('season')
    # sync.tmdb_id = 79744
    # sync.season = 2
    # sync.cache_refresh = 'force'
    # sync.cache.del_database_init()
    # data = sync.data

    # sync = BaseItemFactory('episode')
    # sync.tmdb_id = 1399
    # sync.season = 2
    # sync.episode = 3

    # sync = BaseItemFactory('video')
    # sync.tmdb_id = 17419

    # sync = BaseItemFactory('movie')
    # sync.tmdb_id = 348
    # data = sync.data['infoproperties']['set.tmdb_id']
    # head = sync.item_id

    # from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
    # sync = BaseViewFactory('episodes', 'tv', 1396, season=2)
    # data = sync.data

    # sync.cache_refresh = 'never'
    # data = sync.return_basemeta_db('art_poster').item_id

    # from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
    # sync = BaseViewFactory('crewedmovies', 'person', 138)
    # data = sync.data

    # sync.extendedinfo = True

    # head = sync.item_id

    # tmdb = TMDb()
    # data = tmdb.genres
    # data = tmdb.get_response_json('configuration')
    # data = tmdb.get_response_json('tv', 249042, append_to_response=tmdb.append_to_response)

    # from tmdbhelper.lib.api.kodi.rpc import get_jsonrpc
    # method = 'VideoLibrary.GetMovies'
    # params = {
    #     'properties': [
    #         'title', 'year'
    #     ],
    #     'filter': {
    #         'and': [
    #             {'field': 'title', 'operator': 'is', 'value': 'Alien'},
    #             {'field': 'year', 'operator': 'is', 'value': '1979'}
    #         ]
    #     }
    # }
    # data = get_jsonrpc(method, params)

    xbmcgui.Dialog().textviewer(f'{head}', f'{data}')
    dumps_to_file(data, 'log_data', 'test_func.json', join_addon_data=True)


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
            lambda **kwargs: test_func(),

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
        'refresh_trakt_sync':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'refresh_trakt_sync')(**kwargs),
        'get_trakt_stats':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'get_stats')(**kwargs),
        'authenticate_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.api.trakt.api', 'TraktAPI')(force=True),
        'revoke_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.api.trakt.api', 'TraktAPI')().logout(),

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
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.maintenance', 'recache_kodidb')(),
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
