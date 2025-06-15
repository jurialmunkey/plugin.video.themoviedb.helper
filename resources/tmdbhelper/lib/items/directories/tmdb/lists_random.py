import random
import string
from tmdbhelper.lib.items.directories.tmdb.lists_discover import ListDiscover


class ListRandomGenre(ListDiscover):
    def get_items(self, **kwargs):
        from tmdbhelper.lib.items.directories.tmdb.lists_allitems import ListGenres as ListAllGenres
        item = random.choice(ListAllGenres(self.handle, self.paramstring).get_items(**kwargs))
        kwargs.update(item['params'])
        items = super().get_items(**kwargs)
        self.plugin_category = item['params']['plugin_category']
        return items


class ListRandomProvider(ListDiscover):
    def get_items(self, **kwargs):
        from tmdbhelper.lib.items.directories.tmdb.lists_allitems import ListProviders as ListAllProviders
        item = random.choice(ListAllProviders(self.handle, self.paramstring).get_items(**kwargs))
        kwargs.update(item['params'])
        items = super().get_items(**kwargs)
        self.plugin_category = item['params']['plugin_category']
        return items


class ListRandomKeyword(ListDiscover):
    def get_items(self, **kwargs):
        from tmdbhelper.lib.items.directories.tmdb.lists_allitems import ListKeywords as ListAllKeywords
        item = random.choice(ListAllKeywords(self.handle, self.paramstring).get_items())
        kwargs.update(item['params'])
        items = super().get_items(**kwargs)
        self.plugin_category = string.capwords(item['params']['plugin_category'])
        return items


class ListRandomNetwork(ListDiscover):
    def get_items(self, **kwargs):
        from tmdbhelper.lib.items.directories.tmdb.lists_allitems import ListNetworks as ListAllNetworks
        item = random.choice(ListAllNetworks(self.handle, self.paramstring).get_items())
        kwargs.update(item['params'])
        items = super().get_items(**kwargs)
        self.plugin_category = string.capwords(item['params']['plugin_category'])
        return items


class ListRandomStudio(ListDiscover):
    def get_items(self, **kwargs):
        from tmdbhelper.lib.items.directories.tmdb.lists_allitems import ListStudios as ListAllStudios
        item = random.choice(ListAllStudios(self.handle, self.paramstring).get_items())
        kwargs.update(item['params'])
        items = super().get_items(**kwargs)
        self.plugin_category = string.capwords(item['params']['plugin_category'])
        return items
