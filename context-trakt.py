# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
if __name__ == '__main__':
    import sys
    from resources.lib.script.sync import sync_trakt_item
    from json import loads
    sync_trakt_item(**loads(sys.listitem.getProperty('tmdbhelper.context.trakt')))
