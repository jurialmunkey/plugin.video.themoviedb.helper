# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.script.method.decorators import is_in_kwargs
from tmdbhelper.lib.script.method.sync import invalidate_sync
from tmdbhelper.lib.sync.providers.list_actions import get_provider_list_actions


@is_in_kwargs({'like_list': True})
def like_list(like_list=None, user_slug=None, delete=False, **kwargs):
    actions = get_provider_list_actions('trakt')
    if actions is not None:
        return actions.like_list(like_list, user_slug=user_slug or 'me', delete=delete)


@is_in_kwargs({'delete_list': True})
def delete_list(delete_list=None, **kwargs):
    actions = get_provider_list_actions('trakt')
    if actions is not None:
        return actions.delete_list(delete_list)


@is_in_kwargs({'rename_list': True})
def rename_list(rename_list=None, **kwargs):
    actions = get_provider_list_actions('trakt')
    if actions is not None:
        return actions.rename_list(rename_list)


def authenticate_trakt(**kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI(force=True)
    invalidate_sync('all', notification=False, sync=False)


def revoke_trakt(**kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    if not TraktAPI().logout():
        return
    invalidate_sync('all', notification=False, sync=False)


def get_stats(forced=False, **kwargs):
    from tmdbhelper.lib.script.stats import get_stats as get_provider_stats
    return get_provider_stats(forced=forced)
