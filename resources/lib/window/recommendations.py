import xbmcgui
from xbmc import Monitor
from resources.lib.items.router import Router
from resources.lib.addon.dialog import BusyDialog
from resources.lib.addon.thread import ParallelThread
from resources.lib.addon.plugin import get_infolabel, executebuiltin, get_condvisibility
from resources.lib.api.tmdb.api import TMDb


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
        self._recommendations = kwargs['recommendations'].split('||')
        self._recommendations = [
            {'list_id': int(list_id), 'url': url, 'related': related.lower() == 'true', 'action': action}
            for list_id, url, related, action in (i.split('|') for i in self._recommendations)]
        self._actions = {i['list_id']: i.pop('action') for i in self._recommendations}
        self._list_id = None

    def onInit(self):
        if not self._tmdb_id or not self._recommendations:
            return self.close()

        # Build first list separately then thread rest
        with BusyDialog():
            self._list_id = self.build_first_recommendation()
            if not self._list_id:
                return self.close()
            self.build_first_recommendation()

        def _threaditem(i):
            self.build_list(**i)

        with ParallelThread(self._recommendations, _threaditem):
            self._mon.waitForAbort(0.1)  # Wait to ensure first list is visible
            self.setFocusId(self._list_id)  # Setfocus to first list id

    def onAction(self, action):
        _action_id = action.getId()
        if _action_id in ACTION_CLOSEWINDOW:
            return self.close()
        if _action_id in ACTION_SHOW_INFO:
            return self.do_action()
        if _action_id in ACTION_CONTEXT_MENU:
            return self.do_action()
        if _action_id in ACTION_SELECT:
            return self.do_action()

    def do_action(self):
        _fid = self.getFocusId()
        _action = self._actions.get(_fid)
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

    def build_first_recommendation(self):
        _recommendation = self._recommendations.pop(0)
        _success = self.build_list(**_recommendation)
        if not _success and self._recommendations:
            return self.build_first_recommendation()  # Keep trying if we failed
        return int(_recommendation['list_id']) if _success else False

    def _get_items(self, path):
        listitems = Router(-1, path).get_directory(items_only=True) or []
        listitems = [li.get_listitem(offscreen=True) for li in listitems if li]
        return listitems

    def build_list(self, list_id, url, related):
        try:
            _lst = self.getControl(list_id)
        except RuntimeError:  # List with that ID doesn't exist so don't build it
            return
        self.setProperty(PROP_LIST_VISIBLE.format(list_id), 'True')
        self.setProperty(PROP_LIST_ISUPDATING.format(list_id), 'True')
        affx = f'&tmdb_type={self._tmdb_type}&tmdb_id={self._tmdb_id}' if related else ''
        path = f'{url}{affx}{self._tmdb_affix}'
        listitems = self._get_items(path)
        if not listitems:
            self.clearProperty(PROP_LIST_ISUPDATING.format(list_id))
            self.clearProperty(PROP_LIST_VISIBLE.format(list_id))
            return
        _lst.addItems(listitems)
        self.clearProperty(PROP_LIST_ISUPDATING.format(list_id))
        return True


def open_recommendations_gui(recommendations, tmdb_type, **kwargs):
    from resources.lib.addon.plugin import ADDONPATH

    ui = WindowRecommendations(
        'script-tmdbhelper-recommendations.xml', ADDONPATH, 'default', '1080i',
        recommendations=recommendations, tmdb_type=tmdb_type, **kwargs)
    ui.doModal()
    del ui
