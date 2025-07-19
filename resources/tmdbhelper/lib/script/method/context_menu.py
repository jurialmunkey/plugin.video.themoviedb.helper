# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.script.method.decorators import is_in_kwargs, get_tmdb_id
from jurialmunkey.ftools import cached_property


class _RelatedLists:
    def __init__(
        self,
        tmdb_id=None,
        tmdb_type=None,
        season=None,
        episode=None,
        **kwargs
    ):
        self.tmdb_id = tmdb_id
        self.tmdb_type = tmdb_type
        self.season = season
        self.episode = episode

    @cached_property
    def items(self):
        from tmdbhelper.lib.items.directories.base.lists_base import ListRelatedBaseDir
        return ListRelatedBaseDir(-1, '').get_items(
            tmdb_type=self.tmdb_type,
            tmdb_id=self.tmdb_id,
            season=self.season,
            episode=self.episode,
        )

    @cached_property
    def choices(self):
        if not self.items or len(self.items) <= 1:
            return []
        return [i.get('label') for i in self.items]

    @staticmethod
    def format_content(info):
        if info in ('posters', 'fanart', 'images'):
            return 'pictures'
        return 'videos'

    @staticmethod
    def format_folderpath(i):
        from tmdbhelper.lib.addon.plugin import format_folderpath, encode_url
        path = encode_url(path=i.get('path'), **i.get('params'))
        info = i['params']['info']
        return format_folderpath(path, content=_RelatedLists.format_content(info), info=info, play='RunPlugin')  # Use RunPlugin to avoid window manager info dialog crash with Browse method

    def select(self):
        from xbmcgui import Dialog
        from tmdbhelper.lib.addon.plugin import executebuiltin
        x = Dialog().contextmenu(self.choices)
        if x == -1:
            return
        executebuiltin('Dialog.Close(busydialog)')  # Kill modals because prevents ActivateWindow
        executebuiltin(_RelatedLists.format_folderpath(self.items[x]))


@is_in_kwargs({'tmdb_type': True})
@get_tmdb_id
def related_lists(**kwargs):
    _RelatedLists(**kwargs).select()
