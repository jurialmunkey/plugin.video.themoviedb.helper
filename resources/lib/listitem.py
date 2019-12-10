import xbmcgui
import xbmcaddon
import xbmcplugin
import resources.lib.utils as utils

try:
    from urllib.parse import urlencode  # Py3
except ImportError:
    from urllib import urlencode  # Py2


class ListItem(object):
    def __init__(self, label=None, label2=None, dbtype=None, library=None, tmdb_id=None, imdb_id=None, dbid=None,
                 cast=None, infolabels=None, infoproperties=None, poster=None, thumb=None, icon=None, fanart=None,
                 mixed_type=None, url=None, is_folder=True):
        self.addonpath = xbmcaddon.Addon('plugin.video.themoviedb.helper').getAddonInfo('path')
        self.label = label or 'N/A'
        self.label2 = label2 or ''
        self.library = library or ''  # <content target= video, music, pictures, none>
        self.tmdb_id = tmdb_id or ''  # ListItem.Property(tmdb_id)
        self.imdb_id = imdb_id or ''  # IMDb ID for item
        self.poster = poster
        self.thumb = thumb
        self.url = url or {}
        self.mixed_type = mixed_type or ''
        self.icon = icon or '{0}/resources/poster.png'.format(self.addonpath)
        self.fanart = fanart or '{0}/fanart.jpg'.format(self.addonpath)
        self.cast = cast or []  # Cast list
        self.is_folder = is_folder
        self.infolabels = infolabels or {}  # ListItem.Foobar
        self.infoproperties = infoproperties or {}  # ListItem.Property(Foobar)
        if dbid:
            self.infolabels['dbid'] = dbid

    def set_url(self, **kwargs):
        url = kwargs.pop('url', 'plugin://plugin.video.themoviedb.helper/?')
        return '{0}{1}'.format(url, urlencode(kwargs))

    def get_url(self, url, url_tmdb_id=None):
        self.url = self.url or url.copy()
        self.url['tmdb_id'] = self.tmdb_id = url_tmdb_id or self.tmdb_id
        if self.mixed_type:
            self.url['type'] = self.mixed_type
            self.infolabels['mediatype'] = utils.type_convert(self.mixed_type, 'dbtype')
        if self.label == 'Next Page':
            self.infolabels['mediatype'] = ''
        if self.infolabels.get('mediatype') in ['season', 'episode']:
            self.url['season'] = self.infolabels.get('season')
        if self.infolabels.get('mediatype') == 'episode':
            self.url['episode'] = self.infolabels.get('episode')
        self.is_folder = False if self.url.get('info') in ['play', 'textviewer', 'imageviewer'] else True

    def get_details(self, dbtype=None, tmdb=None, omdb=None):
        self.infolabels['mediatype'] = dbtype

        if not dbtype or not tmdb:
            return

        details = None
        if dbtype in ['movie', 'tvshow']:
            tmdbtype = 'tv' if dbtype == 'tvshow' else 'movie'
            details = tmdb.get_detailed_item(tmdbtype, self.tmdb_id, cache_only=True)
        if dbtype in ['season', 'episode']:
            episode = self.infolabels.get('episode') if dbtype == 'episode' else None
            details = tmdb.get_detailed_item('tv', self.tmdb_id, season=self.infolabels.get('season'), episode=episode, cache_only=True)
        # # TODO: Add details for actors

        if not details:
            return

        self.infolabels = utils.merge_two_dicts(details.get('infolabels', {}), utils.del_empty_keys(self.infolabels))
        self.infoproperties = utils.merge_two_dicts(details.get('infoproperties', {}), utils.del_empty_keys(self.infoproperties))

        if dbtype == 'movie' and omdb and self.imdb_id:
            self.infoproperties = utils.merge_two_dicts(self.infoproperties, omdb.get_ratings_awards(imdb_id=self.imdb_id, cache_only=True))
        # TODO: Merge artwork? Maybe?

    def create_listitem(self, handle=None, **kwargs):
        listitem = xbmcgui.ListItem(label=self.label, label2=self.label2)
        listitem.setLabel2(self.label2)
        listitem.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': self.tmdb_id})
        listitem.setInfo(self.library, self.infolabels)
        listitem.setProperties(self.infoproperties)
        listitem.setArt({'thumb': self.thumb, 'icon': self.icon, 'poster': self.poster, 'fanart': self.fanart})
        listitem.setCast(self.cast)
        xbmcplugin.addDirectoryItem(handle, self.set_url(**kwargs), listitem, self.is_folder)
