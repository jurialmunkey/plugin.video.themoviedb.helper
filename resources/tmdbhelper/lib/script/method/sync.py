from tmdbhelper.lib.script.method.decorators import is_in_kwargs, get_tmdb_id


@is_in_kwargs({'tmdb_type': ['movie', 'tv']})
@get_tmdb_id
def sync_item(tmdb_type=None, tmdb_id=None, season=None, episode=None, sync_type=None, **kwargs):
    """ Open item sync menu using the configured providers """
    from tmdbhelper.lib.script.sync.menu_default import sync_item
    sync_item(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode, sync_type=sync_type)


def invalidate_sync(invalidate_sync, notification=True, sync=True, **kwargs):
    from tmdbhelper.lib.sync.invalidator import SyncInvalidator
    sync_invalidator = SyncInvalidator(invalidate_sync)
    if sync_invalidator is None:
        return
    sync_invalidator.notification = notification
    sync_invalidator.run(sync=sync)
