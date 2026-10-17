# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.script.method.decorators import is_in_kwargs
from tmdbhelper.lib.script.method.sync import invalidate_sync
from tmdbhelper.lib.script.method.lists import select_sort_list


@is_in_kwargs({'like_list': True})
def like_list(like_list=None, user_slug=None, delete=False, **kwargs):
    from tmdbhelper.lib.sync.datasync import SyncDataFactory
    SyncDataFactory().like_userlist(
        user_slug=user_slug or 'me',
        list_slug=like_list,
        confirmation=True,
        delete=delete
    )
    if not delete:
        return
    from tmdbhelper.lib.script.method.kodi_utils import container_refresh
    container_refresh()


@is_in_kwargs({'delete_list': True})
def delete_list(delete_list=None, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.addon.plugin import get_localized
    if not Dialog().yesno(get_localized(32358), get_localized(32357).format(delete_list)):
        return
    TraktAPI().delete_response('users/me/lists', delete_list)
    from tmdbhelper.lib.script.method.kodi_utils import container_refresh
    container_refresh()


@is_in_kwargs({'rename_list': True})
def rename_list(rename_list=None, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.addon.plugin import get_localized
    name = Dialog().input(get_localized(32359))
    if not name:
        return
    TraktAPI().post_response('users/me/lists', rename_list, postdata={'name': name}, response_method='put')
    from tmdbhelper.lib.script.method.kodi_utils import container_refresh
    container_refresh()


def sort_list(**kwargs):
    from tmdbhelper.lib.items.directories.trakt.lists_sorting import get_sort_methods
    sort_methods = get_sort_methods(kwargs['info'])
    return select_sort_list(sort_methods, **kwargs)


def authenticate_trakt(**kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI(force=True)
    invalidate_sync('all', notification=False, sync=False)


def revoke_trakt(**kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI().logout()
    invalidate_sync('all', notification=False, sync=False)
