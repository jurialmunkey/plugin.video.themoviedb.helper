# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting


CONTEXT_MENU_ITEMS = {
    # Browse Lists
    '$ADDON[plugin.video.themoviedb.helper 32235]': {
        'command': 'RunScript(plugin.video.themoviedb.helper,related_lists,{})',
        'setting': 'contextmenu_related_lists',
        'episode': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}', 'episode': '{episode}'},
        'other': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'}
    },
    # Sync Options
    '$ADDON[plugin.video.themoviedb.helper 32549]': {
        'command': 'RunScript(plugin.video.themoviedb.helper,sync_options,{})',
        'setting': 'contextmenu_sync_options',
        'season': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}'},
        'episode': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}', 'episode': '{episode}'},
        'other': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'}
    },
    # Refresh Details
    '$ADDON[plugin.video.themoviedb.helper 32233]': {
        'command': 'RunScript(plugin.video.themoviedb.helper,refresh_details,{})',
        'setting': 'contextmenu_refresh_details',
        'episode': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}', 'episode': '{episode}'},
        'season': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}'},
        'other': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'}
    },
    # Modify Artwork
    '$ADDON[plugin.video.themoviedb.helper 32118]': {
        'command': 'RunScript(plugin.video.themoviedb.helper,modify_artwork,{})',
        'setting': 'contextmenu_modify_artwork',
        'movie': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'},
        'tvshow': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'},
        'episode': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}', 'episode': '{episode}'},
        'season': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}'},
    },
    # Add to Library
    '$LOCALIZE[20444]': {
        'command': 'RunScript(plugin.video.themoviedb.helper,add_to_library,{})',
        'setting': 'contextmenu_add_to_library',
        'movie': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'},
        'tvshow': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'},
        'season': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'},
        'episode': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'}
    }

}


class ContextMenuConfig:
    """The context menu items that are switched on, worked out once for a list of items.

    discovery_source provides action_discovery, which is only loaded when sync options
    are switched on and no shared answer about sync actions is stored.
    """

    def __init__(self, discovery_source, context=None):
        self.discovery_source = discovery_source
        self.context = context or CONTEXT_MENU_ITEMS

    @cached_property
    def has_sync_actions(self):
        from tmdbhelper.lib.script.actions.availability import SyncActionsAvailability
        return SyncActionsAvailability(self.discovery_source).is_available

    def is_enabled(self, mediatypes):
        if not get_setting(mediatypes['setting']):
            return False
        if mediatypes['setting'] == 'contextmenu_sync_options':
            return self.has_sync_actions
        return True

    @cached_property
    def play_random_enabled(self):
        return self.get_play_random_enabled()

    @staticmethod
    def get_play_random_enabled():
        return get_setting('contextmenu_play_random')

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        return {
            name: mediatypes
            for name, mediatypes in self.context.items()
            if self.is_enabled(mediatypes)
        }


class ContextMenu():
    """ Builds a context menu for a listitem based upon a definition of formattable keys
    If context params have format key in self.info but it is empty then item isn't built
    Context menu builds only for specified mediatypes (use other for all others)
    A shared ContextMenuConfig avoids reading the same settings for every item in a list.
    """

    def __init__(self, listitem, config=None):
        self._li = listitem
        self.config = config or ContextMenuConfig(listitem)
        self.info = {
            'ftv_id': self._li.ftv_id,
            'tmdb_id': self._li.tmdb_id,
            'tmdb_type': self._li.tmdb_type,
            'trakt_type': self._li.trakt_type,
            'season': self._li.season,
            'episode': self._li.episode,
        }
        self.mediatype = self._li.infolabels.get('mediatype')

    def get(self):
        items = [
            (name, str(item))
            for name, item in (
                (name, self._build_item(mediatypes))
                for name, mediatypes in self.config.items.items()
            )
            if item
        ]
        if self.config.play_random_enabled:
            from tmdbhelper.lib.items.context_random import PlayRandomContextMenu
            items += PlayRandomContextMenu(self._li).items
        from tmdbhelper.lib.items.context_nextepisodes import BrowseNextEpisodesContextMenu
        items += BrowseNextEpisodesContextMenu(self._li).items
        return items

    def _build_item(self, mediatypes):
        params_def = mediatypes.get(self.mediatype, mediatypes.get('other'))
        router_def = mediatypes.get('command')
        if not params_def or not router_def:
            return

        item = {}
        for k, v in params_def.items():
            try:  # Need to try accept in case hard-coded int/bool etc.
                value = v.format(**self.info)
            except AttributeError:
                value = v
            if value in ['None', '', None]:
                return  # Don't create a context item if we don't have a formatter value
            item[k] = value

        router_str = ','.join([f'{k}={v}' for k, v in item.items()])
        return router_def.format(router_str)
