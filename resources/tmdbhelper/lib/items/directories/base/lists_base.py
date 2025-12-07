from tmdbhelper.lib.addon.plugin import ADDON, get_localized
from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.items.directories.base.basedir_nodes import BaseDirNode
from collections import namedtuple


BaseDirItem = namedtuple("BaseDirItem", "item type")


class BaseDirList:
    def __init__(
        self,
        main=False,
        trakt=False,
        tmdb=False,
        mdblist=False,
        tvdb=False,
        random=False,
        trakt_genre=False,
        tmdb_v4=False,
        calendar=False,
        details=False,
    ):
        self.main = main
        self.tmdb = tmdb
        self.trakt = trakt
        self.mdblist = mdblist
        self.tvdb = tvdb
        self.random = random
        self.trakt_genre = trakt_genre
        self.tmdb_v4 = tmdb_v4
        self.calendar = calendar
        self.details = details

    def build_basedir(self, item_type=None, group=None, info=None):
        basedir = self.get_basedir_grouped(item_type, info) if info and not group else None
        basedir = basedir or self.get_basedir_ungrouped(item_type, group)
        return basedir

    @staticmethod
    def set_grouped_item(i, info):
        item = i.item.get_item(i.type, mixed_dir=False)
        item['params'] = {'info': info, 'group': f'{i.item.group}'}
        item['label'] = get_localized(i.item.group)
        return item

    def get_basedir_grouped(self, item_type=None, info=None):
        groups = {
            i.item.group: i
            for i in self.get_basedir(item_type)
        }
        return [
            self.set_grouped_item(i, info)
            for i in groups.values()
        ]

    def get_basedir_ungrouped(self, item_type=None, group=None):
        return [
            i.item.get_item(i.type, mixed_dir=bool(not item_type))
            for i in self.get_basedir(item_type)
            if not group or int(group) == i.item.group  # Convert paramstring value to int for comparison
        ]

    def get_basedir(self, item_type=None):
        return [
            BaseDirItem(basedir_item, basedir_item_type)
            for basedir_item in self.basedir
            for basedir_item_type in basedir_item.types
            if not item_type or item_type == basedir_item_type
        ]

    @property
    def basedir(self):
        basedir = []
        basedir += self.basedir_main
        basedir += self.basedir_random
        basedir += self.basedir_tmdb
        basedir += self.basedir_trakt
        basedir += self.basedir_mdblist
        basedir += self.basedir_tvdb
        basedir += self.basedir_trakt_genre
        basedir += self.basedir_tmdb_v4
        basedir += self.basedir_calendar
        basedir += self.basedir_details
        return basedir

    @property
    def basedir_main(self):
        from tmdbhelper.lib.items.directories.base.basedir_main import get_all_main_class_instances
        return [] if not self.main else get_all_main_class_instances()

    @property
    def basedir_random(self):
        from tmdbhelper.lib.items.directories.base.basedir_random import get_all_random_class_instances
        return [] if not self.random else get_all_random_class_instances()

    @property
    def basedir_tmdb(self):
        from tmdbhelper.lib.items.directories.base.basedir_tmdb import get_all_tmdb_class_instances
        return [] if not self.tmdb else get_all_tmdb_class_instances()

    @property
    def basedir_trakt(self):
        from tmdbhelper.lib.items.directories.base.basedir_trakt import get_all_trakt_class_instances
        return [] if not self.trakt else get_all_trakt_class_instances()

    @property
    def basedir_mdblist(self):
        from tmdbhelper.lib.items.directories.base.basedir_mdblist import get_all_mdblist_class_instances
        return [] if not self.mdblist else get_all_mdblist_class_instances()

    @property
    def basedir_tvdb(self):
        from tmdbhelper.lib.items.directories.base.basedir_tvdb import get_all_tvdb_class_instances
        return [] if not self.tvdb else get_all_tvdb_class_instances()

    @property
    def basedir_trakt_genre(self):
        from tmdbhelper.lib.items.directories.base.basedir_trakt_genre import get_all_trakt_genre_class_instances
        return [] if not self.trakt_genre else get_all_trakt_genre_class_instances(self.trakt_genre)

    @property
    def basedir_tmdb_v4(self):
        from tmdbhelper.lib.items.directories.base.basedir_tmdb_v4 import get_all_tmdb_v4_class_instances
        return [] if not self.tmdb_v4 else get_all_tmdb_v4_class_instances()

    @property
    def basedir_calendar(self):
        from tmdbhelper.lib.items.directories.base.basedir_calendar import get_all_calendar_class_instances
        return [] if not self.calendar else get_all_calendar_class_instances(**self.calendar)

    @property
    def basedir_details(self):
        from tmdbhelper.lib.items.directories.base.basedir_details import get_all_details_class_instances
        return [] if not self.details else get_all_details_class_instances(**self.details)


