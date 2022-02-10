import re
import xbmcaddon
from resources.lib.items.artselect import _ArtworkSelector
from resources.lib.items.listitem import ListItem
from resources.lib.files.cache import BasicCache
from resources.lib.api.tmdb.api import TMDb
from resources.lib.api.fanarttv.api import FanartTV
from resources.lib.addon.timedate import set_timestamp, get_timestamp
from resources.lib.addon.constants import IMAGEPATH_QUALITY_POSTER, IMAGEPATH_QUALITY_FANART, IMAGEPATH_QUALITY_THUMBS, IMAGEPATH_QUALITY_CLOGOS, IMAGEPATH_ALL, ARTWORK_BLACKLIST
from resources.lib.addon.decorators import TimerList
# from resources.lib.addon.plugin import kodi_log

ADDON = xbmcaddon.Addon('plugin.video.themoviedb.helper')
ARTWORK_QUALITY = ADDON.getSettingInt('artwork_quality')
ARTWORK_QUALITY_FANART = IMAGEPATH_QUALITY_FANART[ARTWORK_QUALITY]
ARTWORK_QUALITY_THUMBS = IMAGEPATH_QUALITY_THUMBS[ARTWORK_QUALITY]
ARTWORK_QUALITY_CLOGOS = IMAGEPATH_QUALITY_CLOGOS[ARTWORK_QUALITY]
ARTWORK_QUALITY_POSTER = IMAGEPATH_QUALITY_POSTER[ARTWORK_QUALITY]
IMAGEPATH_MAP = {
    "fanart": ARTWORK_QUALITY_FANART,
    "tvshow.fanart": ARTWORK_QUALITY_FANART,
    "season.fanart": ARTWORK_QUALITY_FANART,
    "landscape": ARTWORK_QUALITY_THUMBS,
    "tvshow.landscape": ARTWORK_QUALITY_THUMBS,
    "season.landscape": ARTWORK_QUALITY_THUMBS,
    "clearlogo": ARTWORK_QUALITY_CLOGOS,
    "tvshow.clearlogo": ARTWORK_QUALITY_CLOGOS,
    "season.clearlogo": ARTWORK_QUALITY_CLOGOS,
    "thumb": ARTWORK_QUALITY_THUMBS,
    "tvshow.thumb": ARTWORK_QUALITY_THUMBS,
    "season.thumb": ARTWORK_QUALITY_THUMBS,
    "poster": ARTWORK_QUALITY_POSTER,
    "tvshow.poster": ARTWORK_QUALITY_POSTER,
    "season.poster": ARTWORK_QUALITY_POSTER
}
CACHE_DAYS = 10000


