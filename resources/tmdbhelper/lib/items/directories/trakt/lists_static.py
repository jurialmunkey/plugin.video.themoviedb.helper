from tmdbhelper.lib.items.directories.trakt.lists_standard import ListTraktStandard, ListTraktStandardProperties
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from jurialmunkey.parser import try_int
from contextlib import suppress


RUNSCRIPT = 'Runscript(plugin.video.themoviedb.helper,{})'


class StaticItemMapper:
    def __init__(self, meta, add_infoproperties):
        self.add_infoproperties = add_infoproperties
        self.meta = meta

    @cached_property
    def list_type(self):
        with suppress(KeyError):
            return self.meta['list']['type']

    @cached_property
    def list_slug(self):
        with suppress(KeyError):
            return self.meta['list']['ids']['slug']

    @cached_property
    def user_slug(self):
        if self.list_type == 'official':
            return 'official'
        with suppress(KeyError):
            return self.meta['list']['user']['ids']['slug']

    @cached_property
    def list_name(self):
        with suppress(KeyError):
            return self.meta['list'].get('name') or ''

    @cached_property
    def user_name(self):
        with suppress(KeyError):
            return self.meta['list']['user'].get('name') or self.user_slug or ''

    @cached_property
    def list_description(self):
        with suppress(KeyError):
            return self.meta['list'].get('description')

    @cached_property
    def params(self):
        params = {
            'info': 'trakt_userlist',
            'tmdb_type': 'both',
            'list_name': self.list_name,
            'list_slug': self.list_slug,
            'user_slug': self.user_slug,
            'plugin_category': self.list_name,
        }
        return params

    @cached_property
    def infolabels(self):
        infolabels = {
            'plot': self.list_description,
            'studio': self.user_name,
        }
        return infolabels

    @cached_property
    def infoproperties(self):
        infoproperties = {
            k: v for k, v in self.meta['list'].items()
            if v and type(v) not in [list, dict]
        }
        infoproperties.update({'is_sortable': 'True'})
        return infoproperties

    @cached_property
    def unique_ids(self):
        unique_ids = {
            'slug': self.list_slug,
            'user': self.user_slug,
        }
        return unique_ids

    art = {}

    @cached_property
    def context_menu(self):
        return self.get_context_menu()

    def get_context_menu(self):
        return [
            (
                get_localized(32309),
                RUNSCRIPT.format('sort_list,{}'.format(','.join(f'{k}={v}' for k, v in self.params.items())))
            ),
            (
                get_localized(20444),
                RUNSCRIPT.format('user_list={list_slug},user_slug={user_slug}'.format(**self.params))
            ),
        ]

    @cached_property
    def item(self):
        return {
            'label': self.list_name,
            'label2': self.user_name,
            'infolabels': self.infolabels,
            'infoproperties': self.infoproperties,
            'art': self.art,
            'params': self.params,
            'unique_ids': self.unique_ids,
            'context_menu': self.context_menu
        }


class StaticLikedItemMapper(StaticItemMapper):
    def get_context_menu(self):
        context_menu = super().get_context_menu()
        context_menu = context_menu + [
            (
                get_localized(32319),
                RUNSCRIPT.format('like_list={list_slug},user_slug={user_slug},delete'.format(**self.params))
            )
        ]
        return context_menu


class StaticUnLikedItemMapper(StaticItemMapper):
    def get_context_menu(self):
        context_menu = super().get_context_menu()
        context_menu = context_menu + [
            (
                get_localized(32315),
                RUNSCRIPT.format('like_list={list_slug},user_slug={user_slug}'.format(**self.params))
            )
        ]
        return context_menu


class StaticOwnedItemMapper(StaticItemMapper):
    def get_context_menu(self):
        context_menu = super().get_context_menu()
        context_menu = context_menu + [
            (
                get_localized(118),
                RUNSCRIPT.format('rename_list={list_slug}'.format(**self.params))
            ),
            (
                get_localized(117),
                RUNSCRIPT.format('delete_list={list_slug}'.format(**self.params))
            )
        ]
        return context_menu


class ListTraktStaticProperties(ListTraktStandardProperties):

    item_mapper_class = StaticItemMapper

    @property
    def url(self):
        return self.request_url

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item


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
        list_properties.item_mapper_class = StaticUnLikedItemMapper
        list_properties.request_url = 'lists/trending'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32208
        return list_properties


class ListTraktStaticPopular(ListTraktStatic):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticUnLikedItemMapper
        list_properties.request_url = 'lists/popular'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32209
        return list_properties


class ListTraktStaticLiked(ListTraktStaticNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticLikedItemMapper
        list_properties.trakt_authorization = True
        list_properties.request_url = 'users/likes/lists'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32210
        return list_properties


class ListTraktStaticOwned(ListTraktStaticOwnedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.item_mapper_class = StaticOwnedItemMapper
        list_properties.trakt_authorization = True
        list_properties.request_url = 'users/me/lists'
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32211
        return list_properties
