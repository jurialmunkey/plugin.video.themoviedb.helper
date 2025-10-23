import contextlib
from json import dumps
from urllib.parse import quote_plus, quote
from jurialmunkey.parser import try_int
from jurialmunkey.ftools import cached_property


class PlayerNextEpisodes:
    def __init__(self, tmdb_id, season, episode, player=None):
        self.tmdb_id = try_int(tmdb_id)
        self.season = try_int(season)
        self.episode = try_int(episode)
        self.player = player

    @cached_property
    def lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        lidc = ListItemDetails()
        lidc.cache_refresh = 'basic'
        lidc.extendedinfo = False
        return lidc

    @cached_property
    def parent_data(self):
        from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
        sync = BaseItemFactory('tvshow')
        sync.tmdb_id = self.tmdb_id
        return sync.data

    @cached_property
    def all_episodes(self):
        from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
        sync = BaseViewFactory('flatseasons', 'tv', self.tmdb_id)
        return sync.data

    @cached_property
    def next_episodes(self):
        return [i for i in self.all_episodes if self.is_future_episode(i)]

    @cached_property
    def finalised_items(self):
        return [self.finalise_item(li) for li in self.configured_items if li]

    @cached_property
    def configured_items(self):
        return self.lidc.configure_listitems_threaded(self.next_episodes)

    def is_future_episode(self, i):
        s_number = try_int(i['infolabels'].get('season', -1))
        e_number = try_int(i['infolabels'].get('episode', -1))
        if s_number < self.season:
            return False
        if s_number > self.season:
            return True
        if e_number < self.episode:
            return False
        return True

    def finalise_item(self, li):
        li.finalise()
        if not self.player:
            return li
        li.params['player'] = self.player
        li.params['mode'] = 'play'
        return li

    @cached_property
    def listitems(self):
        if not self.items:
            return
        return [li.get_listitem() for li in self.items if li]

    @cached_property
    def items(self):
        if not self.parent_data:
            return
        if not self.all_episodes:
            return
        if not self.next_episodes:
            return
        if not self.configured_items:
            return
        return self.finalised_items


