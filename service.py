import xbmc
import xbmcgui
from resources.lib.plugin import Plugin
import resources.lib.utils as utils
_setmain = {'label', 'icon', 'poster', 'thumb', 'fanart', 'cast', 'tmdb_id', 'imdb_id'}
_setinfo = {
    'title', 'originaltitle', 'tvshowtitle', 'plot', 'rating', 'votes', 'premiered', 'year', 'imdbnumber', 'tagline',
    'status', 'episode', 'season', 'genre', 'duration', 'set', 'studio', 'country', 'MPAA', 'director', 'writer'}
_setprop = {
    'tvdb_id', 'biography', 'birthday', 'age', 'deathday', 'character', 'department', 'job', 'known_for', 'role',
    'born', 'creator', 'aliases', 'budget', 'revenue', 'set.tmdb_id', 'set.name', 'set.poster', 'set.fanart',
    'awards', 'metacritic_rating', 'imdb_rating', 'imdb_votes', 'rottentomatoes_rating', 'rottentomatoes_image',
    'rottentomatoes_reviewtotal', 'rottentomatoes_reviewsfresh', 'rottentomatoes_reviewsrotten',
    'rottentomatoes_consensus', 'rottentomatoes_usermeter', 'rottentomatoes_userreviews'}
_setiter = {
    'Cast': ['name', 'role', 'thumb'],
    'Crew': ['name', 'job', 'department', 'thumb'],
    'Creator': ['name', 'tmdb_id'],
    'Genre': ['name', 'tmdb_id'],
    'Studio': ['name', 'tmdb_id'],
    'Country': ['name', 'tmdb_id'],
    'Language': ['name', 'iso'],
    'known_for': ['title', 'tmdb_id', 'rating', 'tmdb_type']}


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
        self.properties = set()
        self.home = xbmcgui.Window(10000)
        self.run_monitor()

    def run_monitor(self):
        self.home.setProperty('TMDbHelper.ServiceStarted', 'True')
        while not self.kodimonitor.abortRequested():
            self.get_container()

            self.cur_folder = '{0}{1}{2}'.format(
                self.container,
                xbmc.getInfoLabel(self.get_dbtype()),
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
            elif self.properties:
                self.clear_properties()  # TODO: Also clear when container paths change

            else:
                self.kodimonitor.waitForAbort(1)

    def reset_properties(self):
        self.properties = self.properties.union(_setmain, _setinfo, _setprop)
        self.clear_properties()
        self.clear_iterprops()

    def clear_iterprops(self):
        self.high_idx = self.high_idx if self.high_idx > 10 else 10
        for k, v in _setiter.items():
            for n in v:
                for i in range(self.high_idx):
                    try:
                        self.home.clearProperty('TMDbHelper.ListItem.{0}.{1}.{2}'.format(k, i, n))
                    except Exception:
                        pass
        self.high_idx = 0

    def clear_property(self, key):
        try:
            self.home.clearProperty('TMDbHelper.ListItem.{0}'.format(key))
        except Exception as exc:
            utils.kodi_log('{0}{1}'.format(key, exc), 1)

    def clear_properties(self):
        for k in self.properties:
            self.clear_property(k)
        self.properties = set()
        self.pre_item = None

    def set_property(self, key, value):
        try:
            self.home.setProperty('TMDbHelper.ListItem.{0}'.format(key), u'{0}'.format(value))
        except Exception as exc:
            utils.kodi_log('{0}{1}'.format(key, exc), 1)

    def set_indx_properties(self, dictionary):
        if not isinstance(dictionary, dict):
            return
        pre_name = ''
        pre_affix = ''
        idx = 0
        for k, v in sorted(dictionary.items()):
            if '.' not in k:
                continue
            try:
                cur_name, pos, cur_affix = k.split('.')
                if cur_name != pre_name or cur_affix != pre_affix:  # If we've moved to next lot gotta clear higher props
                    if self.high_idx > idx:
                        for n in range(idx, self.high_idx):
                            n += 1
                            self.clear_property('{0}.{1}.{2}'.format(pre_name, n, pre_affix))
                pre_name, pre_affix = cur_name, cur_affix
                idx = utils.try_parse_int(pos)
                self.high_idx = idx if idx > self.high_idx else self.high_idx

                v = v or ''
                self.properties.add(k)
                self.set_property(k, v)
            except Exception as exc:
                utils.kodi_log('k: {0} v: {1} e: {2}'.format(k, v, exc), 1)

    def set_iter_properties(self, dictionary, keys):
        if not isinstance(dictionary, dict):
            return
        for k in keys:
            try:
                v = dictionary.get(k)
                v = v or ''
                if isinstance(v, list):
                    n = ''
                    for i in v:
                        if not i:
                            continue
                        try:
                            n = '{0} / {1}'.format(n, i) if n else i
                        except Exception as exc:
                            utils.kodi_log(exc, 1)
                    v = n if n else v
                self.properties.add(k)
                self.set_property(k, v)
            except Exception as exc:
                'k: {0} e: {1}'.format(k, exc)

    def set_properties(self, item):
        self.set_iter_properties(item, _setmain)
        self.set_iter_properties(item.get('infolabels', {}), _setinfo)
        self.set_iter_properties(item.get('infoproperties', {}), _setprop)
        self.set_indx_properties(item.get('infoproperties', {}))
        self.home.clearProperty('TMDbHelper.IsUpdating')

    def get_container(self):
        widgetid = utils.try_parse_int(self.home.getProperty('TMDbHelper.WidgetContainer'))
        self.container = 'Container({0}).'.format(widgetid) if widgetid else 'Container.'
        self.containeritem = '{0}ListItem.'.format(self.container) if not xbmc.getCondVisibility("Window.IsVisible(movieinformation)") else 'ListItem.'

    def get_dbtype(self):
        dbtype = xbmc.getInfoLabel('{0}DBTYPE'.format(self.containeritem))
        return '{0}s'.format(dbtype) if dbtype else xbmc.getInfoLabel('Container.Content()') or ''

    def get_infolabel(self, infolabel):
        return xbmc.getInfoLabel('{0}{1}'.format(self.containeritem, infolabel))

    def get_position(self):
        return xbmc.getInfoLabel('{0}CurrentItem'.format(self.container))

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
        elif dbtype in ['sets']:
            tmdbtype = 'collection'

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

        self.home.setProperty('TMDbHelper.IsUpdating', 'True')

        try:
            details = self.tmdb.get_detailed_item(tmdbtype, self.get_tmdb_id(tmdbtype, imdb_id, query, year), season=season, episode=episode)
            details = self.get_omdb_ratings(details)
        except Exception as exc:
            utils.kodi_log(exc, 1)

        if not details:
            self.home.clearProperty('TMDbHelper.IsUpdating')
            return

        self.set_properties(details)


if __name__ == '__main__':
    ServiceMonitor()
