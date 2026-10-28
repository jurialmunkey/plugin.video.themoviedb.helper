from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized, get_setting
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from tmdbhelper.lib.player.dialog.dictionary import PlayerDictionary


class PlayerEpisodeGroups:

    def __init__(self, item, player, virtual_season=None, virtual_episode=None):
        self.item = item
        self.player = player
        self.virtual_season = virtual_season
        self.virtual_episode = virtual_episode

    @cached_property
    def policy(self):
        return self.player.meta_get('episode_groups') or get_setting('player_episode_groups', 'str')

    @cached_property
    def groups(self):
        return self.get_groups()

    def get_groups(self):
        return BaseViewFactory('episode_groups', 'tv', self.item.tmdb_id).data or []

    @cached_property
    def numbering(self):
        return self.get_numbering()

    def get_numbering(self):
        return {
            'default': lambda: {},
            'select': self.select_numbering,
            'group': self.get_callback_numbering,
        }[self.policy]()

    def get_callback_numbering(self):
        if self.virtual_season is None or self.virtual_episode is None:
            return {}
        return {'virtual_season': self.virtual_season, 'virtual_episode': self.virtual_episode}

    def select_numbering(self):
        if not self.groups:
            return {}
        from xbmcgui import Dialog
        selection = Dialog().select(
            get_localized(32593),
            [get_localized(32594), *[group['title'] for group in self.groups]])
        if selection < 0:
            return
        if selection == 0:
            return {}
        return self.get_group_numbering(self.groups[selection - 1]['tmdb_id'])

    def get_group_numbering(self, group_id):
        data = BaseViewFactory(
            'episode_group_episode', 'tv', self.item.tmdb_id,
            season=self.item.season, episode=self.item.episode, group_id=group_id).data
        return {
            key: data[0][key] for key in ('virtual_season', 'virtual_episode')
        } if data else {}

    @cached_property
    def dictionary(self):
        return self.get_dictionary()

    def get_dictionary(self):
        if self.numbering is None:
            return
        if not self.numbering:
            return self.player.item
        item = PlayerDictionary(
            tmdb_type='tv', tmdb_id=self.item.tmdb_id,
            season=self.item.season, episode=self.item.episode,
            details=self.item.details, **self.numbering)
        return self.player.get_item_substitutes(item)
