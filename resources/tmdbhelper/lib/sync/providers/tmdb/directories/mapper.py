from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.mapper_basic import ItemMapper


class TMDbDirectoryItemMapper(ItemMapper):
    type_art = False

    @cached_property
    def builder(self):
        return self.get_builder()

    def get_builder(self):
        return self.meta.item.item_builder(
            self.meta.item, self.meta.type, mixed_dir=True, type_art=self.type_art)

    @cached_property
    def label(self):
        return self.get_label()

    def get_label(self):
        return self.builder.label

    def get_params(self):
        return self.builder.params

    def get_art(self):
        return self.builder.art

    def get_infoproperties(self):
        return self.builder.infoproperties.copy()

    def get_context_menu(self):
        return self.builder.context_menu


class TMDbUserListMapper(ItemMapper):
    @cached_property
    def label(self):
        return self.get_label()

    def get_label(self):
        return self.meta['name']

    @cached_property
    def list_id(self):
        return self.get_list_id()

    def get_list_id(self):
        return str(self.meta['id'])

    def get_infolabels(self):
        return {'plot': self.meta.get('description')}

    def get_infoproperties(self):
        return {key: value for key, value in self.meta.items() if not isinstance(value, (list, dict))}

    def get_art(self):
        fanart = self.tmdb_imagepath.get_imagepath_fanart(self.meta.get('backdrop_path'))
        return {'icon': fanart, 'fanart': fanart}

    def get_params(self):
        return {
            'info': 'tmdb_list', 'tmdb_type': 'both', 'list_id': self.list_id,
            'user_id': self.user_id, 'list_name': self.label, 'plugin_category': self.label,
        }

    def get_unique_ids(self):
        return {'list': self.list_id, 'user': self.user_id}
