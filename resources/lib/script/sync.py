# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import xbmc
import xbmcgui
from resources.lib.helpers.decorators import busy_dialog
from resources.lib.helpers.parser import try_int
from resources.lib.trakt.api import TraktAPI
from resources.lib.helpers.plugin import ADDON


def _sync_item_methods():
    return [
        {
            'method': 'history',
            'sync_type': 'watched',
            'allow_episodes': True,
            'name_add': xbmc.getLocalizedString(16103),
            'name_remove': xbmc.getLocalizedString(16104)},
        {
            'method': 'collection',
            'sync_type': 'collection',
            'allow_episodes': True,
            'name_add': ADDON.getLocalizedString(32289),
            'name_remove': ADDON.getLocalizedString(32290)},
        {
            'method': 'watchlist',
            'sync_type': 'watchlist',
            'name_add': ADDON.getLocalizedString(32291),
            'name_remove': ADDON.getLocalizedString(32292)},
        {
            'method': 'recommendations',
            'sync_type': 'recommendations',
            'name_add': ADDON.getLocalizedString(32293),
            'name_remove': ADDON.getLocalizedString(32294)}]


class SyncItem():
    def __init__(self, trakt_type, unique_id, season=None, episode=None, id_type=None):
        self.trakt_type = trakt_type
        self.unique_id = unique_id
        self.season = try_int(season) if season is not None else None
        self.episode = try_int(episode) if episode is not None else None
        self.id_type = id_type
        self.trakt_api = TraktAPI()

    def _build_choices(self):
        choices = [{'name': ADDON.getLocalizedString(32298), 'method': 'userlist'}]
        choices += [j for j in (self._sync_item_check(**i) for i in _sync_item_methods()) if j]
        choices += [{'name': ADDON.getLocalizedString(32304), 'method': 'comments'}]
        return choices

    def _sync_item_check(self, sync_type=None, method=None, name_add=None, name_remove=None, allow_episodes=False):
        if self.season is not None and (not allow_episodes or not self.episode):
            return
        if self.trakt_api.is_sync(self.trakt_type, self.unique_id, self.season, self.episode, self.id_type, sync_type):
            return {'name': name_remove, 'method': '{}/remove'.format(method)}
        return {'name': name_add, 'method': method}

    def _sync_userlist(self):
        with busy_dialog():
            list_sync = self.trakt_api.get_list_of_lists('users/me/lists') or []
            list_sync.append({'label': ADDON.getLocalizedString(32299)})
        x = xbmcgui.Dialog().contextmenu([i.get('label') for i in list_sync])
        if x == -1:
            return
        if list_sync[x].get('label') == ADDON.getLocalizedString(32299):
            return  # TODO: CREATE NEW LIST
        list_slug = list_sync[x].get('params', {}).get('list_slug')
        if not list_slug:
            return
        with busy_dialog():
            return self.trakt_api.add_list_item(
                list_slug, self.trakt_type, self.unique_id, self.id_type,
                season=self.season, episode=self.episode)

    def _view_comments(self):
        trakt_type = 'show' if self.trakt_type in ['season', 'episode'] else self.trakt_type
        with busy_dialog():
            slug = self.trakt_api.get_id(self.unique_id, self.id_type, trakt_type, 'slug')
            comments = self.trakt_api.get_response_json('{}s'.format(trakt_type), slug, 'comments', limit=50) or []
            itemlist = [i.get('comment', '').replace('\n', ' ') for i in comments]
        return self._choose_comment(itemlist, comments)

    def _choose_comment(self, itemlist, comments):
        if not itemlist:
            xbmcgui.Dialog().ok(ADDON.getLocalizedString(32305), ADDON.getLocalizedString(32306))
            return -1
        x = xbmcgui.Dialog().select(ADDON.getLocalizedString(32305), itemlist)
        if x == -1:
            return -1
        info = comments[x].get('comment')
        name = comments[x].get('user', {}).get('name')
        rate = comments[x].get('user_stats', {}).get('rating')
        info = u'{}\n\n{} {}/10'.format(info, xbmc.getLocalizedString(563), rate) if rate else u'{}'.format(info)
        xbmcgui.Dialog().textviewer(name, info)
        return self._choose_comment(itemlist, comments)

    def _sync_item(self, method):
        if method == 'userlist':
            return self._sync_userlist()
        if method == 'comments':
            return self._view_comments()
        with busy_dialog():
            return self.trakt_api.sync_item(
                method, self.trakt_type, self.unique_id, self.id_type,
                season=self.season, episode=self.episode)

    def sync(self):
        with busy_dialog():
            choices = self._build_choices()
        x = xbmcgui.Dialog().contextmenu([i.get('name') for i in choices])
        if x == -1:
            return
        name = choices[x].get('name')
        method = choices[x].get('method')
        item_sync = self._sync_item(method)
        if item_sync == -1:
            return
        if item_sync and item_sync.status_code in [200, 201, 204]:
            xbmcgui.Dialog().ok(
                ADDON.getLocalizedString(32295),
                ADDON.getLocalizedString(32297).format(
                    name, self.trakt_type, self.id_type.upper(), self.unique_id))
            xbmc.executebuiltin('Container.Refresh')
            xbmc.executebuiltin('UpdateLibrary(video,/fake/path/to/force/refresh/on/home)')
            return
        xbmcgui.Dialog().ok(
            ADDON.getLocalizedString(32295),
            ADDON.getLocalizedString(32296).format(
                name, self.trakt_type, self.id_type.upper(), self.unique_id))
