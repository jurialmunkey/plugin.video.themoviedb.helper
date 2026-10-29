import json
from jurialmunkey.ftools import cached_property
from jurialmunkey.window import get_property


class StatsProperties:
    names_property = 'Stats.PropertyNames'
    prefix = 'TraktStats'

    def __init__(self, stats):
        self.stats = stats

    @cached_property
    def properties(self):
        return self.get_properties()

    def get_properties(self):
        properties = {}
        totals = {}
        for key, value in self.stats.items():
            name, stat_type = key.split('_', 1)
            properties.update(self.get_stat_properties(name, stat_type, value))
            totals[name] = totals.get(name, 0) + value
        for name, value in totals.items():
            properties.update(self.get_stat_properties(name, 'total', value))
        return properties

    def get_stat_properties(self, name, stat_type, value):
        prop = f'{self.prefix}.{stat_type}.{name}'
        properties = {prop: str(value)}
        if name == 'minutes':
            days, minutes = divmod(int(value), 60 * 24)
            hours, minutes = divmod(minutes, 60)
            properties.update({
                f'{prop}_d': str(days),
                f'{prop}_h': str(hours),
                f'{prop}_mm': str(minutes),
            })
        return properties

    def clear(self):
        names = set(json.loads(get_property(self.names_property) or '[]'))
        names.update(self.properties)
        for name in names:
            get_property(name, clear_property=True)
        get_property(self.names_property, clear_property=True)

    def publish(self):
        self.clear()
        for name, value in self.properties.items():
            get_property(name, set_property=value)
        get_property(self.names_property, set_property=json.dumps(list(self.properties)))


def get_stats(forced=False, **kwargs):
    from tmdbhelper.lib.query.database.database import FindQueriesDatabase
    stats = FindQueriesDatabase().get_trakt_stats(forced=forced)
    if stats is not None:
        StatsProperties(stats).publish()
