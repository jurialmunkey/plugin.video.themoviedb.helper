from tmdbhelper.lib.addon.plugin import get_localized, get_condvisibility, executebuiltin, ADDONPATH
from jurialmunkey.ftools import cached_property
from collections import namedtuple
from xbmcgui import Dialog, WindowXMLDialog, ListItem, INPUT_NUMERIC


ItemTuple = namedtuple("ItemTuple", "label value")


class TraktDiscoverMenu:
    def __init__(self, main):
        self.main = main

    label_affix = None
    paramstring = None
    label = None

    @cached_property
    def listitem(self):
        return ListItem(label=self.listitem_label)

    @cached_property
    def label_prefix(self):
        label_prefix = get_localized(self.label_prefix_localized)
        label_prefix = f'{label_prefix} ({self.label_affix})' if self.label_affix else label_prefix
        return label_prefix

    @property
    def listitem_label(self):
        return f'{self.label_prefix}: {self.label}' if self.label else self.label_prefix


class TraktDiscoverList(TraktDiscoverMenu):
    idx = 0
    key = 'info'
    label_prefix_localized = 535

    @property
    def route(self):
        if self.idx is None:
            return
        return self.routes[self.idx]

    @property
    def label(self):
        if not self.route:
            return
        return self.route.label

    @property
    def value(self):
        if not self.route:
            return
        return self.route.value

    @property
    def paramstring(self):
        if not self.value:
            return
        return f'{self.key}={self.value}'

    @cached_property
    def routes(self):
        return (
            ItemTuple(get_localized(32204), 'trakt_trending'),
            ItemTuple(get_localized(32175), 'trakt_popular'),
            ItemTuple(get_localized(32205), 'trakt_mostplayed'),
            ItemTuple(get_localized(32414), 'trakt_mostviewers'),
            ItemTuple(get_localized(32206), 'trakt_anticipated'),
        )

    @property
    def dialog_select(self):
        return Dialog().select

    @property
    def preselect(self):
        return self.idx or -1

    def menu(self):
        x = self.dialog_select(self.listitem_label, [i.label for i in self.routes], preselect=self.preselect)
        self.idx = x if x != -1 else self.idx
        self.listitem.setLabel(self.listitem_label)


class TraktDiscoverType(TraktDiscoverList):
    key = 'tmdb_type'
    label_prefix_localized = 467

    @cached_property
    def routes(self):
        return (
            ItemTuple(get_localized(342), 'movie'),
            ItemTuple(get_localized(20343), 'tv'),
        )


class TraktDiscoverGenres(TraktDiscoverList):
    idx = None
    key = 'genres'
    label_prefix_localized = 135

    @property
    def routes_items(self):
        if self.main.routes_dict['type'].value == 'movie':
            return self.routes_items_movies
        return self.routes_items_shows

    @cached_property
    def routes_items_movies(self):
        return self.main.trakt_api.get_response_json('genres/movies')

    @cached_property
    def routes_items_shows(self):
        return self.main.trakt_api.get_response_json('genres/shows')

    @cached_property
    def routes(self):
        return tuple((ItemTuple(i['name'], i['slug']) for i in self.routes_items if i))

    @property
    def dialog_select(self):
        return Dialog().multiselect

    @property
    def route(self):
        if not self.idx:
            return
        return [self.routes[x] for x in self.idx]

    @property
    def label(self):
        if not self.route:
            return
        return ' / '.join((i.label for i in self.route))

    @property
    def value(self):
        if not self.route:
            return
        return '%2C'.join((i.value for i in self.route))

    @property
    def preselect(self):
        return self.idx or []


class TraktDiscoverCertifications(TraktDiscoverGenres):
    idx = None
    key = 'certifications'
    label_prefix_localized = 32486

    @cached_property
    def routes_items_movies(self):
        try:
            return self.main.trakt_api.get_response_json('certifications/movies')['us']
        except (KeyError, TypeError):
            return []

    @cached_property
    def routes_items_shows(self):
        try:
            return self.main.trakt_api.get_response_json('certifications/shows')['us']
        except (KeyError, TypeError):
            return []


class TraktDiscoverYears(TraktDiscoverMenu):
    key = 'years'
    label_prefix_localized = 652
    value_a = None
    value_z = None

    @property
    def label(self):
        if not self.value_a:
            return
        if not self.value_z:
            return f'{self.value_a}'
        if self.value_a == self.value_z:
            return f'{self.value_a}'
        return f'{self.value_a}-{self.value_z}'

    @property
    def value(self):
        return self.label

    @property
    def paramstring(self):
        if not self.value:
            return
        return f'{self.key}={self.value}'

    @property
    def input_label(self):
        return get_localized(32279)

    def menu(self):
        self.value_a = Dialog().input(f'{self.input_label} [>>]', type=INPUT_NUMERIC, defaultt=f'{self.value_a}' if self.value_a else '')
        self.value_z = Dialog().input(f'{self.input_label} [<<]', type=INPUT_NUMERIC, defaultt=f'{self.value_z}' if self.value_z else '')
        self.listitem.setLabel(self.listitem_label)


class TraktDiscoverRuntimes(TraktDiscoverYears):
    key = 'runtimes'
    label_prefix_localized = 2050

    @property
    def input_label(self):
        return get_localized(12391)


