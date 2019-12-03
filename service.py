import xbmc
import xbmcgui
from resources.lib.plugin import Plugin
import resources.lib.utils as utils


class ServiceMonitor(Plugin):
    def __init__(self):
        super(ServiceMonitor, self).__init__()
        self.kodimonitor = xbmc.Monitor()
        self.container = ''
        self.cur_item = 0
        self.pre_item = 1
        self.setprops = []
        self.home = xbmcgui.Window(10000)
        self.run_monitor()

    def run_monitor(self):
        while not self.kodimonitor.abortRequested():
            if xbmc.getCondVisibility("!Skin.HasSetting(TMDbHelper.Service)"):
                self.kodimonitor.waitForAbort(30)
            # skip when modal dialogs are opened (e.g. textviewer in musicinfo dialog)
            elif xbmc.getCondVisibility(
                    "Window.IsActive(DialogSelect.xml) | Window.IsActive(progressdialog) | "
                    "Window.IsActive(contextmenu) | Window.IsActive(busydialog)"):
                self.kodimonitor.waitForAbort(2)

            # skip when container scrolling
            elif xbmc.getCondVisibility(
                    "Container.OnScrollNext | Container.OnScrollPrevious | Container.Scrolling"):
                self.kodimonitor.waitForAbort(1)  # Maybe clear props here too

            # media window is opened or widgetcontainer set - start listitem monitoring!
            elif xbmc.getCondVisibility(
                    "Window.IsMedia | !String.IsEmpty(Window(Home).Property(TMDbHelper.WidgetContainer))"):
                self.get_listitem()
                self.kodimonitor.waitForAbort(0.15)

            # clear window props
            else:
                self.clear_properties()
                self.kodimonitor.waitForAbort(1)

    def clear_properties(self):
        for key in self.setprops:
            try:
                self.home.clearProperty(u'TMDbHelper.ListItem.{0}'.format(key))
            except Exception:
                pass
        self.setprops = []

    def set_property(self, key, value):
        try:
            self.home.setProperty(u'TMDbHelper.ListItem.{0}'.format(key), u'{0}'.format(value))
        except Exception as exc:
            utils.kodi_log('{0}{1}'.format(key, exc), 1)

    def set_iter_properties(self, dictionary):
        for k, v in dictionary.items():
            if isinstance(v, list):
                idx = 0
                self.set_property(k, v[idx])
                self.setprops.append(k)
                for i in v:
                    p = '{0}.{1}'.format(k, idx + 1)
                    self.set_property(p, v[idx])
                    self.setprops.append(p)
                    idx += 1
                continue
            self.setprops.append(k)
            self.set_property(k, v)

    def set_properties(self, item):
        self.setprops = ['Label', 'Icon', 'Poster', 'Thumb', 'Fanart', 'tmdb_id', 'imdb_id']
        self.set_property('Label', item.get('label'))
        self.set_property('Icon', item.get('icon'))
        self.set_property('Poster', item.get('poster'))
        self.set_property('Thumb', item.get('thumb'))
        self.set_property('Fanart', item.get('fanart'))
        self.set_property('tmdb_id', item.get('tmdb_id'))
        self.set_property('imdb_id', item.get('imdb_id'))
        self.set_iter_properties(item.get('infolabels', {}))
        self.set_iter_properties(item.get('infoproperties', {}))

    def get_container(self):
        widgetid = utils.try_parse_int(self.home.getProperty('TMDbHelper.WidgetContainer'))
        return 'Container({0}).'.format(widgetid) if widgetid else 'Container.'

    def get_dbtype(self):
        dbtype = xbmc.getInfoLabel('ListItem.DBTYPE'.format(self.container))
        return '{0}s'.format(dbtype) if dbtype else xbmc.getInfoLabel('Container.Content()') or ''

    def get_infolabel(self, infolabel):
        return xbmc.getInfoLabel('{0}ListItem.{1}'.format(self.container, infolabel))

    def get_tmdb_id(self, itemtype, imdb_id=None, query=None, year=None):
        try:
            if imdb_id and imdb_id.startswith('tt'):
                return self.tmdb.get_tmdb_id(itemtype=itemtype, imdb_id=imdb_id)
            return self.tmdb.get_tmdb_id(itemtype=itemtype, query=query, year=year)
        except Exception:
            return

    def get_listitem(self):
        self.container = self.get_container()

        dbtype = self.get_dbtype()
        if dbtype in ['tvshows', 'seasons', 'episodes']:
            tmdbtype = 'tv'
        elif dbtype in ['movies']:
            tmdbtype = 'movie'
        else:
            return  # TODO: Add checks for sets etc.

        imdb_id = self.get_infolabel('IMDBNumber')
        query = self.get_infolabel('TvShowTitle') or self.get_infolabel('Title') or self.get_infolabel('Label')
        year = self.get_infolabel('year')
        season = self.get_infolabel('Season') if dbtype == 'episodes' else ''
        episode = self.get_infolabel('Episode') if dbtype == 'episodes' else ''

        self.cur_item = '{0}.{1}.{2}.{3}.{4}'.format(imdb_id, query, year, season, episode)
        if self.cur_item == self.pre_item:
            return  # Don't get details if we already did last time!
        self.pre_item = self.cur_item

        try:
            details = self.tmdb.get_detailed_item(tmdbtype, self.get_tmdb_id(tmdbtype, imdb_id, query, year), season=season, episode=episode)
            details = self.get_omdb_ratings(details)
        except Exception:
            return

        if not details:
            return

        self.set_properties(details)


if __name__ == '__main__':
    ServiceMonitor()
