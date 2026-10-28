from xbmcgui import Dialog, DLG_YESNO_YES_BTN
from jurialmunkey.parser import try_int
from jurialmunkey.window import get_property
from tmdbhelper.lib.addon.plugin import get_condvisibility, get_localized
from tmdbhelper.lib.files.locker import mutexlock
from tmdbhelper.lib.script.method.sync_provider import SyncProviderListSelection
from tmdbhelper.lib.script.sync.provider_default import SyncProviderDefaultSelection
from tmdbhelper.lib.script.sync.provider_install import SyncProviderInstall
from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting


class SyncProviderSetup:
    mutex_lockname = 'SyncProviderSetup'
    later_property = 'SyncProviderSetup.Later'
    prompt_property = 'SyncProviderSetup.Prompt'

    def __init__(self, capabilities, list_name):
        self.capabilities = capabilities
        self.list_name = list_name
        self.is_widget = self.get_is_widget()
        self.prompt_version = get_property(self.prompt_property)

    def get_is_widget(self):
        return not get_condvisibility('Window.IsActive(MyVideoNav.xml)')

    @property
    def eligible_capabilities(self):
        return tuple(feature for feature in self.capabilities if not SyncProviderSetting(feature).is_never)

    def has_provider(self):
        registry = SyncProviderRegistry()
        return any(registry.get_selected_provider(feature) is not None for feature in self.eligible_capabilities)

    @property
    def is_suppressed(self):
        if not self.eligible_capabilities:
            return True
        return self.is_widget and bool(get_property(self.later_property))

    def ensure_provider(self):
        if self.has_provider():
            return True
        if self.is_suppressed:
            return False
        return self.prompt()

    @mutexlock
    def prompt(self):
        # Re-read state after waiting: another invocation may have handled setup.
        if self.has_provider():
            return True
        if self.is_suppressed:
            return False
        if self.is_widget and self.prompt_version != get_property(self.prompt_property):
            return False
        get_property(self.prompt_property, str(try_int(get_property(self.prompt_property)) + 1))
        if not self.confirm():
            return False
        SyncProviderListSelection(self.eligible_capabilities).select()
        return self.has_provider()

    def disable_capabilities(self):
        for capability in self.eligible_capabilities:
            SyncProviderSetting(capability).disable()

    def confirm(self):
        if not self.is_widget:
            return Dialog().yesno(
                get_localized(32550), get_localized(32555).format(self.list_name),
                yeslabel=get_localized(186), nolabel=get_localized(222),
                defaultbutton=DLG_YESNO_YES_BTN)
        selected = Dialog().yesnocustom(
            get_localized(32550), get_localized(32555).format(self.list_name),
            yeslabel=get_localized(186), nolabel=get_localized(32556), customlabel=get_localized(13170),
            defaultbutton=DLG_YESNO_YES_BTN)
        if selected == 1:
            return True
        if selected == 2:
            self.disable_capabilities()
        else:  # Later, or closing the dialog, defers widget prompts for this session.
            get_property(self.later_property, 'True')
        return False


class SyncProviderOnboarding:
    mutex_lockname = SyncProviderSetup.mutex_lockname

    def __init__(self, addon_id):
        self.addon_id = addon_id

    @mutexlock
    def configure(self):
        provider = SyncProviderInstall(self.addon_id).install()
        if provider is not None:
            SyncProviderDefaultSelection(provider).select()
