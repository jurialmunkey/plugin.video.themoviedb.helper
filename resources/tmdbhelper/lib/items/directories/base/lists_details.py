from tmdbhelper.lib.addon.plugin import convert_type
from tmdbhelper.lib.items.container import ContainerDirectory
from jurialmunkey.ftools import cached_property


class ItemDetails:
    def __init__(self, directory, tmdb_type, tmdb_id, season=None, episode=None):
        self.directory = directory  # Directory container class instance
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode

    @property
    def lidc(self):
        return self.directory.lidc

    @cached_property
    def lidc_item(self):
        return self.lidc.get_item(self.tmdb_type, self.tmdb_id, self.season, self.episode)

    @cached_property
    def params(self):
        params = {
            'info': 'details',
            'tmdb_type': self.tmdb_type,
            'tmdb_id': self.tmdb_id
        }
        if self.season is None:
            return params
        params['season'] = self.season
        if self.episode is None:
            return params
        params['episode'] = self.episode
        return params

    @cached_property
    def item(self):
        if not self.lidc_item:
            return
        item = self.lidc_item
        item.setdefault('params', {}).update(self.params)
        return item

    @cached_property
    def itemlist(self):
        if not self.item:
            return []
        return [self.item]


class ListDetails(ContainerDirectory):
    is_detailed = True
    is_cacheonly = False

    def get_items(self, tmdb_type, tmdb_id, season=None, episode=None, **kwargs):
        self.kodi_db = self.get_kodi_database(tmdb_type)
        self.container_content = convert_type(tmdb_type, output='container', season=season, episode=episode)
        return ItemDetails(self, tmdb_type, tmdb_id, season, episode).itemlist
