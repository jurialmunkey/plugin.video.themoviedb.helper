from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDONPATH


class PlayerListItem:
    def __init__(self, player, posx):
        self.player = player
        self.posx = posx

    @cached_property
    def uid(self):
        if self.player.plugin_name in ('xbmc.core', 'plugin.video.themoviedb.helper'):
            return self.player.name
        return self.player.plugin_name

    @cached_property
    def label(self):
        return self.player.name

    @cached_property
    def label2(self):
        return self.player.plugin_name

    @cached_property
    def thumb(self):
        thumb = self.player.plugin_icon
        thumb = thumb or f'{ADDONPATH}/resources/icons/other/kodi.png'
        return thumb

    @cached_property
    def art(self):
        return {'thumb': self.thumb}

    @cached_property
    def item(self):
        return {
            'label': self.label,
            'label2': self.label2,
            'art': self.art,
        }

    @cached_property
    def listitem(self):
        from tmdbhelper.lib.items.listitem import ListItem
        return ListItem(**self.item).get_listitem()


class PlayerListItemCombined(PlayerListItem):
    @cached_property
    def label(self):
        if self.player.plugin_name in ('xbmc.core', 'plugin.video.themoviedb.helper'):
            return self.player.name
        from xbmcaddon import Addon as KodiAddon
        return KodiAddon(self.player.plugin_name).getAddonInfo('name')
