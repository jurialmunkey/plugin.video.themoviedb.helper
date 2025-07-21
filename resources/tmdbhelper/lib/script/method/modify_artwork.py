# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import xbmcgui
from tmdbhelper.lib.addon.plugin import get_localized
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.script.method.kodi_utils import container_refresh, service_refresh
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.script.method.decorators import is_in_kwargs, get_tmdb_id


class ModifyArtwork:

    accepted_aspects = ('poster', 'fanart', 'landscape', 'clearlogo', 'thumb')
    season = None
    episode = None

    def __init__(self, tmdb_id, **kwargs):
        self.tmdb_id = tmdb_id

    @cached_property
    def item_id(self):
        return self.parent_id

    @cached_property
    def parent_id(self):
        return f'{self.tmdb_type}.{self.tmdb_id}'

    @cached_property
    def season_id(self):
        return f'{self.tmdb_type}.{self.tmdb_id}.{self.season}'

    @cached_property
    def episode_id(self):
        return f'{self.tmdb_type}.{self.tmdb_id}.{self.season}.{self.episode}'

    @cached_property
    def database(self):
        return ItemDetailsDatabase()

    @cached_property
    def current_url(self):
        return self.get_current_url(self.aspect)

    def get_current_url(self, aspect):
        current_url = self.database.get_list_values(
            table='user_art',
            keys=('icon',),
            values=(aspect, self.item_id),
            conditions='type=? AND parent_id=? LIMIT 1'
        )
        try:
            return current_url[0]['icon']
        except (KeyError, TypeError, AttributeError, IndexError):
            return ''

    @cached_property
    def url_routes_browse(self):
        return [{'func': self.get_browse_url, 'name': get_localized(1024)}]

    @cached_property
    def url_routes_select(self):
        if not self.configured_listitems:
            return []
        return [{'func': self.get_select_url, 'name': get_localized(424)}]

    @cached_property
    def url_routes_manual(self):
        return [{'func': self.get_manual_url, 'name': get_localized(413)}]

    @cached_property
    def url_routes_delete(self):
        if not self.current_url:
            return []
        return [{'func': self.get_delete_url, 'name': get_localized(1210)}]

    @cached_property
    def url_routes(self):
        url_routes = []
        url_routes += self.url_routes_browse
        url_routes += self.url_routes_select
        url_routes += self.url_routes_manual
        url_routes += self.url_routes_delete
        return url_routes

    @cached_property
    def url(self):
        x = xbmcgui.Dialog().select(
            heading=f'{get_localized(39123)} URL',
            list=[i['name'] for i in self.url_routes]
        )
        if x == -1:
            return
        func = self.url_routes[x]['func']
        return func()

    factory_art_routes = {
        'fanart': 'fanart',
        'landscape': 'fanart',
        'poster': 'poster',
        'clearlogo': 'clearlogo',
        'thumb': 'thumb',
    }

    factory_ftv_routes = {
        'fanart': 'ftv_fanart',
        'landscape': 'ftv_landscape',
        'poster': 'ftv_poster',
        'clearlogo': 'ftv_clearlogo',
    }

    @cached_property
    def factory_art_data(self):
        return self.get_factory_data(self.factory_art_routes)

    @cached_property
    def factory_ftv_data(self):
        return self.get_factory_data(self.factory_ftv_routes)

    def get_factory_data(self, mapping):
        try:
            return BaseViewFactory(
                mapping[self.aspect],
                self.tmdb_type,
                self.tmdb_id,
                self.season,
                self.episode
            ).data or []
        except(AttributeError, KeyError, TypeError):
            return []

    @cached_property
    def sync_data(self):
        return self.factory_art_data + self.factory_ftv_data

    @cached_property
    def configured_listitems(self):
        return [
            ListItem(**i).get_listitem()
            for i in self.sync_data
        ]

    def get_delete_url(self):
        return ''  # Empty string prompts option to delete

    def get_select_url(self):
        if not self.configured_listitems:
            return
        x = xbmcgui.Dialog().select(
            heading=get_localized(13511),
            list=self.configured_listitems,
            useDetails=True,
        )
        if x == -1:
            return
        return self.sync_data[x]['art']['thumb']

    def get_browse_url(self):
        return xbmcgui.Dialog().browseSingle(
            type=2,
            heading=get_localized(13511),
            shares='files',
            useThumbs=True,
            mask='.jpg|.png|.gif|.bmp|.tif|.jpeg|.tga|.tiff|.webp',
            defaultt=self.current_url,
        ) or None

    def get_manual_url(self):
        return xbmcgui.Dialog().input(
            f'{get_localized(32106).format(self.aspect)} ({get_localized(32105)})',
            defaultt=self.current_url,
        )

    @cached_property
    def artwork_aspects_listitems(self):
        return [
            ListItem(
                label=i,
                art={'icon': self.get_current_url(i) or 'DefaultAddonImages.png'}
            ).get_listitem()
            for i in self.accepted_aspects
        ]

    @cached_property
    def aspect(self):
        x = xbmcgui.Dialog().select(get_localized(13511), self.artwork_aspects_listitems, useDetails=True)
        if x == -1:
            return -1
        return self.accepted_aspects[x]

    def del_item(self):
        self.database.del_list_values(
            table='user_art',
            values=(self.aspect, self.item_id),
            conditions='type=? AND parent_id=?',
        )

    def set_item(self):
        self.database.set_list_values(
            table='user_art',
            keys=('type', 'icon', 'parent_id'),
            values=(self.aspect, self.url or None, self.item_id),
            overwrite=True
        )

    def run(self, aspect=None, url=None):
        if aspect is not None:
            self.aspect = aspect
        if url is not None:
            self.url = url
        if self.aspect not in self.accepted_aspects:
            return -1
        if self.url == '' and (
            not self.current_url or not xbmcgui.Dialog().yesno(
                get_localized(32115).format(self.aspect),
                get_localized(32116)
            )
        ):
            return False
        if self.url is None:
            return False
        if self.url == '':
            self.del_item()
            return True
        self.set_item()
        return True


