import xbmc
import xbmcgui
import xbmcaddon
from resources.lib.items.listitem import ListItem
from resources.lib.api.fanarttv.api import ARTWORK_TYPES, NO_LANGUAGE
from resources.lib.api.tmdb.mapping import get_imagepath_poster, get_imagepath_fanart
from resources.lib.addon.decorators import busy_dialog
# from resources.lib.addon.plugin import kodi_log

ADDON = xbmcaddon.Addon('plugin.video.themoviedb.helper')


class _ArtworkSelector():
    def refresh_all_artwork(self, tmdb_type, tmdb_id, ok_dialog=True, container_refresh=True, season=None):
        old_cache_refresh = self.ftv_api.cache_refresh
        self.ftv_api.cache_refresh = True

        with busy_dialog():
            item = self.get_item(tmdb_type, tmdb_id, season, refresh_cache=True)
        if not item:
            return xbmcgui.Dialog().ok(
                xbmc.getLocalizedString(39123),
                ADDON.getLocalizedString(32217).format(tmdb_type, tmdb_id)) if ok_dialog else None
        if ok_dialog:
            artwork_types = {k.capitalize() for k, v in item['artwork'].get('tmdb', {}).items() if v}
            artwork_types |= {k.capitalize() for k, v in item['artwork'].get('fanarttv', {}).items() if v}
            xbmcgui.Dialog().ok(
                xbmc.getLocalizedString(39123),
                ADDON.getLocalizedString(32218).format(tmdb_type, tmdb_id, ', '.join(artwork_types)))

        # Cache refreshed artwork
        item['artwork'] = {
            'tmdb': item['artwork'].get('tmdb'),
            'fanarttv': item['artwork'].get('fanarttv')}
        name = '{}.{}.{}.{}'.format(tmdb_type, tmdb_id, season, None)
        self._cache.set_cache(item, cache_name=name, cache_days=10000)

        # Refresh container to display new artwork
        if container_refresh:
            xbmc.executebuiltin('Container.Refresh')
            xbmc.executebuiltin('UpdateLibrary(video,/fake/path/to/force/refresh/on/home)')
        self.ftv_api.cache_refresh = old_cache_refresh  # Set it back to previous setting

    def select_artwork(self, tmdb_type, tmdb_id, container_refresh=True, blacklist=[], season=None):
        with busy_dialog():
            item = self.get_item(tmdb_type, tmdb_id, season)
            if not item:
                return
            ftv_id, ftv_type = self.get_ftv_typeid(tmdb_type, item)
            if not ftv_id or not ftv_type:
                return
        #     ftv_art = self.ftv_api.get_artwork_request(ftv_id, ftv_type)
        # if not ftv_art:
        #     return xbmcgui.Dialog().notification(
        #         xbmc.getLocalizedString(39123),
        #         ADDON.getLocalizedString(32217).format(ftv_type, ftv_id))

        # Choose Type
        artwork_types = [i for i in ARTWORK_TYPES.get(ftv_type if season is None else 'season') if i not in blacklist]  # Remove types that we previously looked for
        choice = xbmcgui.Dialog().select(xbmc.getLocalizedString(13511), artwork_types)
        if choice == -1:
            return

        # Get artwork of user's choosing
        artwork_type = artwork_types[choice]
        get_lang = artwork_type not in NO_LANGUAGE
        ftv_items = self.ftv_api.get_artwork(ftv_id, ftv_type, artwork_type, get_list=True, get_lang=get_lang, season=season) or []
        tmdb_items = self.tmdb_api.get_request_sc(tmdb_type, tmdb_id, 'images') if artwork_type in ['poster', 'fanart', 'landscape'] else None
        tmdb_items = tmdb_items or {}

        # If there was not artwork of that type found then blacklist it before re-prompting
        if not ftv_items and not tmdb_items:
            xbmcgui.Dialog().notification(
                xbmc.getLocalizedString(39123),
                ADDON.getLocalizedString(32217).format(tmdb_type, tmdb_id))
            blacklist.append(artwork_types[choice])
            return self.select_artwork(tmdb_type, tmdb_id, container_refresh, blacklist, season=season)

        # Choose artwork from options
        items = [
            ListItem(
                label=i.get('url'),
                label2=ADDON.getLocalizedString(32219).format(i.get('lang', ''), i.get('likes', 0), i.get('id', '')),
                art={'thumb': i.get('url')}).get_listitem() for i in ftv_items if i.get('url')]
        if artwork_type == 'poster':
            items += [
                ListItem(
                    label=get_imagepath_poster(i.get('file_path')),
                    label2=ADDON.getLocalizedString(32219).format(i.get('iso_639_1', ''), i.get('vote_average', 0), None),
                    art={'thumb': get_imagepath_poster(i.get('file_path'))}).get_listitem()
                for i in tmdb_items.get('posters', []) if i.get('file_path')]
        elif artwork_type in ['fanart', 'landscape']:
            items += [
                ListItem(
                    label=get_imagepath_fanart(i.get('file_path')),
                    label2=ADDON.getLocalizedString(32219).format(i.get('iso_639_1', ''), i.get('vote_average', 0), None),
                    art={'thumb': get_imagepath_fanart(i.get('file_path'))}).get_listitem()
                for i in tmdb_items.get('backdrops', []) if i.get('file_path')]
        choice = xbmcgui.Dialog().select(xbmc.getLocalizedString(13511), items, useDetails=True)
        if choice == -1:  # If user hits back go back to main menu rather than exit completely
            return self.select_artwork(ftv_id, ftv_type, container_refresh, blacklist, season=season)

        success = items[choice].getLabel()
        if not success:
            return

        # Cache our artwork forever since it was selected manually
        manual = item['artwork'].setdefault('manual', {})
        manual[artwork_type] = success
        name = '{}.{}.{}.{}'.format(tmdb_type, tmdb_id, season, None)
        self._cache.set_cache(item, cache_name=name, cache_days=10000)

        if container_refresh:
            xbmc.executebuiltin('Container.Refresh')
            xbmc.executebuiltin('UpdateLibrary(video,/fake/path/to/force/refresh/on/home)')

    def manage_artwork(self, tmdb_id=None, tmdb_type=None, season=None):
        if not tmdb_id or not tmdb_type:
            return
        choice = xbmcgui.Dialog().contextmenu([
            ADDON.getLocalizedString(32220),
            ADDON.getLocalizedString(32221)])
        if choice == -1:
            return
        if choice == 0:
            return self.select_artwork(tmdb_id=tmdb_id, tmdb_type=tmdb_type, season=season)
        if choice == 1:
            return self.refresh_all_artwork(tmdb_id=tmdb_id, tmdb_type=tmdb_type, season=season)
