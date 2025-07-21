from jurialmunkey.ftools import cached_property


class NullItemMapper:
    @cached_property
    def item(self):
        return {}


class ItemMapper:
    def __init__(self, meta, add_infoproperties):
        self.add_infoproperties = add_infoproperties
        self.meta = meta

    label = ''

    @staticmethod
    def clean_dict(dictionary):
        clean_dict = {k: v for k, v in dictionary.items() if v not in (None, '')}
        return clean_dict

    @cached_property
    def infolabels(self):
        return self.clean_dict(self.get_infolabels())

    def get_infolabels(self):
        return {}

    @cached_property
    def infoproperties(self):
        return self.clean_dict(self.get_infoproperties())

    def get_infoproperties(self):
        return {}

    @cached_property
    def params(self):
        return self.clean_dict(self.get_params())

    def get_params(self):
        return {}

    @cached_property
    def unique_ids(self):
        return self.clean_dict(self.get_unique_ids())

    def get_unique_ids(self):
        return {}

    @cached_property
    def art(self):
        return self.clean_dict(self.get_art())

    def get_art(self):
        return {}

    @cached_property
    def context_menu(self):
        return self.get_context_menu()

    def get_context_menu(self):
        return []

    @cached_property
    def item(self):
        return {
            'label': self.label,
            'infolabels': self.infolabels,
            'infoproperties': self.infoproperties,
            'art': self.art,
            'params': self.params,
            'unique_ids': self.unique_ids,
            'context_menu': self.context_menu
        }
