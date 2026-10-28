from xbmcgui import Dialog, DLG_YESNO_YES_BTN
from jurialmunkey.parser import try_int
from jurialmunkey.window import get_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.files.locker import mutexlock
from tmdbhelper.lib.script.sync.provider_install import SyncProviderInstall


class SyncProviderDirectorySetup(SyncProviderInstall):
    mutex_lockname = 'SyncProviderDirectorySetup'

    def __init__(self, addon_id, route):
        super().__init__(addon_id)
        self.route = route
        self.prompt_version = get_property(self.prompt_property)

    @property
    def prompt_property(self):
        return f'SyncProviderDirectorySetup.{self.addon_id}.Prompt'

    def ensure_provider(self):
        provider = self.get_provider()
        return provider if provider is not None else self.prompt()

    @mutexlock
    def prompt(self):
        provider = self.get_provider()
        if provider is not None:
            return provider
        if self.prompt_version != get_property(self.prompt_property):
            return
        get_property(self.prompt_property, str(try_int(self.prompt_version) + 1))
        if Dialog().yesno(
                get_localized(32550), get_localized(32580).format(self.route, self.display_name),
                yeslabel=get_localized(186), nolabel=get_localized(222),
                defaultbutton=DLG_YESNO_YES_BTN):
            return self.install()
