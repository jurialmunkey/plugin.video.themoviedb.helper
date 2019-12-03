import xbmc
import xbmcgui
from resources.lib.plugin import Plugin
import resources.lib.utils as utils


class ServiceMonitor(Plugin):
    def __init__(self):
        super(ServiceMonitor, self).__init__()
        self.kodimonitor = xbmc.Monitor()
        self.container = 'Container.'
        self.containeritem = 'ListItem.'
        self.cur_item = 0
        self.pre_item = 1
        self.high_idx = 0
        self.pre_folder = None
        self.cur_folder = None
        self.setprops = []
        self.home = xbmcgui.Window(10000)
        self.run_monitor()

    def run_monitor(self):
        while not self.kodimonitor.abortRequested():
            self.get_container()

            self.cur_folder = '{0}{1}{2}'.format(
                self.container,
                xbmc.getInfoLabel('{0}Content()'.format(self.container)),
                xbmc.getInfoLabel('{0}NumItems'.format(self.container)))

            if xbmc.getCondVisibility("!Skin.HasSetting(TMDbHelper.Service)"):
                self.kodimonitor.waitForAbort(30)

            elif self.cur_folder != self.pre_folder:
                self.reset_properties()
                self.pre_folder = self.cur_folder
                self.kodimonitor.waitForAbort(2)

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
                    "Window.IsMedia | !String.IsEmpty(Window(Home).Property(TMDbHelper.WidgetContainer)) | Window.IsVisible(movieinformation)"):
                self.get_listitem()
                self.kodimonitor.waitForAbort(0.15)

            # clear window props
            elif self.setprops:
                self.clear_properties()  # TODO: Also clear when container paths change

            else:
                self.kodimonitor.waitForAbort(1)

    def reset_properties(self):
        self.setprops = {
            'Label', 'Icon', 'Poster', 'Thumb', 'Fanart', 'tmdb_id', 'imdb_id', 'title', 'originaltitle',
            'tvshowtitle', 'plot', 'rating', 'votes', 'premiered', 'year', 'imdbnumber', 'tagline', 'status',
            'episode', 'season', 'genre', 'duration', 'set', 'studio', 'country', 'MPAA', 'tvdb_id', 'biography',
            'birthday', 'age', 'deathday', 'character', 'department', 'job', 'known_for', 'role', 'born', 'creator',
            'director', 'writer', 'aliases', 'known_for', 'budget', 'revenue', 'set.tmdb_id', 'set.name', 'set.poster',
            'set.fanart', 'awards', 'metacritic_rating', 'imdb_rating', 'imdb_votes', 'rottentomatoes_rating',
            'rottentomatoes_image', 'rottentomatoes_reviewtotal', 'rottentomatoes_reviewsfresh', 'rottentomatoes_reviewsrotten',
            'rottentomatoes_consensus', 'rottentomatoes_usermeter', 'rottentomatoes_userreviews'}
        self.clear_properties()
        self.clear_iterprops()

    def clear_iterprops(self):
        iterprops = {
            'Cast': ['name', 'role', 'thumb'],
            'Crew': ['name', 'job', 'department', 'thumb'],
            'Creator': ['name', 'tmdb_id'],
            'Genre': ['name', 'tmdb_id'],
            'Studio': ['name', 'tmdb_id'],
            'Country': ['name', 'tmdb_id'],
            'Language': ['name', 'iso'],
            'known_for': ['title', 'tmdb_id', 'rating', 'tmdb_type']}
        self.high_idx = self.high_idx if self.high_idx > 10 else 10
        for k, v in iterprops.items():
            for n in v:
                for i in range(self.high_idx):
                    try:
                        self.home.clearProperty('TMDbHelper.ListItem.{0}.{1}.{2}'.format(k, i, n))
                    except Exception:
                        pass

    def clear_properties(self):
        for k in self.setprops:
            try:
                self.home.clearProperty('TMDbHelper.ListItem.{0}'.format(k))
            except Exception:
                pass
        self.setprops = {}

    def set_property(self, key, value):
        try:
            self.home.setProperty('TMDbHelper.ListItem.{0}'.format(key), u'{0}'.format(value))
        except Exception as exc:
            utils.kodi_log('{0}{1}'.format(key, exc), 1)

    def set_iter_properties(self, dictionary):
        if not isinstance(dictionary, dict):
            return
        for k, v in dictionary.items():
            try:
                if isinstance(v, list):
                    idx = 0
                    self.set_property(k, v[idx])
                    self.setprops.add(k)
                    for i in v:
                        try:
                            p = '{0}.{1}'.format(k, idx + 1)
                            self.set_property(p, i)
                            self.setprops.add(p)
                            idx += 1
                        except Exception as exc:
                            utils.kodi_log(exc, 1)
                    self.high_idx = idx if idx > self.high_idx else self.high_idx
                    continue
                self.setprops.add(k)
                self.set_property(k, v)
            except Exception as exc:
                utils.kodi_log(exc, 1)

    def set_properties(self, item):
        self.setprops = {'Label', 'Icon', 'Poster', 'Thumb', 'Fanart', 'tmdb_id', 'imdb_id'}
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
        self.container = 'Container({0}).'.format(widgetid) if widgetid else 'Container.'
        self.containeritem = '{0}ListItem.'.format(self.container) if not xbmc.getCondVisibility("Window.IsVisible(movieinformation)") else 'ListItem.'

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
        except Exception as exc:
            utils.kodi_log(exc, 1)
            return

    def get_listitem(self):
        self.get_container()

        tmdbtype = ''
        dbtype = self.get_dbtype()
        if dbtype in ['tvshows', 'seasons', 'episodes']:
            tmdbtype = 'tv'
        elif dbtype in ['movies']:
            tmdbtype = 'movie'

        imdb_id = self.get_infolabel('IMDBNumber')
        query = self.get_infolabel('TvShowTitle') or self.get_infolabel('Title') or self.get_infolabel('Label')
        year = self.get_infolabel('year')
        season = self.get_infolabel('Season') if dbtype == 'episodes' else ''
        episode = self.get_infolabel('Episode') if dbtype == 'episodes' else ''

        self.cur_item = '{0}.{1}.{2}.{3}.{4}'.format(imdb_id, query, year, season, episode)
        if self.cur_item == self.pre_item:
            return  # Don't get details if we already did last time!
        self.pre_item = self.cur_item

        if not tmdbtype:
            return

        try:
            details = self.tmdb.get_detailed_item(tmdbtype, self.get_tmdb_id(tmdbtype, imdb_id, query, year), season=season, episode=episode)
            details = self.get_omdb_ratings(details)
        except Exception as exc:
            utils.kodi_log(exc, 1)

        if not details:
            return

        self.set_properties(details)


if __name__ == '__main__':
    ServiceMonitor()
