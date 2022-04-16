# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
if __name__ == '__main__':
    import sys
    from resources.lib.script.method import manage_artwork
    from json import loads
    manage_artwork(**loads(sys.listitem.getProperty('tmdbhelper.context.artwork')))
