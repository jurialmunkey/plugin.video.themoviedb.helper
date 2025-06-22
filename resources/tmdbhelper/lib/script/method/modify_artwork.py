# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import xbmcgui
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.script.method.kodi_utils import container_refresh
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase


class ModifyArtwork:

    accepted_aspects = ('poster', 'fanart', 'landscape', 'clearlogo')

    def __init__(self, tmdb_id):
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
    def url(self):
        return xbmcgui.Dialog().input(f'{get_localized(32106).format(self.aspect)} ({get_localized(32105)})') or None

    @cached_property
    def aspect(self):
        x = xbmcgui.Dialog().select(get_localized(39123), self.accepted_aspects)
        if x == -1:
            return
        return self.accepted_aspects[x]

    @cached_property
    def database(self):
        return ItemDetailsDatabase()

    def run(self, aspect=None, url=None):
        if aspect is not None:
            self.aspect = aspect
        if url is not None:
            self.url = url
        if self.aspect not in self.accepted_aspects:
            return  # TODO: Error message ?
        if not self.url and not xbmcgui.Dialog().yesno(get_localized(32115).format(self.aspect), get_localized(32116)):
            return
        self.database.set_list_values(
            table='user_art',
            keys=('type', 'icon', 'parent_id'),
            values=(self.aspect, self.url, self.item_id),
            overwrite=True
        )
        container_refresh()


class ModifyArtworkMovie(ModifyArtwork):
    tmdb_type = 'movie'


class ModifyArtworkTvshow(ModifyArtwork):
    tmdb_type = 'tv'


class ModifyArtworkSeason(ModifyArtwork):
    tmdb_type = 'tv'

    @cached_property
    def item_id(self):
        return self.season_id


class ModifyArtworkEpisode(ModifyArtwork):
    tmdb_type = 'tv'

    @cached_property
    def item_id(self):
        return self.episode_id


class ModifyArtworkPerson(ModifyArtwork):
    tmdb_type = 'person'


def modify_artwork_factory(tmdb_type, season=None, episode=None):
    if tmdb_type == 'movie':
        return ModifyArtworkMovie
    if tmdb_type == 'person':
        return ModifyArtworkPerson
    if tmdb_type == 'tv' and season is not None and episode is not None:
        return ModifyArtworkEpisode
    if tmdb_type == 'tv' and season is not None:
        return ModifyArtworkSeason
    if tmdb_type == 'tv':
        return ModifyArtworkTvshow


def modify_artwork(tmdb_id, tmdb_type, season=None, episode=None, aspect=None, url=None, **kwargs):
    instance = modify_artwork_factory(tmdb_type, season, episode)(tmdb_id)
    instance.season = season
    instance.episode = episode
    instance.run(aspect, url)
