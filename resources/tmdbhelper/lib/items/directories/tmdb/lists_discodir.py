# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from jurialmunkey.window import get_property
from jurialmunkey.parser import parse_paramstring, boolean
from tmdbhelper.lib.files.futils import delete_file
from tmdbhelper.lib.addon.consts import NODE_BASEDIR
from tmdbhelper.lib.addon.plugin import PLUGINPATH, ADDONPATH, get_localized
from tmdbhelper.lib.items.routes import get_container
from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory
from tmdbhelper.lib.script.discover.tmdb.main import WINPROP, NODE_FILENAME, TMDbDiscover


class ListDiscoverDir(ContainerDefaultCacheDirectory):

    def get_winprop_params(self):

        try:
            paramstring = get_property(WINPROP)
            paramstring = paramstring.split('?')[1]
        except IndexError:
            return {}

        return parse_paramstring(paramstring)

    def get_static_item(self, label, params, icon='discover'):

        return {
            'label': label,
            'params': params,
            'path': PLUGINPATH,
            'art': {'icon': f'{ADDONPATH}/resources/icons/themoviedb/{icon}.png'}
        }

    @property
    def item_edit(self):
        params = self.get_winprop_params()
        params['info'] = 'user_discover'
        params['update_listing'] = 'true'
        return self.get_static_item(get_localized(32325), params, icon='config')

    @property
    def item_search(self):
        from jurialmunkey.window import get_property
        params = self.get_winprop_params()
        if not params:
            return {}
        params['plugin_category'] = get_property(f'{WINPROP}.name')
        return self.get_static_item(get_property(f'{WINPROP}.name'), params, icon='search')

    @property
    def item_delete(self):
        if not self.dir_nodes:
            return {}
        params = {}
        params['info'] = 'user_discover'
        params['update_listing'] = 'true'
        params['method'] = 'delete'
        return self.get_static_item(get_localized(32237), params, icon='trash')

    @property
    def item_save(self):
        if not self.get_winprop_params():
            return {}
        params = {}
        params['info'] = 'user_discover'
        params['update_listing'] = 'true'
        params['method'] = 'save'
        return self.get_static_item(get_localized(190), params, icon='saveas') if params else {}

    @property
    def item_clear(self):
        if not self.get_winprop_params():
            return {}
        params = {}
        params['info'] = 'user_discover'
        params['update_listing'] = 'true'
        params['method'] = 'clear'
        return self.get_static_item(get_localized(32330), params, icon='refresh')

    @cached_property
    def dir_nodes_params(self):
        return dict(
            filename=NODE_FILENAME,
            info='dir_custom_node',
            basedir=NODE_BASEDIR
        )

    @cached_property
    def dir_nodes_paramstring(self):
        from urllib.parse import urlencode
        return urlencode(self.dir_nodes_params)

    @cached_property
    def dir_nodes(self):
        container = get_container('dir_custom_node')(self.handle, self.dir_nodes_paramstring, **self.dir_nodes_params)
        return container.get_directory(items_only=True, build_items=False) or []

    @cached_property
    def custom_nodes(self):
        return (
            self.item_search,
            self.item_edit,
            # self.item_save,  # Maybe use this later for an option to disable autosave
            self.item_clear,
            self.item_delete,
        )

    def get_items(self, **kwargs):
        items = []
        items.extend((i for i in self.custom_nodes if i))
        items.extend(self.dir_nodes)
        return items


class ListUserDiscover(ListDiscoverDir):

    @property
    def update_listing(self):
        return boolean(self.params.get('update_listing'))

    def delete_node(self, **kwargs):
        delete_file(NODE_BASEDIR, NODE_FILENAME, join_addon_data=False)

    def clear_properties(self, **kwargs):
        get_property(f'{WINPROP}', clear_property=True)
        get_property(f'{WINPROP}.name', clear_property=True)
        get_property(f'{WINPROP}.paramstring', clear_property=True)

    def save_listing(self, **kwargs):
        from xbmcgui import Dialog
        from tmdbhelper.lib.script.method.nodes import TMDbNode
        path = get_property(WINPROP)
        if not path:
            return
        name = Dialog().input(get_localized(32241), defaultt=get_property(f'{WINPROP}.name'))
        if not name:
            return
        icon = f'{ADDONPATH}/resources/icons/themoviedb/discover.png'
        node = TMDbNode(name=name, path=path, icon=icon)
        node.notification = False
        node.overwrite = True
        node.file = NODE_FILENAME
        node.add()

    def edit_menu(self, **kwargs):
        discover = TMDbDiscover()
        discover.load_values(**kwargs)
        discover.doModal()

    def get_items(self, update_listing=None, method='edit', **kwargs):
        routes = {
            'delete': self.delete_node,
            'save': self.save_listing,
            'clear': self.clear_properties,
            'edit': self.edit_menu,
        }
        routes[method](**kwargs)
        return super().get_items()
