# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.script.method.decorators import is_in_kwargs
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


def get_trakt_provider(install=False):
    if install:
        from tmdbhelper.lib.script.sync.provider_install import SyncProviderInstall
        return SyncProviderInstall('script.module.tmdbhelper.sync.trakt').install()
    from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
    return SyncProviderRegistry().find_provider('trakt')


def run_trakt_diagnostic(action, **kwargs):
    if get_trakt_provider() is None:
        return
    from json import dumps
    from urllib.parse import quote
    from tmdbhelper.lib.addon.plugin import executebuiltin
    payload = quote(dumps(kwargs), safe='')
    executebuiltin(
        f'RunScript(script.module.tmdbhelper.sync.trakt,action={action},payload={payload})')


def authenticate_trakt(**kwargs):
    provider = get_trakt_provider(install=True)
    if provider is None:
        return
    from tmdbhelper.lib.addon.plugin import executebuiltin
    executebuiltin('RunScript(script.module.tmdbhelper.sync.trakt,action=authenticate)')


def revoke_trakt(**kwargs):
    if get_trakt_provider() is None:
        return
    from tmdbhelper.lib.addon.plugin import executebuiltin
    executebuiltin('RunScript(script.module.tmdbhelper.sync.trakt,action=revoke)')


def get_stats(forced=False, **kwargs):
    from tmdbhelper.lib.script.stats import get_stats as get_provider_stats
    return get_provider_stats(forced=forced)
