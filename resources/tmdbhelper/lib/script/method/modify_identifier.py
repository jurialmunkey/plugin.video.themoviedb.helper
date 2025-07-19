# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import xbmcgui
from tmdbhelper.lib.addon.plugin import get_localized
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.monitor.listitemtools import ListItemMonitorFunctions
from tmdbhelper.lib.query.database.database import FindQueriesDatabase
from tmdbhelper.lib.script.method.kodi_utils import service_refresh


class ModifyIdentifier:

    tmdb_type_allowlist = ('movie', 'tv', 'person', 'reset')

    def run(self, tmdb_id=None, tmdb_type=None):
        if tmdb_type in self.tmdb_type_allowlist:
            self.tmdb_type = tmdb_type
        if self.tmdb_type == 'reset':
            return self.reset_details()
        if tmdb_id is not None:
            self.tmdb_id = tmdb_id
        if not self.tmdb_type or not self.tmdb_id:
            return
        self.set_identifier_details(
            self.identifier_id,
            self.tmdb_id,
            self.tmdb_type,
        )
        self.notification(f'TMDb ID {get_localized(32098)}')

    def notification(self, header):
        xbmcgui.Dialog().ok(
            header,
            f'{self.tmdb_type} {self.tmdb_id}\n\nMonitor ID\n{self.identifier_id}'
        )
        service_refresh()

    def reset_details(self):
        self.del_identifier_details(self.identifier_id)
        self.listitem_monitor_item = self.get_listitem_monitor_item()  # Reset monitor item
        self.tmdb_id = self.listitem_monitor_item.tmdb_id
        self.tmdb_type = self.listitem_monitor_item.tmdb_type
        self.notification(f'TMDb ID {get_localized(13007)}')

    @cached_property
    def listitem_monitor_functions(self):
        return ListItemMonitorFunctions()

    def set_identifier_details(self, *args, **kwargs):
        return self.listitem_monitor_functions.set_identifier_details(*args, **kwargs)

    def del_identifier_details(self, *args, **kwargs):
        return self.listitem_monitor_functions.del_identifier_details(*args, **kwargs)

    @cached_property
    def listitem_monitor_item(self):
        return self.get_listitem_monitor_item()

    def get_listitem_monitor_item(self):
        self.listitem_monitor_functions.setup_current_container()
        self.listitem_monitor_functions.setup_current_item()
        return self.listitem_monitor_functions._item

    @cached_property
    def identifier_id(self):
        return self.listitem_monitor_item.identifier_id

    @cached_property
    def tmdb_type(self):
        return self.get_tmdb_type()

    def get_tmdb_type(self):
        try:
            i = self.tmdb_type_allowlist.index(self.listitem_monitor_item.tmdb_type)
        except ValueError:
            i = 3
        x = xbmcgui.Dialog().select(get_localized(32094), self.tmdb_type_allowlist, preselect=i)
        return self.tmdb_type_allowlist[x] if x != -1 else None

    @cached_property
    def tmdb_id(self):
        return self.get_tmdb_id()

    def get_lookup_tmdb_id(self):
        query = xbmcgui.Dialog().input(
            get_localized(32044),
            defaultt=f'{self.listitem_monitor_item.query or ""}'
        )
        if not query:
            return
        tmdb_id = FindQueriesDatabase().get_tmdb_id_from_query(
            self.tmdb_type,
            query,
            header=query,
            use_details=True
        )
        return tmdb_id

    def get_manual_tmdb_id(self):
        x = xbmcgui.Dialog().input(
            'TMDb ID',
            type=xbmcgui.INPUT_NUMERIC,
            defaultt=f'{self.listitem_monitor_item.tmdb_id or ""}'
        )
        return x if x and x != -1 else None

    def get_tmdb_id(self):
        x = xbmcgui.Dialog().yesnocustom(
            'TMDb ID',
            get_localized(32087),
            yeslabel=get_localized(137),
            nolabel=get_localized(413),
            customlabel=get_localized(222),
            defaultbutton=xbmcgui.DLG_YESNO_YES_BTN,
        )

        return (
            self.get_manual_tmdb_id()
            if x == 0 else
            self.get_lookup_tmdb_id()
            if x == 1 else
            None
        )


def modify_identifier(tmdb_id=None, tmdb_type=None, **kwargs):
    ModifyIdentifier().run(tmdb_id, tmdb_type)
