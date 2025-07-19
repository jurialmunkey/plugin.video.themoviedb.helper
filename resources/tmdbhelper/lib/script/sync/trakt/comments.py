from tmdbhelper.lib.script.sync.trakt.item import ItemSync
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.addon.dialog import busy_decorator
from jurialmunkey.ftools import cached_property
from xbmcgui import Dialog


class ItemComments(ItemSync):
    localized_name = 32304
    preconfigured = True

    def get_trakt_type(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        return 'show'

    def view_comment(self, comment):
        info = comment.get('comment')
        name = comment.get('user', {}).get('name')
        rate = comment.get('user_stats', {}).get('rating')
        info = f'{info}\n\n{get_localized(563)} {rate}/10' if rate else f'{info}'
        Dialog().textviewer(name, info)

    def select_comment(self):
        """ Get a comment from a list of comments """
        if not self.itemlist:
            Dialog().ok(get_localized(32305), get_localized(32306))
            return
        x = Dialog().select(get_localized(32305), self.itemlist)
        if x != -1:
            self.view_comment(self.comments[x])
            return self.select_comment()

    @cached_property
    def comments(self):
        return self.trakt_api.get_response_json(f'{self.trakt_type}s', self.trakt_slug, 'comments', limit=50) or []

    @cached_property
    def itemlist(self):
        return self.get_itemlist()

    @busy_decorator
    def get_itemlist(self):
        return [i.get('comment', '').replace('\n', ' ') for i in self.comments]

    def sync(self):
        self.select_comment()