class TraktDiscoverRatings(TraktDiscoverYears):
    key = 'ratings'
    label_prefix_localized = 32028

    @property
    def input_label(self):
        return f'{get_localized(32028)} (%/100)'


class TraktDiscoverVotes(TraktDiscoverYears):
    key = 'votes'
    label_prefix_localized = 205

    @property
    def input_label(self):
        return get_localized(205)

    def menu(self):
        self.value_a = Dialog().input(f'{self.input_label}', type=INPUT_NUMERIC, defaultt=f'{self.value_a}' if self.value_a else '')
        self.listitem.setLabel(self.listitem_label)


class TraktDiscoverTMDbRatings(TraktDiscoverRatings):
    key = 'tmdb_ratings'
    label_affix = 'TMDb'

    def menu(self):
        super().menu()
        if self.value_a:
            self.value_a = f'{int(self.value_a) / 10:.1f}'
        if self.value_z:
            self.value_z = f'{int(self.value_z) / 10:.1f}'


class TraktDiscoverTMDbVotes(TraktDiscoverVotes):
    key = 'tmdb_votes'
    label_affix = 'TMDb'


class TraktDiscoverIMDbRatings(TraktDiscoverTMDbRatings):
    key = 'imdb_ratings'
    label_affix = 'IMDb'


class TraktDiscoverIMDbVotes(TraktDiscoverVotes):
    key = 'imdb_votes'
    label_affix = 'IMDb'


class TraktDiscoverRTRatings(TraktDiscoverRatings):
    key = 'rt_meters'
    label_affix = 'Rotten Tomatoes'


class TraktDiscoverRTUserRatings(TraktDiscoverRatings):
    key = 'rt_user_meters'
    label_affix = 'Rotten Tomatoes Users'


class TraktDiscoverMetaRatings(TraktDiscoverTMDbRatings):
    key = 'metascores'
    label_affix = 'Metacritic'


class TraktDiscoverBrowse(TraktDiscoverMenu):

    label_prefix_localized = 1024

    @property
    def command(self):
        if get_condvisibility('Window.IsVisible(MyVideoNav.xml)'):
            return f'Container.Update({self.main.url})'
        return f'ActivateWindow(videos,{self.main.url},return)'

    def menu(self):
        self.main.close()
        executebuiltin(self.command)


class TraktDiscoverReset(TraktDiscoverMenu):

    label_prefix_localized = 13007

    def menu(self):
        self.main.routes_dict = self.main.get_routes_dict()
        self.main.build_menu()


class TraktDiscover(WindowXMLDialog):

    label = 'Trakt Discover'
    ACTION_SELECT = (7, 100, )
    ACTION_CLOSEWINDOW = (9, 10, 92, 216, 247, 257, 275, 61467, 61448,)

    @property
    def url(self):
        url = '&'.join((i.paramstring for i in self.routes if i.paramstring))
        url = 'plugin://plugin.video.themoviedb.helper/?' + url
        return url

    @cached_property
    def routes_dict(self):
        return self.get_routes_dict()

    def get_routes_dict(self):
        return {
            'browse': TraktDiscoverBrowse(self),
            'list': TraktDiscoverList(self),
            'type': TraktDiscoverType(self),
            'years': TraktDiscoverYears(self),
            'genres': TraktDiscoverGenres(self),
            'certifications': TraktDiscoverCertifications(self),
            'runtimes': TraktDiscoverRuntimes(self),
            'ratings': TraktDiscoverRatings(self),
            'votes': TraktDiscoverVotes(self),
            'tmdb_ratings': TraktDiscoverTMDbRatings(self),
            'tmdb_votes': TraktDiscoverTMDbVotes(self),
            'imdb_ratings': TraktDiscoverIMDbRatings(self),
            'imdb_votes': TraktDiscoverIMDbVotes(self),
            'rt_meters': TraktDiscoverRTRatings(self),
            'rt_user_meters': TraktDiscoverRTUserRatings(self),
            'metascores': TraktDiscoverMetaRatings(self),
            'reset': TraktDiscoverReset(self),
        }

    @property
    def routes(self):
        return tuple(self.routes_dict.values())

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    def onAction(self, action):
        action_id = action.getId()
        if action_id in self.ACTION_CLOSEWINDOW:
            return self.close()
        if action_id in self.ACTION_SELECT:
            return self.click()

    def click(self):
        focus_id = self.getFocusId()
        if focus_id == 3:
            return self.on_action()
        if focus_id == 7:
            return self.close()
        if focus_id == 8:
            return self.routes_dict['reset'].menu()
        if focus_id == 5:
            return self.routes_dict['browse'].menu()

    def on_action(self):
        x = self.list_control.getSelectedPosition()
        self.routes[x].menu()

    @property
    def list_control(self):
        return self.getControl(3)

    def onInit(self):
        self.getControl(1).setLabel(self.label)
        self.getControl(5).setLabel(get_localized(1024))
        self.getControl(6).setVisible(False)
        self.getControl(7).setLabel(get_localized(15067))
        self.getControl(8).setLabel(get_localized(13007))
        self.build_menu()

    def build_menu(self):
        self.list_control.reset()
        self.list_control.addItems([i.listitem for i in self.routes])
        self.setFocus(self.list_control)


def trakt_discover():
    trakt_discover = TraktDiscover('DialogSelect.xml', ADDONPATH)
    trakt_discover.doModal()
