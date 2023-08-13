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
        'authenticate_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.api.trakt.api', 'TraktAPI')(force=True),
        'revoke_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.api.trakt.api', 'TraktAPI')().logout(),
        'recache_kodidb':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'mem_cache_kodidb')(),
        'build_awards':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.awards', 'build_awards')(**kwargs),
        'make_node':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'make_node')(**kwargs),
        'split_value':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'split_value')(**kwargs),
        'kodi_setting':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'kodi_setting')(**kwargs),
        'sync_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'sync_trakt')(**kwargs),
        'sort_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'sort_list')(**kwargs),
        'manage_artwork':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'manage_artwork')(**kwargs),
        'select_artwork':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'select_artwork')(**kwargs),
        'refresh_details':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'refresh_details')(**kwargs),
        'related_lists':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'related_lists')(**kwargs),
        'user_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'user_list')(**kwargs),
        'like_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'like_list')(**kwargs),
        'delete_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'delete_list')(**kwargs),
        'rename_list':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'rename_list')(**kwargs),
        'blur_image':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'blur_image')(**kwargs),
        'image_colors':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'image_colors')(**kwargs),
        'provider_allowlist':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'provider_allowlist')(),
        'monitor_userlist':
            lambda **kwargs: importmodule('tmdbhelper.lib.update.userlist', 'monitor_userlist')(),
        'update_players':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'update_players')(),
        'set_defaultplayer':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'set_defaultplayer')(**kwargs),
        'set_chosenplayer':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'set_chosenplayer')(**kwargs),
        'configure_players':
            lambda **kwargs: importmodule('tmdbhelper.lib.player.configure', 'configure_players')(**kwargs),
        'library_autoupdate':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'library_autoupdate')(**kwargs),
        'log_request':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'log_request')(**kwargs),
        'log_sync':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'log_sync')(**kwargs),
        'delete_cache':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'delete_cache')(**kwargs),
        'wikipedia':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'do_wikipedia_gui')(**kwargs),
        'recommendations':
            lambda **kwargs: importmodule('tmdbhelper.lib.window.recommendations', 'WindowRecommendationsManager')(**kwargs).router(),
        'play':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'play_external')(**kwargs),
        'play_using':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'play_using')(**kwargs),
        'add_to_library':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method', 'add_to_library')(**kwargs),
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
