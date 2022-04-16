# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
if __name__ == '__main__':
    import sys
    from json import loads
    from resources.lib.script.method import sort_list
    sort_list(**loads(sys.listitem.getProperty('tmdbhelper.context.sorting')))
