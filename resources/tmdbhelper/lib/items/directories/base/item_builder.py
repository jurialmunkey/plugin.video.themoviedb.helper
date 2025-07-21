from tmdbhelper.lib.addon.plugin import convert_type, get_localized
from jurialmunkey.ftools import cached_property


class BaseDirItemBuilder:
    def __init__(self, base_item, item_type, mixed_dir=False):
        self.base_item = base_item  # BaseDirItem
        self.mixed_dir = mixed_dir
        self.item_type = item_type

    @cached_property
    def context_menu(self):
        context_menu = [(
            get_localized(32309),
            'Runscript(plugin.video.themoviedb.helper,sort_list,{})'.format(
                ','.join(f'{k}={v}' for k, v in self.params.items()))
        )] if self.base_item.sorting else []
        return context_menu

    @cached_property
    def infoproperties(self):
        infoproperties = {}
        infoproperties.update(self.base_item.infoproperties)
        infoproperties.update({'is_sortable': 'True'}) if self.base_item.sorting else None
        return infoproperties

    @cached_property
    def params(self):
        params = {}
        params.update(self.base_item.params)
        params.update({'tmdb_type': self.item_type})
        params.update({'list_name': self.label}) if self.base_item.sorting else None
        return params

    @cached_property
    def art(self):
        art = {}
        art.update(self.base_item.art)
        return art

    @cached_property
    def label_space(self):
        return ' ' if self.mixed_dir else ''

    @cached_property
    def label_item_type(self):
        return convert_type(self.item_type, 'plural') if self.mixed_dir else ''

    @cached_property
    def label(self):
        return self.base_item.label.format(space=self.label_space, item_type=self.label_item_type)

    @cached_property
    def item(self):
        return {
            'label': self.label,
            'params': self.params,
            'infoproperties': self.infoproperties,
            'context_menu': self.context_menu,
            'art': self.art,
        }
