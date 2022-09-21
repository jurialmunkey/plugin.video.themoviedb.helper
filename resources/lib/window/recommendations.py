import xbmcgui
from xbmc import Monitor
from itertools import zip_longest
from resources.lib.items.router import Router
from resources.lib.addon.dialog import BusyDialog
from resources.lib.addon.thread import ParallelThread
from resources.lib.addon.plugin import get_infolabel, executebuiltin, get_condvisibility, ADDONPATH
from resources.lib.api.tmdb.api import TMDb
from resources.lib.addon.window import get_property
from tmdbhelper.parser import parse_paramstring, reconfigure_legacy_params
from threading import Thread


TMDB_QUERY_PARAMS = ('imdb_id', 'tvdb_id', 'query', 'year', 'episode_year',)
PROP_LIST_VISIBLE = 'List_{}_Visible'
PROP_LIST_ISUPDATING = 'List_{}_IsUpdating'
PROP_LISTITEM = 'Recommendations.ListItem.{}'
PROP_POSITION = 'Recommendations.Position'
PROP_PREVIOUS = 'Recommendations.Previous'
PROP_HIDEINFO = 'Recommendations.HideInfo'
PROP_HIDERECS = 'Recommendations.HideRecs'
PROP_TMDBTYPE = 'Recommendations.TMDbType'

ACTION_CONTEXT_MENU = (117,)
ACTION_SHOW_INFO = (11,)
ACTION_SELECT = (7, )
ACTION_CLOSEWINDOW = (9, 10, 92, 216, 247, 257, 275, 61467, 61448,)


"""
Runscript(plugin.video.themoviedb.helper,recommendations=)
recommendations=list_id(int)|paramstring(str)|related(bool)|action(str) [Separate multiples with || ]
    * The lists to add. Separate additional lists with ||
    * list_id: the container that the items will be added
    * paramstring: the tmdbhelper base path such as info=cast
    * related: whether to add related query params to the paramstring
    * action: the action to perform. can be info|play|text or a Kodi builtin
window_id=window_id(int)
    * The custom window that will act as the base window
setproperty=property(str)
    * Sets Window(Home).Property(TMDbHelper.{property}) to True oninfo until infodialog closes
tmdb_type=type(str)
    * The type of item for related paramstrings
tmdb_id=tmdb_id(int)
    * The tmdb_id for the base item lookup. Optionally can use other standard query= params for lookup
context=builtin(str)
    * The Kodi builtin to call oncontextmenu action
    * If ommitted then standard action for list will be performed

script-tmdbhelper-recommendations.xml
<onload>SetProperty(Action_{list_id},action)</onload>
    * Set an action for an undefined list

DialogVideoInfo.xml
<onunload>Runscript(plugin.video.themoviedb.helper,recommendations=onback,window_id=1191)</onunload>
    * Load previous item in history
"""


