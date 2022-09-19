import xbmcgui
from xbmc import Monitor
from resources.lib.items.router import Router
from resources.lib.addon.dialog import BusyDialog
from resources.lib.addon.thread import ParallelThread
from resources.lib.addon.plugin import get_infolabel, executebuiltin, get_condvisibility, ADDONPATH
from resources.lib.api.tmdb.api import TMDb
from resources.lib.addon.logger import kodi_log


TMDB_QUERY_PARAMS = ('imdb_id', 'tvdb_id', 'query', 'year', 'episode_year',)
PROP_LIST_VISIBLE = 'List_{}_Visible'
PROP_LIST_ISUPDATING = 'List_{}_IsUpdating'
ACTION_CONTEXT_MENU = (117,)
ACTION_SHOW_INFO = (11,)
ACTION_SELECT = (7, )
ACTION_CLOSEWINDOW = (9, 10, 92, 216, 247, 257, 275, 61467, 61448,)
CALL_AUTO = 1190
ANIMATION_DELAY = 1


class WindowRecommendations(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self._mon = Monitor()
        self._tmdb_api = TMDb()
        self._tmdb_type = kwargs['tmdb_type']
        self._tmdb_affix = '&nextpage=false&fanarttv=false&cacheonly=true'
        self._tmdb_query = {i: kwargs[i] for i in TMDB_QUERY_PARAMS if kwargs.get(i)}
        self._tmdb_id = kwargs.get('tmdb_id') or self._tmdb_api.get_tmdb_id(tmdb_type=self._tmdb_type, **self._tmdb_query)
        self._recommendations = sorted(kwargs['recommendations'].split('||'))
        self._recommendations = {
            int(list_id): {'list_id': int(list_id), 'url': url, 'related': related.lower() == 'true', 'action': action}
            for list_id, url, related, action in (i.split('|') for i in self._recommendations)}
        self._queue = (i for i in self._recommendations)
        self._cache = {}
        self._list_id = None
        self._context_action = kwargs.get('context')

    def onInit(self):
        if not self._tmdb_id or not self._recommendations:
            return self.close()

        # Build first list separately then thread rest
        with BusyDialog():
            self._build_next()
        if not self._next_id:
            return self.close()

        self._build_all_in_groups(3)  # Build remaining lists in groups of three to balance performance
        self.setProperty(PROP_LIST_VISIBLE.format('All'), 'True')

    def _build_all_in_groups(self, x):
        """ Build remaining queue in threaded groups of x items
        PRO: Balances performance for displaying next list in queue and building all lists
        CON: Queued lists might be added slightly out of order
        """
        def _threaditem(i):
            self._add_items(i, self.build_list(i))

        from itertools import zip_longest
        for _items in zip_longest(*[iter(self._queue)] * x, fillvalue=None):
            with ParallelThread(_items, _threaditem):
                if self._next_id:
                    self._mon.waitForAbort(0.1)  # Wait to ensure first list is visible
                    self.setFocusId(self._next_id)  # Setfocus to first list id
                    self._next_id = None

    def _build_all_consecutively(self):
        """ Build remaining queue in serial order
        PRO: Fastest performance for displaying the next list in queue. Lists added in order.
        CON: Slowest performance for building all lists.
        """
        self._mon.waitForAbort(0.1)  # Wait to ensure first list is visible
        self.setFocusId(self._next_id)

        for i in self._queue:
            self._add_items(i, self.build_list(i))

    def _build_all_threaded_order(self):
        """ Build remaining queue in parallel but added in order
        PRO: Fastest performance for building all lists. Lists added in order.
        CON: Slowest performance for displaying next list in queue.
        """
        self._list_id = self._next_id
        self._items = [i for i in self._queue]
        self._queue = (i for i in self._items)
        self._get_next_id()

        def _threaditem(i):
            self._cache[i] = self.build_list(i)
            if self._next_id in self._cache:
                self._add_items(self._next_id, self._cache[self._next_id])
                self._get_next_id()

        with ParallelThread(self._items, _threaditem):
            self._mon.waitForAbort(0.1)  # Wait to ensure first list is visible
            self.setFocusId(self._list_id)  # Setfocus to first list id

        for i in self._queue:
            self._add_items(i, self._cache.get(i))

    def onAction(self, action):
        _action_id = action.getId()
        if _action_id in ACTION_CLOSEWINDOW:
            return self.close()
        if _action_id in ACTION_SHOW_INFO:
            return self.do_action()
        if _action_id in ACTION_CONTEXT_MENU:
            return executebuiltin(self._context_action) if self._context_action else self.do_action()
        if _action_id in ACTION_SELECT:
            return self.do_action()

    def do_action(self):
        _fid = self.getFocusId()
        _action = self._recommendations.get(_fid, {}).get('action')
        if not _action:
            return
        if _action in ['info', 'play', 'browse']:
            path = get_infolabel(f'Container({_fid}).ListItem.FolderPath') if _fid else None
            return self.do_windowmanager_action(path, _action)
        if _action == 'textviewer':
            plot = get_infolabel(f'Container({_fid}).ListItem.Plot') if _fid else None
            return xbmcgui.Dialog().textviewer('', plot) if plot else None
        return executebuiltin(_action)

    def do_windowmanager_action(self, path, action):
        self.close()
        if not path:
            return
        self._mon.waitForAbort(ANIMATION_DELAY)
        from resources.lib.window.manager import WindowManager
        if action == 'play':
            return WindowManager(playmedia=path, close_dialog=True).router()
        if action == 'browse':
            if get_condvisibility('Window.IsVisible(MyVideoNav.xml)'):
                return WindowManager(call_update=path, close_dialog=True).router()
            return WindowManager(call_path=path, close_dialog=True).router()
        if action == 'info':
            WindowManager(add_path=path, call_auto=CALL_AUTO).router()

    def _build_next(self):
        _listitems = self.build_list(self._get_next_id())
        return self._add_items(self._next_id, _listitems) if _listitems else self._build_next()

    def _get_items(self, path):
        listitems = Router(-1, path).get_directory(items_only=True) or []
        listitems = [li.get_listitem(offscreen=True) for li in listitems if li]
        return listitems

    def _get_next_id(self):
        try:
            self._next_id = next(self._queue)
        except StopIteration:
            self._next_id = None
        return self._next_id

    def _add_items(self, list_id, listitems):
        self.clearProperty(PROP_LIST_ISUPDATING.format(list_id))
        if not list_id or not listitems:
            return
        try:
            _lst = self.getControl(list_id)
        except (RuntimeError, TypeError):  # List with that ID doesn't exist so don't build it
            return
        _lst.addItems(listitems)
        self.setProperty(PROP_LIST_VISIBLE.format(list_id), 'True')

    def build_list(self, list_id):
        try:
            self.getControl(list_id)
        except (RuntimeError, TypeError):  # List with that ID doesn't exist so don't build it
            return

        self.setProperty(PROP_LIST_ISUPDATING.format(list_id), 'True')

        affx = f'&tmdb_type={self._tmdb_type}&tmdb_id={self._tmdb_id}' if self._recommendations[list_id]['related'] else ''
        path = f'{self._recommendations[list_id]["url"]}{affx}{self._tmdb_affix}'

        return self._get_items(path)


def open_recommendations_gui(recommendations, tmdb_type, **kwargs):
    kodi_log([f"Opening {tmdb_type.capitalize()} Recommendations GUI\n", '\n'.join(recommendations.split('||')), '\n', kwargs], 2)
    ui = WindowRecommendations(
        'script-tmdbhelper-recommendations.xml', ADDONPATH, 'default', '1080i',
        recommendations=recommendations, tmdb_type=tmdb_type, **kwargs)
    ui.doModal()
    del ui
