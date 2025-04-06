from tmdbhelper.lib.script.sync.item import ItemSync
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.addon.dialog import BusyDialog
from xbmcgui import Dialog


class ItemComments(ItemSync):
    localized_name = 32304
    preconfigured = True

    def get_trakt_type(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        return 'show'

    def select_comment(self, itemlist, comments):
        """ Get a comment from a list of comments """
        if not itemlist:
            Dialog().ok(get_localized(32305), get_localized(32306))
            return -1
        x = Dialog().select(get_localized(32305), itemlist)
        if x == -1:
            return -1
        info = comments[x].get('comment')
        name = comments[x].get('user', {}).get('name')
        rate = comments[x].get('user_stats', {}).get('rating')
        info = f'{info}\n\n{get_localized(563)} {rate}/10' if rate else f'{info}'
        Dialog().textviewer(name, info)
        return self.select_comment(itemlist, comments)

    def sync(self):
        with BusyDialog():
            comments = self.trakt_api.get_response_json(f'{self.trakt_type}s', self.trakt_id, 'comments', limit=50) or []
            itemlist = [i.get('comment', '').replace('\n', ' ') for i in comments]
        self.select_comment(itemlist, comments)
