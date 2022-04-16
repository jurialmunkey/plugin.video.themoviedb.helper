# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
if __name__ == '__main__':
    import sys
    from resources.lib.script.method import refresh_details
    from json import loads
    refresh_details(**loads(sys.listitem.getProperty('tmdbhelper.context.refresh')))