class WindowRecommendations(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
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
        self._window_id = kwargs['window_id']
        self._setproperty = kwargs.get('setproperty')
        self._window_properties = {
            k.replace('winprop_', ''): v
            for k, v in kwargs.items()
            if k and k.startswith('winprop_')}
        self._kwargs = kwargs
        self._initialised = False
        get_property(PROP_TMDBTYPE, self._tmdb_type)

    def onInit(self):
        for k, v in self._window_properties.items():
            self.setProperty(k, v)

        if self._initialised:
            return

        self._initialised = True

        if not self._tmdb_id or not self._recommendations:
            return self.close()

        # Build first two lists individually then thread rest
        with BusyDialog():
            _list_id = self._build_next()
            if not _list_id:
                return self.close()
            self._build_next()

        # Build rest of the lists threaded in groups of three
        self._build_all_in_groups(3, _list_id)
        self.setProperty(PROP_LIST_VISIBLE.format('All'), 'True')

    def _build_next(self):
        try:
            _next_id = next(self._queue)
        except StopIteration:
            return
        _listitems = self.build_list(_next_id)
        return self._add_items(_next_id, _listitems) if _listitems else self._build_next()

    def _build_all_in_groups(self, x, list_id):
        """ Build remaining queue in threaded groups of x items
        PRO: Balances performance for displaying next list in queue and building all lists
        CON: Queued lists might be added slightly out of order
        """
        def _threaditem(i):
            self._add_items(i, self.build_list(i))

        for _items in zip_longest(*[iter(self._queue)] * x, fillvalue=None):
            with ParallelThread(_items, _threaditem) as pt:
                if list_id:
                    Monitor().waitForAbort(0.1)  # Wait to ensure first list is visible
                    self.setFocusId(list_id)  # Setfocus to first list id
                    list_id = None
                pt._exit = True

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
        focus_id = self.getFocusId()
        _action = self._recommendations.get(focus_id, {}).get('action') or self.getProperty(f'Action_{focus_id}')
        if not _action:
            return
        if _action == 'info':
            return self.do_info(focus_id)
        if _action == 'play':
            return self.do_play(focus_id)
        if _action == 'text':
            return self.do_text(focus_id)
        return executebuiltin(_action)

    def do_text(self, focus_id):
        if not focus_id:
            return
        xbmcgui.Dialog().textviewer('', get_infolabel(f'Container({focus_id}).ListItem.Plot'))

    def do_play(self, focus_id):
        if not focus_id:
            return
        path = get_infolabel(f'Container({focus_id}).ListItem.FolderPath')
        if get_condvisibility(f'Container({focus_id}).ListItem.IsFolder'):
            return  # TODO: Browse
        executebuiltin(f'PlayMedia({path})')

    def do_info(self, focus_id):
        get_property(PROP_HIDEINFO, clear_property=True)
        if not focus_id:
            return
        path = get_infolabel(f'Container({focus_id}).ListItem.FolderPath')
        if not path:
            return

        _wrm = WindowRecommendationsManager(self._window_id)

        try:
            _params = reconfigure_legacy_params(**parse_paramstring(path.split('?')[1]))
            listitem = _wrm.get_listitem(_params['tmdb_type'], _params['tmdb_id'])
        except (TypeError, IndexError, KeyError, AttributeError):
            return

        if self._setproperty:
            get_property(self._setproperty, 'True')

        if get_condvisibility('Window.IsVisible(movieinformation)'):
            get_property(PROP_HIDERECS, 'True')

        _pos = get_property(PROP_POSITION) or '0'
        _wrm.increment_pos(self._tmdb_type, self._tmdb_id)
        _wrm.open_infodialog(listitem, self.close, threaded=False)

        Monitor().waitForAbort(1)
        _new = get_property(PROP_POSITION)

        if self._setproperty:
            get_property(self._setproperty, clear_property=True)

        if _pos == _new:
            get_property(PROP_TMDBTYPE, self._tmdb_type)
            self.doModal()
        else:
            self.close()
        get_property(PROP_HIDEINFO, clear_property=True)

    def _get_items(self, path):
        listitems = Router(-1, path).get_directory(items_only=True) or []
        listitems = [li.get_listitem(offscreen=True) for li in listitems if li]
        return listitems

    def _add_items(self, list_id, listitems):
        if not list_id or not listitems:
            return
        try:
            _lst = self.getControl(list_id)
        except (RuntimeError, TypeError):  # List with that ID doesn't exist so don't build it
            return
        _lst.addItems(listitems)
        self.setProperty(PROP_LIST_VISIBLE.format(list_id), 'True')
        return list_id

    def build_list(self, list_id):
        try:
            self.getControl(list_id)
        except (RuntimeError, TypeError):  # List with that ID doesn't exist so don't build it
            return

        self.setProperty(PROP_LIST_ISUPDATING.format(list_id), 'True')

        affx = f'&tmdb_type={self._tmdb_type}&tmdb_id={self._tmdb_id}' if self._recommendations[list_id]['related'] else ''
        path = f'{self._recommendations[list_id]["url"]}{affx}{self._tmdb_affix}'

        _listitems = self._get_items(path)
        self.clearProperty(PROP_LIST_ISUPDATING.format(list_id))
        return _listitems


class WindowRecommendationsManager():
    def __init__(self, window_id):
        self._window_id = int(window_id) + 10000 if int(window_id) < 10000 else int(window_id)

    def finished(self, builtin=None, after=False, **kwargs):
        get_property(PROP_PREVIOUS, clear_property=True)
        get_property(PROP_POSITION, clear_property=True)
        executebuiltin(builtin) if builtin and not after else None
        executebuiltin(f'Dialog.Close(movieinformation,true)')
        Monitor().waitForAbort(1)
        if xbmcgui.getCurrentWindowId() == self._window_id:
            _win = xbmcgui.Window(self._window_id)
            _win.close() if _win else None
        executebuiltin(builtin) if builtin and after else None

    def open_infodialog(self, listitem, func=None, threaded=False):
        if not listitem:
            return
        if get_condvisibility('Window.IsVisible(movieinformation)'):
            executebuiltin(f'Dialog.Close(movieinformation,true)')
        func() if func else None
        if xbmcgui.getCurrentWindowId() != self._window_id:
            executebuiltin(f'ActivateWindow({self._window_id})')
        if threaded:
            Thread(target=xbmcgui.Dialog().info, args=[listitem]).start()
        else:
            xbmcgui.Dialog().info(listitem)

    def open_new_infodialog(self, tmdb_type, tmdb_id, **kwargs):
        tmdb_query = {i: kwargs[i] for i in TMDB_QUERY_PARAMS if kwargs.get(i)}
        tmdb_id = tmdb_id or TMDb().get_tmdb_id(tmdb_type=tmdb_type, **tmdb_query)

        try:
            listitem = self.get_listitem(tmdb_type, tmdb_id)
        except (TypeError, IndexError, KeyError, AttributeError):
            return

        self.open_infodialog(listitem, threaded=False)

    @staticmethod
    def get_listitem(tmdb_type, tmdb_id):
        with BusyDialog():
            try:
                _path = f"info=details&tmdb_type={tmdb_type}&tmdb_id={tmdb_id}"
                return Router(-1, _path).get_directory(items_only=True)[0].get_listitem()
            except (TypeError, IndexError, KeyError, AttributeError):
                return

    @staticmethod
    def increment_pos(tmdb_type, tmdb_id):
        _pre = int(get_property(PROP_POSITION) or 0)
        _pos = _pre + 1
        get_property(PROP_PREVIOUS, f'{_pre}')
        get_property(PROP_POSITION, f'{_pos}')
        get_property(PROP_LISTITEM.format(_pos), f'{tmdb_type}|{tmdb_id}')

    @staticmethod
    def deincrement_pos():
        _pre = int(get_property(PROP_POSITION) or 0)
        _pos = _pre - 1
        get_property(PROP_PREVIOUS, f'{_pre}')
        get_property(PROP_POSITION, f'{_pos}')
        return get_property(PROP_LISTITEM.format(_pre), clear_property=True)

    def open_previous_info(self):
        # Transition property set so we're already changing windows
        if get_property(PROP_HIDERECS, clear_property=True):
            return

        # Get the previous property position and clear that property
        _hid = int(get_property(PROP_POSITION) or 0) - 1 == int(get_property(PROP_PREVIOUS) or -1)
        _pre = self.deincrement_pos()

        # Not on special window so just allow dialog to close
        if xbmcgui.getCurrentWindowId() != self._window_id:
            return self.finished()

        try:
            self.open_infodialog(self.get_listitem(*_pre.split('|')), threaded=True)
        except (ValueError, AttributeError, TypeError):
            return self.finished()

        get_property(PROP_HIDEINFO, 'True') if _hid else None


def open_recommendations_gui(recommendations, window_id, **kwargs):
    if recommendations == 'onback':
        return WindowRecommendationsManager(window_id).open_previous_info()
    if recommendations == 'onaction':
        return WindowRecommendationsManager(window_id).finished(**kwargs)
    if recommendations == 'oninfo':
        return WindowRecommendationsManager(window_id).open_new_infodialog(**kwargs)
    ui = WindowRecommendations(
        'script-tmdbhelper-recommendations.xml', ADDONPATH, 'default', '1080i',
        recommendations=recommendations, window_id=window_id, **kwargs)
    ui.doModal()
    del ui
