from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized, get_setting, ADDONPATH
from tmdbhelper.lib.addon.consts import RUNSCRIPT
from contextlib import suppress


class StaticItemMapper(ItemMapper):
    @cached_property
    def label(self):
        return self.list_name

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

    def get_params(self):
        params = {
            'info': 'trakt_userlist',
            'tmdb_type': 'both',
            'list_name': self.list_name,
            'list_slug': self.list_slug,
            'user_slug': self.user_slug,
            'plugin_category': self.list_name,
        }
        return params

    def get_infolabels(self):
        infolabels = {
            'plot': self.list_description,
            'studio': [self.user_name],
        }
        return infolabels

    def get_infoproperties(self):
        infoproperties = {
            k: v for k, v in self.meta['list'].items()
            if v and type(v) not in [list, dict]
        }
        infoproperties.update({'is_sortable': 'True'})
        return infoproperties

    def get_unique_ids(self):
        unique_ids = {
            'slug': self.list_slug,
            'user': self.user_slug,
        }
        return unique_ids

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
        if not self.user_slug:  # Workaround to hide invalid entries for banned users still showing in results
            return {}
        if not self.list_slug:  # Workaround to hide invalid entries for banned lists still showing in results
            return {}
        return super().item


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


class StaticGenresItemMapper(ItemMapper):

    def __init__(self, *args, tmdb_type, **kwargs):
        super().__init__(*args, **kwargs)
        self.tmdb_type = tmdb_type

    @cached_property
    def label(self):
        return self.meta['name']

    @cached_property
    def slug(self):
        return self.meta['slug']

    @cached_property
    def icon_path(self):
        return get_setting('trakt_genre_icon_location', 'str')

    @cached_property
    def custom_icon(self):
        import xbmcvfs
        custom_icon = xbmcvfs.validatePath(xbmcvfs.translatePath(f'{self.icon_path}/{self.slug}.png'))
        custom_icon = custom_icon if custom_icon and xbmcvfs.exists(custom_icon) else None
        return custom_icon

    @cached_property
    def icon(self):
        icon = self.custom_icon if self.icon_path else None
        icon = icon or f'{ADDONPATH}/resources/icons/trakt/genres.png'
        return icon

    def get_art(self):
        return {'icon': self.icon}

    def get_unique_ids(self):
        return {'slug': self.slug}

    def get_params(self):
        return {
            'info': 'dir_trakt_genre',
            'genre': self.slug,
            'tmdb_type': self.tmdb_type,
        }
