from tmdbhelper.lib.items.directories.trakt.mapper_standard import EpisodeItemMapper, MovieItemMapper
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_region_date
from jurialmunkey.ftools import cached_property


class CalendarItemMapper:
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


class CalendarEpisodeItemMapper(CalendarItemMapper, EpisodeItemMapper):
    tmdb_type = 'tv'
    mediatype = 'episode'


class CalendarMovieItemMapper(CalendarItemMapper, MovieItemMapper):
    tmdb_type = 'movie'
    mediatype = 'movie'

    @cached_property
    def air_date(self):
        try:
            return convert_timestamp(self.meta['released'], utc_convert=True, time_fmt="%Y-%m-%d", time_lim=10)
        except (KeyError, TypeError, AttributeError):
            return


def FactoryCalendarMovieItemMapper(meta, add_infoproperties=None):
    return CalendarMovieItemMapper(meta, add_infoproperties, sub_type='movie')


def FactoryCalendarEpisodeItemMapper(meta, add_infoproperties=None):
    return CalendarEpisodeItemMapper(meta, add_infoproperties, sub_type='episode')
