import sys
from resources.lib.addon.logger import kodi_log
from resources.lib.addon.parser import parse_paramstring, reconfigure_legacy_params

""" Lazyimports """
from resources.lib.addon.modimp import lazyimport_modules, lazyimport_module
get_container = None  # resources.lib.items.routes
Players = None  # resources.lib.player.players
related_lists = None  # resources.lib.script.method
TMDb = None  # resources.lib.api.tmdb.api


class Router():
    def __init__(self):
        # plugin:// params configuration
        self.handle = int(sys.argv[1])  # plugin:// handle
        self.paramstring = sys.argv[2][1:]  # plugin://plugin.video.themoviedb.helper?paramstring
        self.params = reconfigure_legacy_params(**parse_paramstring(self.paramstring))  # paramstring dictionary

    @lazyimport_modules(globals(), (
        {'module_name': 'resources.lib.player.players', 'import_attr': 'Players'},
        {'module_name': 'resources.lib.api.tmdb.api', 'import_attr': 'TMDb'}))
    def play_external(self):
        kodi_log(['lib.container.router - Attempting to play item\n', self.params], 1)
        if not self.params.get('tmdb_id'):
            self.params['tmdb_id'] = TMDb().get_tmdb_id(**self.params)
        Players(**self.params).play(handle=self.handle if self.handle != -1 else None)

    @lazyimport_modules(globals(), (
        {'module_name': 'resources.lib.script.method', 'import_attr': 'related_lists'},
        {'module_name': 'resources.lib.api.tmdb.api', 'import_attr': 'TMDb'}))
    def context_related(self):
        if not self.params.get('tmdb_id'):
            self.params['tmdb_id'] = TMDb().get_tmdb_id(**self.params)
        self.params['container_update'] = True
        related_lists(include_play=True, **self.params)

    @lazyimport_module(globals(), 'resources.lib.items.routes', import_attr='get_container')
    def get_directory(self):
        container = get_container(self.params.get('info'))(self.handle, self.paramstring, **self.params)
        container.get_tmdb_id()  # TODO: Only get this as necessary
        container.get_directory()

    def run(self):
        if self.params.get('info') == 'play':
            return self.play_external()
        if self.params.get('info') == 'related':
            return self.context_related()
        self.get_directory()