class ListBaseDir(ContainerDirectory):

    @staticmethod
    def get_trakt_calendar_item(endpoint=None, user=None, info='trakt_calendar', **kwargs):
        return {k: v for k, v in (
            ('info', info),
            ('endpoint', endpoint),
            ('user', user),
        ) if v}

    @staticmethod
    def get_library_calendar_item():
        return {'info': 'library_nextaired'}

    def get_items(self, info=None, group=None, **kwargs):
        route = {
            'dir_movie': lambda: BaseDirList(tmdb=True, trakt=True).build_basedir('movie', group=group),
            'dir_tv': lambda: BaseDirList(tmdb=True, trakt=True).build_basedir('tv', group=group),
            'dir_person': lambda: BaseDirList(tmdb=True, trakt=True).build_basedir('person', group=group),
            'dir_tmdb': lambda: BaseDirList(tmdb=True).build_basedir(group=group, info='dir_tmdb'),
            'dir_trakt': lambda: BaseDirList(trakt=True).build_basedir(group=group, info='dir_trakt'),
            'dir_mdblist': lambda: BaseDirList(mdblist=True).build_basedir(group=group),
            'dir_tvdb': lambda: BaseDirList(tvdb=True).build_basedir(group=group),
            'dir_random': lambda: BaseDirList(random=True).build_basedir(),
            'dir_calendar_dvd': lambda: BaseDirList(calendar=ListBaseDir.get_trakt_calendar_item(info='trakt_dvdcalendar', **kwargs)).build_basedir('movie'),
            'dir_calendar_movie': lambda: BaseDirList(calendar=ListBaseDir.get_trakt_calendar_item(info='trakt_moviecalendar', **kwargs)).build_basedir('movie'),
            'dir_calendar_trakt': lambda: BaseDirList(calendar=ListBaseDir.get_trakt_calendar_item(**kwargs)).build_basedir('tv'),
            'dir_calendar_library': lambda: BaseDirList(calendar=ListBaseDir.get_library_calendar_item()).build_basedir('tv'),
            'dir_custom_node': lambda: BaseDirNode(**kwargs).build_basedir(),
            'dir_trakt_genre': lambda: BaseDirList(trakt_genre=kwargs.get('genre')).build_basedir(kwargs.get('tmdb_type')),
            'dir_tmdb_v4': lambda: BaseDirList(tmdb_v4=True).build_basedir(),
            'dir_settings': lambda: ADDON.openSettings(),
        }
        func = route.get(info, lambda: BaseDirList(main=True).build_basedir())
        return func()


class ListRelatedBaseDir(ContainerDirectory):
    def get_items(self, tmdb_type, tmdb_id, season=None, episode=None, include_play=False, **kwargs):
        return BaseDirList(
            details={
                'tmdb_type': tmdb_type, 'tmdb_id': tmdb_id, 'season': season, 'episode': episode,
                'detailed_item': {}, 'include_play': include_play,
            }
        ).build_basedir(tmdb_type)
