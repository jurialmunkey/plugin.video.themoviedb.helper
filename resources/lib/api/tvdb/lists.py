from resources.lib.items.container import Container
from resources.lib.api.mapping import get_empty_item
from resources.lib.addon.plugin import ADDONPATH
from resources.lib.addon.consts import TVDB_DISCLAIMER


TVDB_ICON = f'{ADDONPATH}/resources/icons/tvdb/tvdb.png'


class ListLists(Container):
    def _get_items(self, endpoint, param_info, key=None, params=None):
        data = self.tvdb_api.get_request_lc(endpoint)
        if key and data:
            self.plugin_category = data.get('name')
            data = data.get(key)
        if not data:
            return

        def _get_item(i):
            item = get_empty_item()
            item['label'] = i.get('name')
            item['art']['icon'] = TVDB_ICON
            item['params'] = {'info': param_info, 'tvdb_id': i.get('id')}
            item['infolabels']['plot'] = TVDB_DISCLAIMER
            if params:
                item['params'].update(params)
            return item

        items = [_get_item(i) for i in data if i.get('id')]

        return items
