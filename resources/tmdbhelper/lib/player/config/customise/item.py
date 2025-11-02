from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.player.config.customise.create import PlayerCreate
from tmdbhelper.lib.player.config.customise.modify import PlayerCustomiseModifyItem
from tmdbhelper.lib.addon.plugin import ADDONPATH
from jurialmunkey.parser import boolean


class PlayerCustomiseDialogItem:

    def __init__(self, filename, metadata):
        self.filename = filename
        self.metadata = metadata
        self.modified = False

    def get_metadata(self, name):
        try:
            return self.metadata[name]
        except KeyError:
            return

    @property
    def methods(self):
        methods = ('play_movie', 'play_episode', 'search_movie', 'search_episode')
        return [i for i in methods if self.get_metadata(i)]

    @property
    def fallback_methods(self):
        return [(i, self.get_fallback_method(i)) for i in self.methods]

    def get_fallback_method(self, name):
        fallback = self.get_metadata("fallback")
        return None if not fallback else fallback.get(name)

    @property
    def is_resolvable(self):
        return boolean(self.get_metadata('is_resolvable'))

    @property
    def is_disabled(self):
        return boolean(self.get_metadata('disabled'))

    @property
    def make_playlist(self):
        return boolean(self.get_metadata('make_playlist'))

    @property
    def has_fallback(self):
        return boolean(self.fallback)

    @property
    def fallback(self):
        return self.get_metadata('fallback') or {}

    @property
    def addon(self):
        from xbmcaddon import Addon as KodiAddon
        return KodiAddon(self.get_metadata('plugin') or '')

    @property
    def priority(self):
        return self.get_metadata('priority')

    @property
    def name(self):
        return self.get_metadata('name') or ''

    @property
    def label(self):
        return f'[DISABLED] {self.name}' if self.is_disabled else self.name

    @property
    def thumb(self):
        thumb = self.get_metadata('icon') or ''
        thumb = thumb.format(ADDONPATH)
        thumb = thumb or self.addon.getAddonInfo('icon')
        return thumb

    @property
    def item(self):
        return {
            'label': self.label,
            'label2': self.filename,
            'art': {'thumb': self.thumb},
        }

    @property
    def listitem(self):
        return ListItem(**self.item).get_listitem()

    def configure(self):

        if self.filename == 'create_player':
            self.filename = PlayerCreate().create_player()
            return

        while PlayerCustomiseModifyItem(self).select():
            pass
