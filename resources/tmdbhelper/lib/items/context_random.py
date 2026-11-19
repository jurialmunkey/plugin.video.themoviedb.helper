from urllib.parse import parse_qsl, quote, urlencode
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import PLUGINPATH


class PlayRandomPath:
    """A directory URL that can be traversed without running a menu action."""

    excluded_routes = (
        'dir_settings',
        'user_discover',
        'trakt_authenticate',
        'trakt_discover',
        'fanart',
        'posters',
        'images',
        'episode_thumbs',
        'reviews',
        'videos',
    )
    search_routes = ('search', 'trakt_searchlists', 'mdblist_searchlists')

    def __init__(self, path):
        self.path = path

    @cached_property
    def params(self):
        return self.get_params()

    def get_params(self):
        query = self.path.partition('?')[2].split('&&')[0]
        return dict(parse_qsl(query, keep_blank_values=True))

    @cached_property
    def is_folder(self):
        return self.get_is_folder()

    def get_is_folder(self):
        if self.path.partition('?')[0] != PLUGINPATH:
            return False
        if self.params.get('info') in self.excluded_routes:
            return False
        if self.params.get('info') in ('play', 'details'):
            return False
        if self.params.get('clear_cache') or self.params.get('method'):
            return False
        if self.params.get('info') in self.search_routes and not self.params.get('query'):
            return False
        return True

    @cached_property
    def paramstring(self):
        return self.get_paramstring()

    def get_paramstring(self):
        params = self.params.copy()
        if params.get('info') == 'flatseasons':
            # Pick a season before an episode, regardless of the display preference.
            params['info'] = 'seasons'
        params.pop('widget', None)
        params.pop('reload', None)
        params.pop('update_listing', None)
        secondary_paths = self.path.partition('?')[2].split('&&')[1:]
        return '&&'.join([urlencode(sorted(params.items())), *secondary_paths])


class PlayRandomContextMenu:
    """Share item eligibility between the context menu and random traversal."""

    def __init__(self, listitem):
        self.listitem = listitem

    @cached_property
    def folder(self):
        return self.get_folder()

    def get_folder(self):
        return PlayRandomPath(self.listitem.url)

    @cached_property
    def is_folder(self):
        return self.get_is_folder()

    def get_is_folder(self):
        if not self.listitem.is_folder or self.listitem.next_page:
            return False
        if self.listitem.infoproperties.get('specialseason'):
            return False
        return self.folder.is_folder

    @cached_property
    def is_playable(self):
        return self.get_is_playable()

    def get_is_playable(self):
        if self.listitem.is_folder:
            return False
        if self.listitem.mediatype not in ('movie', 'episode'):
            return False
        return self.folder.params.get('info') == 'play'

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        if not self.is_folder:
            return []
        path = quote(f'{PLUGINPATH}?{self.folder.paramstring}', safe='')
        return [
            (
                '$ADDON[plugin.video.themoviedb.helper 32767]',
                f'RunScript(plugin.video.themoviedb.helper,play_random={path})',
            ),
        ]
