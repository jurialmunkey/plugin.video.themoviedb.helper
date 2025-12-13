import re
from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH
from jurialmunkey.ftools import cached_property
from xbmcgui import Dialog
from tmdbhelper.lib.script.discover.base import DiscoverMain
from tmdbhelper.lib.script.discover.tmdb.routes import get_all_route_class_instances


NODE_FILENAME = 'TMDb Discover.json'
WINPROP = 'UserDiscover.FolderPath'


class TMDbDiscoverMain(DiscoverMain):

    file = NODE_FILENAME
    winprop = WINPROP
    base_params = ('info=discover', 'with_id=True')

    def load_values(self, tmdb_type='movie', **kwargs):
        self.routes_dict['tmdb_type'].load_value(tmdb_type)  # Set TMDb Type first as other values depend on it
        super().load_values(**kwargs)

    @cached_property
    def label(self):
        return f'TMDb {get_localized(32174)}'

    @cached_property
    def icon(self):
        return f'{ADDONPATH}/resources/icons/themoviedb/discover.png'

    @cached_property
    def name(self):
        return Dialog().input(get_localized(32241), defaultt=self.defaultt)

    @property
    def tmdb_type(self):
        return self.routes_dict['tmdb_type'].value

    @cached_property
    def iso_country(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb().iso_country

    @staticmethod
    def get_routes_dict_keyname(instance):
        """
        Create dictionary keynames
        Remove TMDbDiscover prefix from class name
        Splits CamelCase class names on Capitals and convert to snake_case
        """
        name = instance.__class__.__name__
        name = name.replace('TMDbDiscover', '')
        name = re.sub(r"([A-Z])", r" \1", name).split()
        return '_'.join(name).lower()

    def get_routes_dict(self):
        return {self.get_routes_dict_keyname(i): i for i in get_all_route_class_instances(self)}


def TMDbDiscover():
    return TMDbDiscoverMain('DialogSelect.xml', ADDONPATH)
