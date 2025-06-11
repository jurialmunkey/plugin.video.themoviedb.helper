from tmdbhelper.lib.items.directories.trakt.mapper_standard import EpisodeItemMapper
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_region_date
from tmdbhelper.lib.files.ftools import cached_property


class CalendarEpisodeItemMapper(EpisodeItemMapper):
    tmdb_type = 'tv'
    mediatype = 'episode'

    @cached_property
    def air_date(self):
        try:
            return convert_timestamp(self.meta['first_aired'], utc_convert=True)
        except (KeyError, TypeError, AttributeError):
            return

    def get_infoproperties(self):
        infoproperties = super().get_infoproperties()
        infoproperties.update({
            'air_date': get_region_date(self.air_date, 'datelong'),
            'air_time': get_region_date(self.air_date, 'time'),
            'air_day': self.air_date.strftime('%A'),
            'air_day_short': self.air_date.strftime('%a'),
            'air_date_short': self.air_date.strftime('%d %b'),
        } if self.air_date else {})
        return infoproperties

    def get_infolabels(self):
        infolabels = super().get_infolabels()
        infolabels['premiered'] = self.air_date.strftime('%Y-%m-%d')
        return infolabels


def FactoryCalendarEpisodeItemMapper(meta, add_infoproperties=None):
    return CalendarEpisodeItemMapper(meta, add_infoproperties, sub_type='episode')
