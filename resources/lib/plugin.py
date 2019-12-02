import xbmc
import xbmcgui
import xbmcaddon
import resources.lib.utils as utils
from resources.lib.globals import LANGUAGES, APPEND_TO_RESPONSE, TMDB_LISTS
from resources.lib.kodilibrary import KodiLibrary
from resources.lib.tmdb import TMDb
from resources.lib.omdb import OMDb


class Plugin(object):
    def __init__(self):
        self.addonpath = xbmcaddon.Addon().getAddonInfo('path')
        self.prefixname = 'TMDbHelper.'
        self.kodimoviedb = None
        self.koditvshowdb = None
        self.details_tv = None

        addonname = 'plugin.video.themoviedb.helper'
        cache_long = xbmcaddon.Addon().getSettingInt('cache_details_days')
        cache_short = xbmcaddon.Addon().getSettingInt('cache_list_days')
        tmdb_apikey = xbmcaddon.Addon().getSetting('tmdb_apikey')
        omdb_apikey = xbmcaddon.Addon().getSetting('omdb_apikey')
        language = LANGUAGES[xbmcaddon.Addon().getSettingInt('language')]
        mpaa_prefix = xbmcaddon.Addon().getSetting('mpaa_prefix')

        self.tmdb = TMDb(
            api_key=tmdb_apikey, language=language, cache_long=cache_long, cache_short=cache_short,
            append_to_response=APPEND_TO_RESPONSE, addon_name=addonname, mpaa_prefix=mpaa_prefix)

        self.omdb = OMDb(
            api_key=omdb_apikey, cache_long=cache_long, cache_short=cache_short,
            addon_name=addonname) if omdb_apikey else None

    def textviewer(self, header, text):
        xbmcgui.Dialog().textviewer(header, text)

    def imageviewer(self, image):
        xbmc.executebuiltin('ShowPicture({0})'.format(image))

    def get_tmdb_id(self, query=None, itemtype=None, imdb_id=None, year=None, **kwargs):
        if kwargs.get('tmdb_id'):
            return kwargs.get('tmdb_id')
        query = utils.split_items(query)[0] if query else None
        itemtype = itemtype or TMDB_LISTS.get(kwargs.get('info'), {}).get('tmdb_check_id') or kwargs.get('type')
        return self.tmdb.get_tmdb_id(itemtype=itemtype, imdb_id=imdb_id, query=query, year=year, longcache=True)

    def get_omdb_ratings(self, item, cache_only=False):
        if self.omdb and item.get('infolabels', {}).get('imdbnumber'):
            ratings_awards = self.omdb.get_ratings_awards(imdb_id=item.get('infolabels', {}).get('imdbnumber'), cache_only=cache_only)
            if ratings_awards:
                item['infoproperties'] = utils.merge_two_dicts(item.get('infoproperties', {}), ratings_awards)
        return item

    def get_db_info(self, item, info=None, dbtype=None):
        kodidatabase = None
        if 'movie' in [item.get('url', {}).get('type'), dbtype]:
            self.kodimoviedb = self.kodimoviedb or KodiLibrary(dbtype='movie')
            kodidatabase = self.kodimoviedb
        if 'tv' in [item.get('url', {}).get('type'), dbtype]:
            self.koditvshowdb = self.koditvshowdb or KodiLibrary(dbtype='tvshow')
            kodidatabase = self.koditvshowdb
        if kodidatabase and info:
            item[info] = kodidatabase.get_info(
                info=info,
                dbid=item.get('dbid'),
                imdb_id=item.get('infolabels', {}).get('imdbnumber'),
                originaltitle=item.get('infolabels', {}).get('originaltitle'),
                title=item.get('infolabels', {}).get('title'),
                year=item.get('infolabels', {}).get('year'))
        return item
