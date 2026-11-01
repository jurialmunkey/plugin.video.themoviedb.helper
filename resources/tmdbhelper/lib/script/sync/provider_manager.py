from xbmcgui import Dialog, DLG_YESNO_NO_BTN
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.script.sync.provider_install import SyncProviderInstall
from tmdbhelper.lib.script.sync.provider_manager_features import SyncProviderManagerFeatures, SyncProviderManagerSetup
from tmdbhelper.lib.sync.providers.catalog import PROVIDERS
from tmdbhelper.lib.sync.providers.module import SyncProviderModuleDiscovery


class SyncProviderManager:
    def get_label(self, module):
        if module.addon is None:
            return get_localized(32558).format(module.display_name)
        status = get_localized(32584 if module.is_enabled else 32585)
        return get_localized(32741).format(module.display_name, status)

    def select(self):
        selected = 0
        while True:
            modules = SyncProviderModuleDiscovery().get_modules()
            selected = Dialog().select(
                get_localized(32740), [self.get_label(module) for module in modules],
                preselect=selected)
            if selected == -1:
                return
            self.toggle(modules[selected])

    def toggle(self, module):
        if module.is_enabled:
            return self.disable(module)
        return self.enable(module)

    def enable(self, module):
        if module.addon_id not in PROVIDERS and not Dialog().yesno(
                get_localized(32740), get_localized(32563).format(module.display_name),
                yeslabel=get_localized(186), nolabel=get_localized(222),
                defaultbutton=DLG_YESNO_NO_BTN):
            return
        provider = SyncProviderInstall(module.addon_id).install() if module.addon is None else module.enable()
        if provider is not None:
            SyncProviderManagerSetup(provider).select()

    def disable(self, module):
        features = SyncProviderManagerFeatures(module.provider)
        removed = '\n'.join(features.active_features)
        message = get_localized(32745).format(module.display_name)
        if removed:
            message += '\n\n' + get_localized(32746).format(removed)
        if not Dialog().yesno(
                get_localized(32740), message,
                yeslabel=get_localized(186), nolabel=get_localized(222),
                defaultbutton=DLG_YESNO_NO_BTN):
            return
        module.set_enabled(False)
        features.clear()
