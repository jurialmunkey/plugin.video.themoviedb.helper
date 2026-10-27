from tmdbhelper.lib.addon.plugin import ADDONPATH, convert_type, get_localized
from jurialmunkey.ftools import cached_property


class BaseDirItemBuilder:
    def __init__(self, base_item, item_type, mixed_dir=False, type_art=False):
        self.base_item = base_item  # BaseDirItem
        self.mixed_dir = mixed_dir
        self.item_type = item_type
        self.type_art = type_art

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
        return self.get_art()

    def get_art(self):
        art = self.base_item.art.copy()
        if not self.type_art:
            return art
        from tmdbhelper.lib.items.directories.base.artwork import get_directory_icon_variant
        icon = get_directory_icon_variant(self.base_item.art_icon, self.item_type)
        if icon:
            art['icon'] = f'{ADDONPATH}/{icon}'
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
