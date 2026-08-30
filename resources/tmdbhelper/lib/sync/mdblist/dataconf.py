from jurialmunkey.ftools import cached_property


class ConfigureEpisodeDataItem:
    def __init__(self, item):
        self.item = item

    @cached_property
    def show(self):
        show = self.item['episode']['show']
        show['type'] = 'show'
        return show

    @cached_property
    def tmdb(self):
        return self.show['ids'].get('tmdb')

    @cached_property
    def snum(self):
        return self.item['episode']['season']

    @cached_property
    def enum(self):
        return self.item['episode']['number']

    @cached_property
    def season(self):
        return {'number': self.snum}

    @cached_property
    def episode(self):
        return {'number': self.enum, 'plays': 0, 'last_watched_at': self.item['last_watched_at']}


class ConfigureEpisodeList:
    def __init__(self, episodes_list):
        self.episodes_list = episodes_list

    @cached_property
    def configure_list(self):
        return tuple((ConfigureEpisodeDataItem(item) for item in self.episodes_list))

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        meta = {}

        for i in self.configure_list:
            show = meta.setdefault(i.tmdb, i.show)
            seasons = show.setdefault('seasons', {})
            season = seasons.setdefault(i.snum, i.season)
            episodes = season.setdefault('episodes', {})
            episode = episodes.setdefault(i.enum, i.episode)
            episode['plays'] += 1

        for show in meta.values():
            for season in show["seasons"].values():
                season["episodes"] = list(season["episodes"].values())
            show["seasons"] = list(show["seasons"].values())

        return list(meta.values())
