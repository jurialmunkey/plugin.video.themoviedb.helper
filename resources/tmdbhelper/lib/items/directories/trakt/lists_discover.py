from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory


class ListDiscoverDir(ContainerDefaultCacheDirectory):

    @property
    def item_new(self):
        from tmdbhelper.lib.addon.plugin import PLUGINPATH, ADDONPATH, get_localized
        return {
            'label': f'{get_localized(35261)}...',
            'params': {'info': 'trakt_discover'},
            'path': PLUGINPATH,
            'art': {'icon': f'{ADDONPATH}/resources/trakt.png'}
        }

    def get_items(self, **kwargs):
        from tmdbhelper.lib.script.discover.trakt import NODE_FILENAME
        from tmdbhelper.lib.addon.consts import NODE_BASEDIR
        from tmdbhelper.lib.items.routes import get_container
        from urllib.parse import urlencode

        params = dict(
            filename=NODE_FILENAME,
            info='dir_custom_node',
            basedir=NODE_BASEDIR
        )

        container = get_container('dir_custom_node')(self.handle, urlencode(params), **params)

        items = []
        items.append(self.item_new)
        items.extend(container.get_directory(items_only=True, build_items=False) or [])

        return items


class ListDiscover(ListDiscoverDir):

    def get_items(self, **kwargs):
        from tmdbhelper.lib.script.discover.trakt import TraktDiscover
        discover = TraktDiscover()
        discover.load_values(**kwargs)
        discover.doModal()
        return super().get_items(**kwargs)
