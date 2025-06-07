from tmdbhelper.lib.items.directories.trakt.lists_standard import ListTraktStandard, ListTraktStandardProperties
# from tmdbhelper.lib.files.ftools import cached_property
from jurialmunkey.parser import try_int


class ListTraktStaticProperties(ListTraktStandardProperties):
    @property
    def url(self):
        return self.request_url

    def get_mapped_item(self, item, add_infoproperties=None):

        try:
            list_slug = item['list']['ids']['slug']
            user_slug = item['list']['user']['ids']['slug'] if item['list']['type'] != 'official' else 'official'
        except KeyError:
            return

        list_name = item['list'].get('name') or ''
        user_name = item['list']['user'].get('name') or user_slug or ''

        infolabels = {
            'plot': item['list'].get('description'),
            'studio': user_name,
        }

        infoproperties = {
            k: v for k, v in item['list'].items()
            if v and type(v) not in [list, dict]
        }
        infoproperties.update({
            'is_sortable': 'True'
        })

        return {
            'label': list_name,
            'label2': user_name,
            'infolabels': infolabels,
            'infoproperties': infoproperties,
            'art': {},
            'params': {
                'info': 'trakt_userlist',
                'tmdb_type': 'both',
                'list_name': list_name,
                'list_slug': list_slug,
                'user_slug': user_slug,
                'plugin_category': list_name,
            },
            'unique_ids': {
                'slug': list_slug,
                'user': user_slug,
            },
            'context_menu': []
        }


class ListTraktStaticNoCacheProperties(ListTraktStaticProperties):
    def get_cached_items(self, *args, **kwargs):
        """ Divert cached to uncached """
        items = self.get_uncached_items(*args, **kwargs)
        return items


class ListTraktStaticOwnedNoCacheProperties(ListTraktStaticNoCacheProperties):
    def get_mapped_item(self, item, add_infoproperties=None):
        """ Owned lists are flatter so need to reconfigure to match config of other types """
        return super().get_mapped_item({'list': item}, add_infoproperties=add_infoproperties)


class ListTraktStatic(ListTraktStandard):
    default_cacheonly = True
    list_properties_class = ListTraktStaticProperties

    def get_items(self, *args, length=None, **kwargs):
        length = try_int(length) or 5
        return super().get_items(*args, length=length, **kwargs)

    def get_items_finalised(self):
        from xbmcplugin import SORT_METHOD_UNSORTED
        self.sort_methods = [{'sortMethod': SORT_METHOD_UNSORTED, 'label2Mask': '%U'}]  # By studio (ie username)
        return super().get_items_finalised()


class ListTraktStaticNoCache(ListTraktStatic):
    list_properties_class = ListTraktStaticNoCacheProperties


class ListTraktStaticOwnedNoCache(ListTraktStatic):
    list_properties_class = ListTraktStaticOwnedNoCacheProperties


class ListTraktStaticTrending(ListTraktStatic):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'lists/trending'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32208
        return list_properties


class ListTraktStaticPopular(ListTraktStatic):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'lists/popular'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32209
        return list_properties


class ListTraktStaticLiked(ListTraktStaticNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.trakt_authorization = True
        list_properties.request_url = 'users/likes/lists'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32210
        return list_properties


class ListTraktStaticOwned(ListTraktStaticOwnedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.trakt_authorization = True
        list_properties.request_url = 'users/me/lists'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32211
        return list_properties
