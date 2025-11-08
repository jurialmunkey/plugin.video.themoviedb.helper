from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.update import get_userlist
from tmdbhelper.lib.addon.plugin import executebuiltin


class LibraryCommonFunctions():
    busy_spinner = False
    clean_library = False
    auto_update = False
    debug_logging = True

    def __init__(self, busy_spinner=True):
        self.busy_spinner = busy_spinner

    @cached_property
    def _log(self):
        from tmdbhelper.lib.update.logger import LibraryLogger
        _log = LibraryLogger()
        _log.log_folder = self.log_folder
        return _log

    @cached_property
    def kodi_db_movies(self):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        return get_kodi_library('movie', cache_refresh=True)

    @cached_property
    def kodi_db_tv(self):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        return get_kodi_library('tv', cache_refresh=True)

    def get_movie_info(self, *args, **kwargs):
        return self.kodi_db_movies.get_info(*args, **kwargs)

    def get_tv_info(self, *args, **kwargs):
        return self.kodi_db_tv.get_info(*args, **kwargs)

    @cached_property
    def p_dialog(self):
        if not self.busy_spinner:
            return
        from xbmcgui import DialogProgressBG
        p_dialog = DialogProgressBG()
        p_dialog.create(self._msg_title, self._msg_start)
        return p_dialog

    def __enter__(self):
        pass

    def __exit__(self):
        for func in (
            func for func, cond in (
                (lambda: self.p_dialog.close(), self.p_dialog),
                (lambda: self._log._clean(), self.debug_logging),
                (lambda: self._log._out(), self.debug_logging),
                (lambda: executebuiltin('UpdateLibrary(video)'), self.auto_update),
                (lambda: executebuiltin('ClearLibrary(video)'), self.clean_library),
            ) if cond
        ):
            func()

    def _update(self, count, total, **kwargs):
        if not self.p_dialog:
            return
        self.p_dialog.update((((count + 1) * 100) // total), **kwargs)

    def add_userlist(self, user_slug=None, list_slug=None, confirm=True, force=False, **kwargs):
        request = get_userlist(user_slug=user_slug, list_slug=list_slug, confirm=confirm, busy_spinner=self.busy_spinner)

        if not request:
            return
        i_total = len(request)

        for x, i in enumerate(request):
            self._update(x, i_total, message=f'Updating {i.get(i.get("type"), {}).get("title")}...')
            self._add_userlist_item(i, force=force, user_slug=user_slug, list_slug=list_slug)

    def _add_userlist_item(self, i, force=False, user_slug=None, list_slug=None):
        i_type = i.get('type')
        if i_type == 'movie':
            func = self.add_movie
        elif i_type == 'show':
            func = self.add_tvshow
        else:
            return

        item = i.get(i_type, {})
        tmdb_id = item.get('ids', {}).get('tmdb')
        imdb_id = item.get('ids', {}).get('imdb')

        if not tmdb_id:
            self._log._add(
                'tv' if i_type == 'show' else 'movie', item.get('ids', {}).get('slug'),
                'skipped item in Trakt user list with missing TMDb ID')
            return

        return func(tmdb_id, force=force, imdb_id=imdb_id, user_slug=user_slug, list_slug=list_slug)
