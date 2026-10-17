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
    sync_invalidator.notification = notification
    sync_invalidator.run(sync=sync)


def get_stats(**kwargs):
    from tmdbhelper.lib.query.database.database import FindQueriesDatabase
    from jurialmunkey.window import get_property

    stats = FindQueriesDatabase().get_trakt_stats()
    if not stats:
        return

    combined_stats = {}

    def set_proptime(prop_name, v):
        days, minutes = divmod(int(v), 60 * 24)
        hour, minutes = divmod(int(minutes), 60)
        get_property(f'{prop_name}_d', set_property=f'{days}')
        get_property(f'{prop_name}_h', set_property=f'{hour}')
        get_property(f'{prop_name}_mm', set_property=f'{minutes}')

    def set_property(base_name, stat_name, stat_type, v):
        prop_name = f'{base_name}.{stat_type}.{stat_name}'
        get_property(prop_name, set_property=f'{v}')
        set_proptime(prop_name, v) if stat_name == 'minutes' else None

    def set_combined(stat_name, v):
        stat_name = f'{stat_name}_total'
        combined_stats.setdefault(stat_name, 0)
        combined_stats[stat_name] += v

    def set_allstats(d, base_name, update_combined=True):
        for k, v in d.items():
            stat_name, stat_type = k.split('_', 1)
            set_property(base_name, stat_name, stat_type, v)
            set_combined(stat_name, v) if update_combined else None

    set_allstats(stats, 'TraktStats')
    set_allstats(combined_stats, 'TraktStats', update_combined=False)
