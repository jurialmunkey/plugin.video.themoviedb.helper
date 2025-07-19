from xbmcgui import Dialog, INPUT_NUMERIC
from tmdbhelper.lib.addon.plugin import ADDONPATH, get_localized
from jurialmunkey.parser import try_int, boolean
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.player.create import CreatePlayer
from tmdbhelper.lib.player.files import PlayerFiles
from tmdbhelper.lib.player.editsteps import _EditPlayer
from jurialmunkey.ftools import cached_property
from collections import namedtuple


class ConfigurePlayersSelectFallback:
    def __init__(self, dialog_item):
        self.dialog_item = dialog_item

    @cached_property
    def item_choice(self):
        x = Dialog().select(
            get_localized(32342).format(self.dialog_item.filename),
            [f'{name}: {data}' for name, data in self.dialog_item.fallback_methods]
        )
        return self.dialog_item.fallback_methods[x] if x != -1 else None

    @cached_property
    def new_player(self):
        if not self.item_choice:
            return
        return ConfigurePlayersDialogMenuFallbacks(self.item_choice[1]).choice

    @cached_property
    def new_filename(self):
        if not self.new_player:
            return
        return self.new_player.filename

    @cached_property
    def new_method(self):
        if not self.new_filename:
            return
        x = Dialog().select(get_localized(32341), self.new_player.methods)
        return self.new_player.methods[x] if x != -1 else None

    @cached_property
    def new_fallback(self):
        if self.new_filename == 'remove_fallback':
            return ''
        if not self.new_method:
            return
        return f'{self.new_filename} {self.new_method}'

    @cached_property
    def fallback(self):
        if self.new_fallback is None:
            return
        fallback = self.dialog_item.fallback
        if self.new_filename == 'remove_fallback':
            fallback.pop(self.item_choice[0], None)
        else:
            fallback[self.item_choice[0]] = self.new_fallback
        return fallback


