# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.script.method.decorators import is_in_kwargs, get_tmdb_id


@is_in_kwargs({'tmdb_type': ['movie', 'tv']})
@get_tmdb_id
def add_to_library(tmdb_type=None, tmdb_id=None, force=False, **kwargs):
    if tmdb_type == 'movie':
        return add_movie_to_library(tmdb_id, force=force)
    if tmdb_type == 'tv':
        return add_tvshow_to_library(tmdb_id, force=force)


def add_movie_to_library(tmdb_id, force=False):
    from tmdbhelper.lib.update.builder.movies import LibraryBuilderMovies
    with LibraryBuilderMovies() as library:
        library.forced = force
        library.create(tmdb_id=tmdb_id)


def add_tvshow_to_library(tmdb_id, force=False):
    from tmdbhelper.lib.update.builder.tvshows import LibraryBuilderTvshows
    with LibraryBuilderTvshows() as library:
        library.forced = force
        library.create(tmdb_id=tmdb_id)


@is_in_kwargs({'user_list': True})
def add_user_list(user_list=None, user_slug=None, force=False, **kwargs):
    from tmdbhelper.lib.update.builder.userlist import LibraryBuilderUserList
    with LibraryBuilderUserList() as library:
        library.forced = force
        library.create(user_slug=user_slug or 'me', list_slug=user_list)


def run_autoupdate(force=False, busy_dialog=False, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.plugin import get_localized
    from jurialmunkey.parser import boolean
    if force == 'select':
        choice = Dialog().yesno(
            get_localized(32391),
            get_localized(32392),
            yeslabel=get_localized(32393),
            nolabel=get_localized(32394))
        if choice == -1:
            return
        force = boolean(choice)
    from tmdbhelper.lib.update.monitor import MonitorUserLists
    MonitorUserLists().library_autoupdate(forced=boolean(force))  # busy_spinner=boolean(busy_dialog)
