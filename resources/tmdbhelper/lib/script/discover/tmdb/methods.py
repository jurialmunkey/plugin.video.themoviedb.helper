from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.script.discover.base import DiscoverItem


class TMDbDiscoverMethods:
    @staticmethod
    def get_configured_routes(routes, item_class=DiscoverItem, sorting=True):
        return tuple((
            item_class(label=i['name'], value=i['id'], image=i.get('icon'))
            for i in (sorted(routes, key=lambda x: x['name']) if sorting else routes)
        ))

    @staticmethod
    def get_configured_localized_routes(routes, item_class=DiscoverItem, sorting=True):
        return tuple((
            item_class(label=get_localized(i['name']), value=i['id'], image=i.get('icon'))
            for i in (sorted(routes, key=lambda x: x['name']) if sorting else routes)
        ))

    @staticmethod
    def get_load_value_split(value, separator):
        import re
        return re.split(separator, value, flags=re.IGNORECASE)

    @staticmethod
    def get_load_value_generator(value, separator, id_func, item_class=DiscoverItem):
        return (
            item_class(id_func(tmdb_id), tmdb_id)
            for tmdb_id in TMDbDiscoverMethods.get_load_value_split(value, separator)
        )

    @staticmethod
    def get_load_value_separator(value):
        return '%2C' if '%2C' in value or '%2c' in value else '%7C'

    @staticmethod
    def menu_with_subselection(instance):
        for route in instance.routes_to_subselect:
            if not instance.main.routes_dict[route].value:
                instance.main.routes_dict[route].menu()
            if not instance.main.routes_dict[route].value:
                return False
        for route in instance.routes_to_reset:
            instance.main.routes_dict[route].reset_routes()
        return True
