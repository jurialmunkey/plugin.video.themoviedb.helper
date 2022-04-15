# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
if __name__ == '__main__':
    import sys
    from resources.lib.update.library import add_to_library
    from json import loads
    add_to_library(**loads(sys.listitem.getProperty('tmdbhelper.context.addlibrary')))
