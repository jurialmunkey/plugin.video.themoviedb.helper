from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory


class ListDiscover(ContainerDefaultCacheDirectory):
    def get_items(self, **kwargs):
        from tmdbhelper.lib.script.discover.trakt import trakt_discover
        from tmdbhelper.lib.addon.consts import NODE_BASEDIR
        from tmdbhelper.lib.items.routes import get_container

        try:
            data = trakt_discover()
            file = data['file']
        except (KeyError, TypeError):
            return

        params = dict(
            filename=file,
            info='dir_custom_node',
            basedir=NODE_BASEDIR
        )

        paramstring = '&'.join((f'{k}={v}' for k, v in params.items()))
        container = get_container('dir_custom_node')(self.handle, paramstring, **params)
        return container.get_directory(items_only=True, build_items=False)
