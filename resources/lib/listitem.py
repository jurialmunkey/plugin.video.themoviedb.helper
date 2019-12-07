import xbmcgui
import xbmcaddon
import xbmcplugin
try:
    from urllib.parse import urlencode  # Py3
except ImportError:
    from urllib import urlencode  # Py2


class ListItem:
    def __init__(self, label=None, label2=None, dbtype=None, library=None, tmdb_id=None, imdb_id=None, dbid=None,
                 cast=None, infolabels=None, infoproperties=None, poster=None, thumb=None, icon=None, fanart=None,
                 is_folder=True):
        self.addonpath = xbmcaddon.Addon('plugin.video.themoviedb.helper').getAddonInfo('path')
        self.label = label or 'N/A'
        self.label2 = label2 or ''
        self.dbtype = dbtype or ''  # ListItem.DBType
        self.library = library or ''  # <content target= video, music, pictures, none>
        self.tmdb_id = tmdb_id or ''  # ListItem.Property(tmdb_id)
        self.imdb_id = imdb_id or ''  # IMDb ID for item
        self.poster = poster
        self.thumb = thumb
        self.icon = icon or '{0}/resources/poster.png'.format(self.addonpath)
        self.fanart = fanart or '{0}/fanart.jpg'.format(self.addonpath)
        self.cast = cast or []  # Cast list
        self.is_folder = is_folder
        self.infolabels = infolabels or {}  # ListItem.Foobar
        self.infoproperties = infoproperties or {}  # ListItem.Property(Foobar)
        self.infoart = {'thumb': self.thumb, 'icon': self.icon, 'poster': self.poster, 'fanart': self.fanart}
        if dbid:
            self.infolabels['dbid'] = dbid

    def get_url(self, **kwargs):
        url = kwargs.pop('url', 'plugin://plugin.video.themoviedb.helper/?')
        return '{0}{1}'.format(url, urlencode(kwargs))

    def create_listitem(self, handle=None, **kwargs):
        listitem = xbmcgui.ListItem(label=self.label, label2=self.label2)
        listitem.setLabel2(self.label2)
        listitem.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': self.tmdb_id})
        listitem.setInfo(self.library, self.infolabels)
        listitem.setProperties(self.infoproperties)
        listitem.setArt(self.infoart)
        listitem.setCast(self.cast)
        xbmcplugin.addDirectoryItem(handle, self.get_url(**kwargs), listitem, self.is_folder)
