# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import re
from jurialmunkey.window import get_property
from jurialmunkey.parser import reconfigure_legacy_params
from tmdbhelper.lib.addon.logger import kodi_log
from jurialmunkey.modimp import importmodule
from tmdbhelper.lib.addon.plugin import ADDON


REGEX_WINPROP_FINDALL = r'\$WINPROP\[(.*?)\]'  # $WINPROP[key] = Window(10000).getProperty(TMDbHelper.WinProp.{key})
REGEX_WINPROP_SUB = r'\$WINPROP\[{}\]'


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
        'sort_mdblist':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'sort_mdblist')(**kwargs),
        'invalidate_trakt_sync':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'invalidate_trakt_sync')(**kwargs),
        'get_trakt_stats':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'get_stats')(**kwargs),
        'authenticate_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'authenticate_trakt')(**kwargs),
        'revoke_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'revoke_trakt')(**kwargs),

        # Modify Functions
        'modify_identifier':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.modify_identifier', 'modify_identifier')(**kwargs),
        'modify_artwork':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.modify_artwork', 'modify_artwork')(**kwargs),

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
            lambda **kwargs: importmodule('tmdbhelper.lib.player.method.play', 'play_external')(**kwargs),
        'play_using':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.players.old', 'play_using')(**kwargs),
        'update_players':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.players.old', 'update_players')(),
        'set_defaultplayer':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.players.old', 'set_defaultplayer')(**kwargs),
        'set_chosenplayer':
            lambda **kwargs: importmodule('tmdbhelper.lib.player.method.userdefault', 'run')(**kwargs),
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
            lambda **kwargs: importmodule('tmdbhelper.lib.monitor.service', 'restart_service_monitor')(),
        'test_func':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.test', 'test_func')(**kwargs),
        'open_settings':
            lambda **kwargs: ADDON.openSettings(),
    }

    def router(self):
        if not self.params:
            return
        routes_available = set(self.routing_table.keys())
        params_given = set(self.params.keys())
        route_taken = set.intersection(routes_available, params_given).pop()
        kodi_log(['lib.script.router - route_taken\t', route_taken], 0)
        return self.routing_table[route_taken](**self.params)
