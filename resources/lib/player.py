import xbmc
from resources.lib.plugin import Plugin
from resources.lib.kodilibrary import KodiLibrary


class Player(Plugin):
    def play(self, itemtype, tmdb_id, season=None, episode=None):
        tmdbtype = 'tv' if itemtype == 'episode' else 'movie'
        item = self.tmdb.get_detailed_item(tmdbtype, tmdb_id)
        if not item:
            return

        if itemtype == 'movie':
            item = self.get_db_info(item, 'file', dbtype='movie')
        if itemtype == 'episode':
            item = self.get_db_info(item, 'dbid', dbtype='tv')
            item['file'] = KodiLibrary(dbtype='episode', tvshowid=item.get('dbid')).get_info(
                'file', season=season, episode=episode)

        if item.get('file'):
            xbmc.executebuiltin('PlayMedia({0})'.format(item.get('file')))
            return

        # TODO: Add Player for Non-DBID items
