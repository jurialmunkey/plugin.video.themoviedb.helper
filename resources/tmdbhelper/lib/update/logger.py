
from jurialmunkey.ftools import cached_property


class LibraryLogger:

    location = 'log_library'

    @cached_property
    def data(self):
        return {}

    def log_item(self, key, tmdb_id, season=None, episode=None, **kwargs):
        to_update = self.data.setdefault(key, {})
        to_update = self.data[key].setdefault(tmdb_id, {})

        if season is not None:
            to_update = self.data[key][tmdb_id].setdefault('seasons', {})
            to_update = self.data[key][tmdb_id]['seasons'].setdefault(season, {})

        if episode is not None:
            to_update = self.data[key][tmdb_id]['seasons'][season].setdefault('episodes', {})
            to_update = self.data[key][tmdb_id]['seasons'][season]['episodes'].setdefault(episode, {})

        for k, v in kwargs.items():
            to_update[k] = v

    def add(self, key, tmdb_id, log_msg, season=None, episode=None, **kwargs):
        if not log_msg:
            return
        self.log_item(key, tmdb_id, season=season, episode=episode, log_msg=log_msg, **kwargs)
        return log_msg

    def out(self):
        if not self.data:
            return
        from tmdbhelper.lib.files.futils import dumps_to_file
        from tmdbhelper.lib.addon.tmdate import get_todays_date
        dumps_to_file(self.data, self.location, f'{get_todays_date(str_fmt="%Y-%m-%d-%H%M%S")}.json')
