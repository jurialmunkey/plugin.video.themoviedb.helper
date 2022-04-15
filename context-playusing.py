# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
if __name__ == '__main__':
    import sys
    import xbmc
    xbmc.executebuiltin(f'RunPlugin({sys.listitem.getProperty("tmdbhelper.context.playusing")})')
