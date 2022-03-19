import sys
from resources.lib.addon.logger import kodi_log
from resources.lib.addon.parser import parse_paramstring, reconfigure_legacy_params

""" Lazyimports """
from resources.lib.addon.modimp import lazyimport_module, lazyimport_modules
OldContainer = None  # resources.lib.items.oldcontainer
Players = None  # resources.lib.player.players
related_lists = None  # resources.lib.script.router
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
    def play_external(self, **kwargs):
        kodi_log(['lib.container.router - Attempting to play item\n', kwargs], 1)
        if not kwargs.get('tmdb_id'):
            kwargs['tmdb_id'] = TMDb().get_tmdb_id(**kwargs)
        Players(**kwargs).play(handle=self.handle if self.handle != -1 else None)

    @lazyimport_modules(globals(), (
        {'module_name': 'resources.lib.script.router', 'import_attr': 'related_lists'},
        {'module_name': 'resources.lib.api.tmdb.api', 'import_attr': 'TMDb'}))
    def context_related(self, **kwargs):
        if not kwargs.get('tmdb_id'):
            kwargs['tmdb_id'] = TMDb().get_tmdb_id(**kwargs)
        kwargs['container_update'] = True
        related_lists(include_play=True, **kwargs)

    @lazyimport_module(globals(), 'resources.lib.items.oldcontainer', import_attr='Container', import_as="OldContainer")
    def get_directory(self):
        container = OldContainer(self.handle, self.paramstring, **self.params)
        container.get_directory()

    def run(self):
        if self.params.get('info') == 'play':
            return self.play_external(**self.params)
        if self.params.get('info') == 'related':
            return self.context_related(**self.params)
        self.get_directory()
