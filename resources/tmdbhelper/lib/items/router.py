from urllib.parse import unquote_plus
from jurialmunkey.parser import parse_paramstring, reconfigure_legacy_params


class Router():
    def __init__(self, handle, paramstring):
        # plugin:// params configuration
        self.handle = handle  # plugin:// handle
        self.paramstring, *secondary_params = paramstring.split('&&')  # plugin://plugin.video.themoviedb.helper?paramstring
        self.params = reconfigure_legacy_params(**parse_paramstring(self.paramstring))  # paramstring dictionary
        self.params.update(self.configure_paths(secondary_params))

    def configure_paths(self, secondary_params):
        paths = [unquote_plus(self.params.pop(k)) for k in tuple(self.params.keys()) if k.startswith('paths')]
        paths.extend([unquote_plus(i) for i in secondary_params])
        return {'paths': paths} if paths else {}

    def play_external(self):
        from tmdbhelper.lib.player.method.play import play_external
        play_external(handle=self.handle if self.handle != -1 else None, **self.params)

    def get_directory(self, items_only=False, build_items=True):
        from tmdbhelper.lib.items.routes import get_container
        container = get_container(self.params.get('info'))(self.handle, self.paramstring, **self.params)
        container.get_tmdb_id()  # TODO: Only get this as necessary
        return container.get_directory(items_only, build_items)

    def run(self):
        if self.params.get('info') == 'play':
            return self.play_external()
        self.get_directory()
