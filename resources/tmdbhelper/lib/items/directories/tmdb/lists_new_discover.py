from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory


class ListDiscoverDir(ContainerDefaultCacheDirectory):

    def get_winprop_params(self):
        from tmdbhelper.lib.script.discover.tmdb.main import WINPROP
        from jurialmunkey.parser import parse_paramstring
        from jurialmunkey.window import get_property

        try:
            paramstring = get_property(WINPROP)
            paramstring = paramstring.split('?')[1]
        except IndexError:
            return {}

        return parse_paramstring(paramstring)

    def get_static_item(self, label, params):
        from tmdbhelper.lib.addon.plugin import PLUGINPATH, ADDONPATH
        return {
            'label': label,
            'params': params,
            'path': PLUGINPATH,
            'art': {'icon': f'{ADDONPATH}/resources/icons/themoviedb/discover.png'}
        }

    @property
    def item_new(self):
        from tmdbhelper.lib.addon.plugin import get_localized
        params = self.get_winprop_params()
        params['info'] = 'tmdb_discover'
        return self.get_static_item(get_localized(21435), params)

    @property
    def item_browse(self):
        from tmdbhelper.lib.addon.plugin import get_localized
        params = self.get_winprop_params()
        return self.get_static_item(get_localized(1024), params) if params else {}

    def get_items(self, **kwargs):
        from tmdbhelper.lib.script.discover.tmdb.main import NODE_FILENAME
        from tmdbhelper.lib.addon.consts import NODE_BASEDIR
        from tmdbhelper.lib.items.routes import get_container

        params = dict(
            filename=NODE_FILENAME,
            info='dir_custom_node',
            basedir=NODE_BASEDIR
        )

        paramstring = '&'.join((f'{k}={v}' for k, v in params.items()))
        container = get_container('dir_custom_node')(self.handle, paramstring, **params)

        items = []
        items.extend((i for i in (self.item_new, self.item_browse) if i))
        items.extend(container.get_directory(items_only=True, build_items=False) or [])

        return items


class ListDiscover(ListDiscoverDir):

    def get_items(self, **kwargs):
        from tmdbhelper.lib.script.discover.tmdb.main import TMDbDiscover
        discover = TMDbDiscover()
        discover.load_values(**kwargs)
        discover.doModal()
        return super().get_items()
