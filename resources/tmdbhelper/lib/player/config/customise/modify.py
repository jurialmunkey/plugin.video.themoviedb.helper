from xbmcgui import Dialog, INPUT_NUMERIC
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.player.config.customise.fallback import PlayerCustomiseSelectFallback
from tmdbhelper.lib.player.config.customise.editsteps import PlayerEditSteps
from jurialmunkey.ftools import cached_property
from collections import namedtuple


class PlayerCustomiseModifyItem:
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
                lambda: PlayerEditSteps(self.dialog_item.metadata, self.dialog_item.filename).run(),
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
        self.set_metadata('fallback', PlayerCustomiseSelectFallback(self.dialog_item).fallback)

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
