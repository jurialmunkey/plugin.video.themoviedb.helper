# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from resources.lib.addon.parser import encode_url
from resources.lib.addon.plugin import executebuiltin, format_folderpath
from resources.lib.api.trakt.api import get_sort_methods
from xbmcgui import Dialog


def sort_list(**kwargs):
    sort_methods = get_sort_methods() if kwargs['info'] == 'trakt_userlist' else get_sort_methods(True)
    x = Dialog().contextmenu([i['name'] for i in sort_methods])
    if x == -1:
        return
    for k, v in sort_methods[x]['params'].items():
        kwargs[k] = v
    executebuiltin(format_folderpath(encode_url(**kwargs)))