class ModifyArtworkMovie(ModifyArtwork):
    tmdb_type = 'movie'


class ModifyArtworkTvshow(ModifyArtwork):
    tmdb_type = 'tv'


class ModifyArtworkSeason(ModifyArtwork):
    tmdb_type = 'tv'

    def __init__(self, tmdb_id, season, **kwargs):
        self.tmdb_id = tmdb_id
        self.season = season

    @cached_property
    def item_id(self):
        return self.season_id


class ModifyArtworkEpisode(ModifyArtwork):
    tmdb_type = 'tv'

    def __init__(self, tmdb_id, season, episode, **kwargs):
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode

    @cached_property
    def item_id(self):
        return self.episode_id


class ModifyArtworkFactory:
    modified = False

    def __init__(self, tmdb_id, tmdb_type, season=None, episode=None, **kwargs):
        self.tmdb_id = tmdb_id
        self.tmdb_type = tmdb_type
        self.season = season
        self.episode = episode

    @cached_property
    def standard_modify_artwork_object(self):
        if self.tmdb_type == 'movie':
            return ModifyArtworkMovie
        if self.tmdb_type == 'tv' and self.season is not None and self.episode is not None:
            return ModifyArtworkEpisode
        if self.tmdb_type == 'tv' and self.season is not None:
            return ModifyArtworkSeason
        if self.tmdb_type == 'tv':
            return ModifyArtworkTvshow

    @cached_property
    def optional_modify_artwork_object(self):
        if self.tmdb_type == 'movie':
            return (
                (get_localized(20338), ModifyArtworkMovie),
            )
        if self.tmdb_type == 'tv' and self.season is not None and self.episode is not None:
            return (
                (get_localized(20359), ModifyArtworkEpisode),
                (get_localized(20373), ModifyArtworkSeason),
                (get_localized(20364), ModifyArtworkTvshow),
            )
        if self.tmdb_type == 'tv' and self.season is not None:
            return (
                (get_localized(20373), ModifyArtworkSeason),
                (get_localized(20364), ModifyArtworkTvshow),
            )
        if self.tmdb_type == 'tv':
            return (
                (get_localized(20364), ModifyArtworkTvshow),
            )

    @cached_property
    def selected_modify_artwork_object(self):
        if len(self.optional_modify_artwork_object) == 1:
            return self.optional_modify_artwork_object[0][1]
        x = xbmcgui.Dialog().select(
            get_localized(13511),
            [i[0] for i in self.optional_modify_artwork_object]
        )
        if x == -1:
            return
        return self.optional_modify_artwork_object[x][1]

    def run(self, aspect=None, url=None):
        func = (
            self.standard_modify_artwork_object
            if aspect or url else
            self.selected_modify_artwork_object
        )
        try:
            instance = func(self.tmdb_id, season=self.season, episode=self.episode)
        except (TypeError, KeyError, AttributeError):
            return
        x = instance.run(aspect, url)
        if x == -1 or aspect or url:
            return
        if x is True:
            self.modified = True
        return self.run()


@is_in_kwargs({'tmdb_type': True})
@get_tmdb_id
def modify_artwork(*args, aspect=None, url=None, **kwargs):
    modify_artwork = ModifyArtworkFactory(*args, **kwargs)
    modify_artwork.run(aspect, url)
    if not modify_artwork.modified:
        return
    container_refresh()
    service_refresh()