class ConfigurePlayersModifyItem:
    def __init__(self, dialog_item):
        self.dialog_item = dialog_item

    @cached_property
    def namedtuple_option(self):
        return namedtuple("DialogOption", "label configure returns")

    @property
    def dialog_options(self):
        return (
            self.namedtuple_option(
                f'name: {self.dialog_item.name}',
                self.set_name,
                False,
            ),
            self.namedtuple_option(
                f'disabled: {self.dialog_item.is_disabled}',
                self.set_disabled,
                False,
            ),
            self.namedtuple_option(
                f'priority: {self.dialog_item.priority}',
                self.set_priority,
                False,
            ),
            self.namedtuple_option(
                f'is_resolvable: {self.dialog_item.is_resolvable}',
                self.set_resolvable,
                False,
            ),
            self.namedtuple_option(
                f'make_playlist: {self.dialog_item.make_playlist}',
                self.set_makeplaylist,
                False
            ),
            self.namedtuple_option(
                f'fallback: {self.dialog_item.has_fallback}',
                self.set_fallback,
                False
            ),
            self.namedtuple_option(
                get_localized(32440),
                lambda: _EditPlayer(self.dialog_item.metadata, self.dialog_item.filename).run(),
                False
            ),
            self.namedtuple_option(
                get_localized(32330),
                self.delete_player,
                True
            ),
            self.namedtuple_option(
                get_localized(190),
                self.save_file,
                True
            )
        )

    def set_metadata(self, name, data):
        if not data or data == self.dialog_item.get_metadata(name):
            return
        self.dialog_item.metadata[name] = data
        self.dialog_item.modified = True

    def set_name(self):
        self.set_metadata('name', Dialog().input(
            get_localized(32331).format(self.dialog_item.filename),
            defaultt=self.dialog_item.name))

    def set_disabled(self):
        self.set_metadata('disabled', 'false' if self.dialog_item.is_disabled else 'true')

    def set_priority(self):
        self.set_metadata('priority', try_int(Dialog().input(
            get_localized(32344).format(self.dialog_item.filename),
            defaultt=str(self.dialog_item.priority),  # Input numeric takes str for some reason
            type=INPUT_NUMERIC)))

    def set_resolvable(self):
        self.set_metadata('is_resolvable', 'false' if self.dialog_item.is_resolvable else 'true')

    def set_makeplaylist(self):
        x = Dialog().yesnocustom(get_localized(32424), get_localized(32425), customlabel=get_localized(32447))
        self.set_metadata('make_playlist', ('false', 'true', 'upnext')[x] if x != -1 else None)

    def set_fallback(self):
        self.set_metadata('fallback', ConfigurePlayersSelectFallback(self.dialog_item).fallback)

    def delete_player(self):
        from tmdbhelper.lib.addon.consts import PLAYERS_BASEDIR_SAVE
        from tmdbhelper.lib.files.futils import delete_file
        if not Dialog().yesno(
                get_localized(32334),
                get_localized(32335).format(self.dialog_item.filename),
                yeslabel=get_localized(13007), nolabel=get_localized(222)):
            return
        delete_file(PLAYERS_BASEDIR_SAVE, self.dialog_item.filename, join_addon_data=False)

    def save_file(self):
        from tmdbhelper.lib.addon.consts import PLAYERS_BASEDIR_SAVE
        from tmdbhelper.lib.files.futils import dumps_to_file
        if not self.dialog_item.modified or not Dialog().yesno(
                get_localized(32336), get_localized(32337).format(self.dialog_item.filename),
                yeslabel=get_localized(190), nolabel=get_localized(222)
        ):
            return
        dumps_to_file(
            self.dialog_item.metadata,
            PLAYERS_BASEDIR_SAVE,
            self.dialog_item.filename,
            indent=4,
            join_addon_data=False
        )  # Write out file

    @cached_property
    def choice(self):
        x = Dialog().select(self.dialog_item.filename, [i.label for i in self.dialog_options])
        return self.dialog_options[x] if x != -1 else None

    def select(self):
        if not self.choice:
            self.save_file()
            return
        self.choice.configure()
        if self.choice.returns:
            return
        return self.choice


class ConfigurePlayersDialogItem:

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
            self.filename = CreatePlayer().create_player()
            return

        while ConfigurePlayersModifyItem(self).select():
            pass


class ConfigurePlayersDialogMenu:

    @cached_property
    def players(self):
        return self.get_players()

    def get_players(self):
        players = {}
        players.update(self.players_other)
        players.update(self.players_files)
        return players

    players_other = {
        'create_player': {
            'name': get_localized(32140),
            'icon': '-',
            'priority': 1
        }
    }

    @cached_property
    def players_files(self):
        return PlayerFiles().dictionary

    @cached_property
    def players_prioritised(self):
        return sorted((
            ConfigurePlayersDialogItem(filename, metadata)
            for filename, metadata in self.players.items()
        ), key=lambda i: i.priority)

    @cached_property
    def dialog_options(self):
        return self.get_dialog_options()

    @busy_decorator
    def get_dialog_options(self):
        return [i.listitem for i in self.players_prioritised]

    @cached_property
    def choice(self):
        x = Dialog().select(get_localized(32328), self.dialog_options, useDetails=True)
        return self.players_prioritised[x] if x != -1 else None

    def select(self):
        if not self.choice:
            return
        self.choice.configure()
        return self.choice


class ConfigurePlayersDialogMenuFallbacks(ConfigurePlayersDialogMenu):

    def __init__(self, fallback=False):
        self.fallback = fallback

    @cached_property
    def players_other(self):
        return {
            'remove_fallback': {
                'name': f'{get_localized(32141)}: {self.fallback}',
                'icon': '-',
                'priority': 1
            }
        } if self.fallback else {}


def configure_players(*args, **kwargs):
    while ConfigurePlayersDialogMenu().select():
        pass