class PlayerDetails:

    external_id_types = ('tmdb', 'tvdb', 'imdb', 'slug', 'trakt')

    def __init__(self, tmdb_type, tmdb_id, season=None, episode=None, translation=False):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        self.translation = translation

    @cached_property
    def lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        lidc = ListItemDetails()
        lidc.cache_refresh = 'langs' if self.translation else None
        lidc.extendedinfo = True
        return lidc

    @cached_property
    def details(self):
        details = self.get_details()
        details.set_details(details=self.external_ids, reverse=True)
        return details

    def get_details(self, language=None):
        from tmdbhelper.lib.items.listitem import ListItem
        details = self.lidc.get_item(self.tmdb_type, self.tmdb_id, self.season, self.episode)
        return ListItem(**details) if details else None

    @cached_property
    def find_queries_db(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    @cached_property
    def trakt_type(self):
        return 'movie' if self.tmdb_type == 'movie' else 'show'

    @cached_property
    def trakt_slug(self):
        return self.find_queries_db.get_trakt_id(
            id_type='tmdb',
            id_value=self.tmdb_id,
            item_type=self.trakt_type,
            output_type='slug'
        )

    @cached_property
    def trakt_details(self):
        if not self.trakt_slug:
            return
        return self.trakt_api.get_response_json(f'{self.trakt_type}s', self.trakt_slug)

    @cached_property
    def trakt_details_ids(self):
        if not self.trakt_details:
            return {}
        return self.trakt_details.get('ids') or {}

    @cached_property
    def trakt_episode_details(self):
        if not self.trakt_slug:
            return
        if self.season is None:
            return
        if self.episode is None:
            return
        return self.trakt_api.get_response_json(
            'shows', self.trakt_slug,
            'seasons', self.season,
            'episodes', self.episode
        )

    @cached_property
    def trakt_episode_details_ids(self):
        if not self.trakt_episode_details:
            return {}
        return self.trakt_episode_details.get('ids') or {}

    @property
    def trakt_uid_generator(self):
        return ((i, self.trakt_details_ids.get(i)) for i in self.external_id_types)

    @cached_property
    def trakt_movie_uids(self):
        trakt_movie_uids = {k: v for k, v in self.trakt_uid_generator if k and v}
        trakt_movie_uids['tmdb'] = self.tmdb_id
        return trakt_movie_uids

    @cached_property
    def trakt_tvshow_uids(self):
        trakt_tvshow_uids = {f'tvshow.{k}': v for k, v in self.trakt_uid_generator if k and v}
        trakt_tvshow_uids['tvshow.tmdb'] = self.tmdb_id
        return trakt_tvshow_uids

    @property
    def trakt_episode_uid_generator(self):
        return ((i, self.trakt_episode_details_ids.get(i)) for i in self.external_id_types)

    @cached_property
    def trakt_episode_uids(self):
        trakt_episode_uids = self.trakt_tvshow_uids
        trakt_episode_uids.update({k: v for k, v in self.trakt_episode_uid_generator if k and v})
        trakt_episode_uids['tmdb'] = self.tmdb_id
        return trakt_episode_uids

    @cached_property
    def trakt_uids(self):
        if self.trakt_type == 'movie':
            return self.trakt_movie_uids
        return self.trakt_episode_uids

    @cached_property
    def external_ids(self):
        if not self.trakt_details_ids:
            return {}
        return {'unique_ids': self.trakt_uids}


def get_next_episodes(tmdb_id, season, episode, player=None):
    return PlayerNextEpisodes(tmdb_id, season, episode, player).listitems


class PlayerDetailedItemDictMovie(dict):

    tmdb_type = 'movie'

    def __init__(self, tmdb_id, details, **kwargs):
        self.tmdb_id = tmdb_id
        self.details = details

    encoding_methods = {
        '_+': lambda v: v.replace(',', '').replace(' ', '+'),
        '_-': lambda v: v.replace(',', '').replace(' ', '-'),
        '_escaped': lambda v: quote(quote(v)),
        '_escaped+': lambda v: quote(quote_plus(v)),
        '_url': lambda v: quote(v),
        '_url+': lambda v: quote_plus(v),
        '_meta': lambda v: dumps(v).replace(',', ''),
        '_meta_+': lambda v: dumps(v).replace(',', '').replace(' ', '+'),
        '_meta_-': lambda v: dumps(v).replace(',', '').replace(' ', '-'),
        '_meta_escaped': lambda v: quote(quote(dumps(v))),
        '_meta_escaped+': lambda v: quote(quote_plus(dumps(v))),
        '_meta_url': lambda v: quote(dumps(v)),
        '_meta_url+': lambda v: quote_plus(dumps(v)),
    }

    @cached_property
    def encoding_affixes(self):
        return tuple(self.encoding_methods.keys())

    def get_sanitised(self, value, method=None):
        if not isinstance(value, str):
            return value
        try:
            return self.encoding_methods[method](value)
        except KeyError:
            return value.replace(',', '')

    @cached_property
    def routes(self):
        return self.get_routes()

    def get_routes(self):
        return {
            'id': lambda **kwargs: self.tmdb_id,
            'tmdb': lambda **kwargs: self.tmdb_id,
            'imdb': lambda **kwargs: self.details.unique_ids.get('imdb'),
            'tvdb': lambda **kwargs: self.details.unique_ids.get('tvdb'),
            'trakt': lambda **kwargs: self.details.unique_ids.get('trakt'),
            'slug': lambda **kwargs: self.details.unique_ids.get('slug'),
            'originaltitle': lambda **kwargs: self.details.infolabels.get('originaltitle'),
            'title': self.get_title,
            'clearname': self.get_title,
            'year': lambda **kwargs: self.details.infolabels.get('year'),
            'name': self.get_name,
            'premiered': lambda **kwargs: self.details.infolabels.get('premiered'),
            'firstaired': lambda **kwargs: self.details.infolabels.get('premiered'),
            'released': lambda **kwargs: self.details.infolabels.get('premiered'),
            'plot': lambda **kwargs: self.details.infolabels.get('plot'),
            'cast': self.get_cast,
            'actors': self.get_cast,
            'thumbnail': lambda **kwargs: self.details.art.get('thumb'),
            'poster': lambda **kwargs: self.details.art.get('poster'),
            'fanart': lambda **kwargs: self.details.art.get('fanart'),
            'now': self.get_now,
        }

    def get_name(self, language=None, **kwargs):
        name = self[f'{language}_title' if language else 'title']
        name = f'{name} ({self["year"]})'
        return name

    def get_title(self, language=None, **kwargs):
        title = self.details.infoproperties.get(f'{language}_title') if language else self.details.infolabels.get('title')
        title = title or self.details.infolabels.get('originaltitle')
        return (title or self['title']) if language else title

    def get_tvshowtitle(self, language=None, **kwargs):
        tvshowtitle = self.details.infoproperties.get(f'{language}_tvshowtitle') if language else self.details.infolabels.get('tvshowtitle')
        tvshowtitle = tvshowtitle or self.details.infoproperties.get('tvshow.originaltitle')
        return (tvshowtitle or self['tvshowtitle']) if language else tvshowtitle

    def get_plot(self, language=None, **kwargs):
        plot = self.details.infoproperties.get(f'{language}_plot') if language else self.details.infolabels.get('plot')
        plot = plot or self['plot'] if language else None
        return plot

    def get_cast(self, **kwargs):
        return " / ".join([i.get('name') for i in self.details.cast if i.get('name')])

    def get_now(self, **kwargs):
        from tmdbhelper.lib.addon.tmdate import get_datetime_now
        return get_datetime_now().strftime('%Y%m%d%H%M%S%f')

    def initialise_standard_keys(self):
        for k in self.routes.keys():
            self[k]

    def __missing__(self, key):

        # Basic routes for details
        with contextlib.suppress(KeyError, AttributeError):
            self[key] = self.routes[key]()
            self[key] = self.get_sanitised(self[key])
            return self[key]

        # Translation routes
        with contextlib.suppress(KeyError, AttributeError, ValueError):
            language, route_key = key.split('_', 1)
            self[key] = self.routes[route_key](language=language)
            return self[key]

        # Encoding affixes
        for method in self.encoding_affixes:
            if not key.endswith(method):
                continue
            self[key] = self[key[:-len(method)]]
            self[key] = self.get_sanitised(self[key], method)
            return self[key]

        return '_'


class PlayerDetailedItemDictEpisode(PlayerDetailedItemDictMovie):
    tmdb_type = 'tv'

    def __init__(self, tmdb_id, details, season=None, episode=None, **kwargs):
        super().__init__(tmdb_id, details)
        self.season = season
        self.episode = episode

    def get_routes(self):
        routes = super().get_routes()
        routes.update({
            'season': lambda **kwargs: self.season,
            'episode': lambda **kwargs: self.episode,
            'originaltitle': lambda **kwargs: self.details.infoproperties.get('tvshow.originaltitle'),
            'showpremiered': lambda **kwargs: self.details.infoproperties.get('tvshow.premiered'),
            'showyear': lambda **kwargs: self.details.infoproperties.get('tvshow.year'),
            'showname': self.get_tvshowtitle,
            'clearname': self.get_tvshowtitle,
            'tvshowtitle': self.get_tvshowtitle,
            'id': lambda **kwargs: self.details.unique_ids.get('tvdb'),
            'epid': lambda **kwargs: self.details.unique_ids.get('tvdb'),
            'eptvdb': lambda **kwargs: self.details.unique_ids.get('tvdb'),
            'eptmdb': lambda **kwargs: self.details.unique_ids.get('tmdb'),
            'epimdb': lambda **kwargs: self.details.unique_ids.get('imdb'),
            'eptrakt': lambda **kwargs: self.details.unique_ids.get('trakt'),
            'epslug': lambda **kwargs: self.details.unique_ids.get('slug'),
            'tmdb': lambda **kwargs: self.details.unique_ids.get('tvshow.tmdb'),
            'imdb': lambda **kwargs: self.details.unique_ids.get('tvshow.imdb'),
            'tvdb': lambda **kwargs: self.details.unique_ids.get('tvshow.tvdb'),
            'trakt': lambda **kwargs: self.details.unique_ids.get('tvshow.trakt'),
            'slug': lambda **kwargs: self.details.unique_ids.get('tvshow.slug'),

        })
        return routes

    def get_name(self, language=None, **kwargs):
        name = self[f'{language}_tvshowtitle' if language else 'tvshowtitle']
        name = f'{name} S{try_int(self["season"]):02d}E{try_int(self["episode"]):02d}'
        return name


def PlayerDetailedItemDict(tmdb_type, tmdb_id, season=None, episode=None, details=None):
    itemdict = (
        PlayerDetailedItemDictMovie
        if tmdb_type != 'tv' or season is None or episode is None else
        PlayerDetailedItemDictEpisode
    )
    itemdict = itemdict(tmdb_id, details, season=season, episode=episode)
    itemdict.initialise_standard_keys()
    return itemdict
