from xbmcgui import Dialog
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.sync.providers.ratings_settings import RatingsProviderSettings


class RatingsProviderSelection:
    setting_label = 32411
    dialog_label = 32581

    def __init__(self, settings=None):
        self.settings = settings if settings is not None else RatingsProviderSettings()
        self.providers = list(self.settings.providers)
        self.disabled = set(self.settings.disabled)

    @property
    def labels(self):
        return [provider.display_name for provider in self.providers]

    @property
    def preselect(self):
        return [
            index for index, provider in enumerate(self.providers)
            if provider.provider_id not in self.disabled
        ]

    def select(self):
        if not self.providers:
            Dialog().ok(get_localized(self.dialog_label), get_localized(32588))
            return
        return self.select_providers()

    def select_providers(self):
        selected = Dialog().multiselect(
            get_localized(self.dialog_label), self.labels, preselect=self.preselect)
        if selected is None:
            return
        provider_ids = {provider.provider_id for provider in self.providers}
        selected_ids = {self.providers[index].provider_id for index in selected}
        self.disabled = (self.disabled - provider_ids) | (provider_ids - selected_ids)
        self.settings.save(self.settings.order, self.disabled)


class RatingsProviderOrderSelection(RatingsProviderSelection):
    setting_label = 32591
    dialog_label = 32591

    @property
    def labels(self):
        return [
            get_localized(32583).format(
                index, provider.display_name,
                get_localized(32585 if provider.provider_id in self.disabled else 32584))
            for index, provider in enumerate(self.providers, 1)
        ]

    def select_providers(self):
        selected = 0
        while True:
            selected = Dialog().select(
                get_localized(self.dialog_label), self.labels + [get_localized(190), get_localized(222)],
                preselect=selected)
            if selected in (-1, len(self.providers) + 1):
                return
            if selected == len(self.providers):
                return self.save()
            selected = self.modify(selected)

    def get_actions(self, index):
        actions = []
        if index:
            actions.append((32586, self.move_up))
        if index < len(self.providers) - 1:
            actions.append((32587, self.move_down))
        return actions

    def modify(self, index):
        actions = self.get_actions(index)
        if not actions:
            return index
        selected = Dialog().select(
            self.providers[index].display_name, [get_localized(label) for label, _ in actions])
        if selected == -1:
            return index
        return actions[selected][1](index)

    def move_up(self, index):
        return self.move(index, index - 1)

    def move_down(self, index):
        return self.move(index, index + 1)

    def move(self, index, target):
        self.providers.insert(target, self.providers.pop(index))
        return target

    def save(self):
        self.settings.save([provider.provider_id for provider in self.providers], self.disabled)