class ItemBuilder(_ArtworkSelector):
    def __init__(self, tmdb_api=None, ftv_api=None, trakt_api=None, cache_only=False):
        self.parent = {}
        self.tmdb_api = tmdb_api or TMDb()
        self.ftv_api = ftv_api or FanartTV()
        self.trakt_api = trakt_api
        self._cache = BasicCache(filename='ItemBuilder.db')
        self._regex = re.compile(r'({})'.format('|'.join(IMAGEPATH_ALL)))
        self.parent_params = None
        self.cache_only = cache_only
        self.timer_lists = {}
        self.log_timers = False
        # self.__dict__.update(kwargs)

    def _timestamp(self, days=14):
        return set_timestamp(days * 24 * 3600)

    def get_ftv_typeid(self, tmdb_type, item, season=None):
        if not item:
            return None, None
        unique_ids = item['listitem'].get('unique_ids', {})
        if tmdb_type == 'movie':
            return (unique_ids.get('tmdb'), 'movies')
        if tmdb_type == 'tv':
            if season is None:
                return (unique_ids.get('tvdb'), 'tv')
            return (unique_ids.get('tvshow.tvdb'), 'tv')
        return None, None

    def map_item(self, item, tmdb_type, base_item=None):
        return self.tmdb_api.mapper.get_info(item, tmdb_type, base_item=base_item)

    def map_artwork(self, artwork):
        """ Remaps artwork from TMDb to expected quality """
        return {k: self._regex.sub(IMAGEPATH_MAP[k], v) for k, v in artwork.items() if v and k in IMAGEPATH_MAP}

    def get_ftv_artwork(self, ftv_id, ftv_type, season=None):
        with TimerList(self.timer_lists, 'item_ftv', log_threshold=0.05, logging=self.log_timers):
            if not self.ftv_api or not ftv_id or not ftv_type:
                return
            artwork = self.ftv_api.get_all_artwork(ftv_id, ftv_type)
            if not artwork or season is None:
                return artwork

            # Move tvshow artwork properties to tvshow. prefix for seasons/episodes
            artwork = {u'tvshow.{}'.format(k): v for k, v in artwork.items() if v}
            artwork['fanart'] = artwork.get('tvshow.fanart')
            season_artwork = self.ftv_api.get_all_artwork(ftv_id, ftv_type, season)

            # Add season artwork properties to season. prefix for seasons/episodes
            artwork.update({u'season.{}'.format(k): v for k, v in season_artwork.items() if v})
            artwork.update(season_artwork)
        return artwork

    def _get_artwork(self, item):
        if not item or 'artwork' not in item:
            return {}
        return item['artwork'].get(ARTWORK_QUALITY) or self.map_artwork(item['artwork'].get('tmdb')) or {}

    def get_artwork(self, item, tmdb_type, season=None, base_item=None):
        if not item:
            return

        tmdb_art = item['artwork'].get(ARTWORK_QUALITY)
        if not tmdb_art:
            tmdb_art = self._get_artwork(base_item)
            tmdb_art.update(self.map_artwork(item['artwork']['tmdb']) or {})
            item['artwork'][ARTWORK_QUALITY] = tmdb_art

        ftv_art = item['artwork'].get('fanarttv')
        if not ftv_art:
            ftv_id, ftv_type = self.get_ftv_typeid(tmdb_type, base_item or item)
            ftv_art = self.get_ftv_artwork(ftv_id, ftv_type, season=season) or {}
            item['artwork']['fanarttv'] = ftv_art
        return item

    def get_tmdb_item(self, tmdb_type, tmdb_id, season=None, episode=None, base_item=None, manual_art=None):
        with TimerList(self.timer_lists, 'item_tmdb', log_threshold=0.05, logging=self.log_timers):
            details = self.tmdb_api.get_details_request(tmdb_type, tmdb_id, season, episode)
            if not details:
                return
            if season is not None:
                tmdb_type = 'season' if episode is None else 'episode'
            item = {
                'listitem': self.map_item(details, tmdb_type, base_item=base_item['listitem'] if base_item else None),
                'expires': self._timestamp(),
                'artwork': {}}
            item['artwork']['tmdb'] = item['artwork'][ARTWORK_QUALITY] = item['listitem'].pop('art')
            if manual_art:
                item['artwork']['manual'] = manual_art
            item['listitem']['art'] = {}
        return item

    def get_item(self, tmdb_type, tmdb_id, season=None, episode=None, refresh_cache=False):
        if not tmdb_type or not tmdb_id:
            return
        name = '{}.{}.{}.{}'.format(tmdb_type, tmdb_id, season, episode)
        item = None if refresh_cache else self._cache.get_cache(name)
        if self.cache_only:
            return item
        base_item = None
        if season is not None:
            base_name = '{}.{}.None.None'.format(tmdb_type, tmdb_id)
            base_item = self.parent or self._cache.get_cache(base_name)
        if item and get_timestamp(item['expires']):
            if not base_item or base_item['expires'] < item['expires']:
                return item
        manual_art = item['artwork'].get('manual', {}) if item else {}
        if season is not None:
            base_item = base_item or self.get_item(tmdb_type, tmdb_id)
            base_manual_art = base_item['artwork'].get('manual', {}) if base_item else {}
            base_manual_art = {'tvshow.{}'.format(k): v for k, v in base_manual_art.items() if v}
            base_manual_art.update(manual_art)
            manual_art = base_manual_art
        item = self.get_tmdb_item(
            tmdb_type, tmdb_id, season=season, episode=episode,
            base_item=base_item, manual_art=manual_art)
        item = self.get_artwork(item, tmdb_type, season, base_item)
        return self._cache.set_cache(item, name, cache_days=CACHE_DAYS)
        # TODO: Remember to include OMDb too!

    def get_item_artwork(self, artwork):
        art_dict = artwork.get('tmdb') or {}
        art_dict.update(artwork.get('fanarttv') or {})
        art_dict.update(artwork.get('manual') or {})
        return art_dict

    def get_listitem(self, i):
        li = ListItem(parent_params=self.parent_params, **i)
        mediatype = li.infolabels.get('mediatype')
        item = self.get_item(
            li.get_tmdb_type(),
            li.unique_ids.get('tvshow.tmdb') if mediatype in ['season', 'episode'] else li.unique_ids.get('tmdb'),
            li.infolabels.get('season', 0) if mediatype in ['season', 'episode'] else None,
            li.infolabels.get('episode') if mediatype == 'episode' else None)
        if not item or 'listitem' not in item:
            return li
        li.set_details(item['listitem'])
        li.set_artwork(item['artwork'].get(ARTWORK_QUALITY))
        li.set_artwork(item['artwork'].get('fanarttv'), blacklist=ARTWORK_BLACKLIST[ARTWORK_QUALITY])
        li.set_artwork(item['artwork'].get('manual'))
        return li
