# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
if __name__ == '__main__':
    import sys
    from resources.lib.script.method import related_lists
    from json import loads
    related_lists(**loads(sys.listitem.getProperty('tmdbhelper.context.related')))
