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
    def menu_with_subselection(instance):
        for route in instance.routes_to_subselect:
            if not instance.main.routes_dict[route].value:
                instance.main.routes_dict[route].menu()
            if not instance.main.routes_dict[route].value:
                return False
        for route in instance.routes_to_reset:
            instance.main.routes_dict[route].reset_routes()
        return True
