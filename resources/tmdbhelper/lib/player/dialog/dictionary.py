import contextlib
from json import dumps
from urllib.parse import quote_plus, quote
from jurialmunkey.parser import try_int
from jurialmunkey.ftools import cached_property


class PlayerDictionaryDict(dict):

    tmdb_type = ''

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

    def __init__(self, tmdb_id, details, **kwargs):
        self.tmdb_id = tmdb_id
        self.details = details

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

    def string_format_map(self, fmt):
        return fmt.format_map(self)

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

    def initialise_standard_keys(self):
        for k in self.routes.keys():
            self[k]

    @cached_property
    def routes(self):
        return self.get_routes()

    def get_routes(self):
        return {
            'id': lambda **kwargs: self.tmdb_id,
            'tmdb': lambda **kwargs: self.tmdb_id,
            'title': self.get_title,
            'clearname': self.get_title,
            'name': self.get_name,
            'year': lambda **kwargs: self.details.infolabels.get('year'),
            'premiered': lambda **kwargs: self.details.infolabels.get('premiered'),
            'firstaired': lambda **kwargs: self.details.infolabels.get('premiered'),
            'released': lambda **kwargs: self.details.infolabels.get('premiered'),
            'plot': self.get_plot,
            'cast': self.get_cast,
            'actors': self.get_cast,
            'thumbnail': lambda **kwargs: self.details.art.get('thumb'),
            'poster': lambda **kwargs: self.details.art.get('poster'),
            'fanart': lambda **kwargs: self.details.art.get('fanart'),
            'now': self.get_now,
        }

    def get_name(self, language=None, **kwargs):
        name = self[f'{language}_title' if language else 'title']
        return name

    def get_title(self, language=None, **kwargs):
        title = self.details.infoproperties.get(f'{language}_title') if language else self.details.infolabels.get('title')
        return (title or self['title']) if language else title

    def get_plot(self, language=None, **kwargs):
        plot = self.details.infoproperties.get(f'{language}_plot') if language else self.details.infolabels.get('plot')
        return (plot or self['plot']) if language else None

    def get_cast(self, **kwargs):
        return " / ".join([i.get('name') for i in self.details.cast if i.get('name')])

    def get_now(self, **kwargs):
        from tmdbhelper.lib.addon.tmdate import get_datetime_now
        return get_datetime_now().strftime('%Y%m%d%H%M%S%f')


class PlayerDictionaryDictMovie(PlayerDictionaryDict):

    tmdb_type = 'movie'

    def get_routes(self):
        routes = super().get_routes()
        routes.update({
            'imdb': lambda **kwargs: self.details.unique_ids.get('imdb'),
            'tvdb': lambda **kwargs: self.details.unique_ids.get('tvdb'),
            'trakt': lambda **kwargs: self.details.unique_ids.get('trakt'),
            'slug': lambda **kwargs: self.details.unique_ids.get('slug'),
            'originaltitle': lambda **kwargs: self.details.infolabels.get('originaltitle'),
        })
        return routes

    def get_title(self, language=None, **kwargs):
        title = self.details.infoproperties.get(f'{language}_title') if language else self.details.infolabels.get('title')
        title = title or self.details.infolabels.get('originaltitle')
        return (title or self['title']) if language else title

    def get_name(self, language=None, **kwargs):
        name = self[f'{language}_title' if language else 'title']
        name = f'{name} ({self["year"]})'
        return name


class PlayerDictionaryDictEpisode(PlayerDictionaryDict):
    tmdb_type = 'tv'

    def __init__(self, tmdb_id, details, season=None, episode=None, **kwargs):
        super().__init__(tmdb_id, details)
        self.season = season
        self.episode = episode

    def get_routes(self):
        routes = super().get_routes()
        routes.update({
            'id': lambda **kwargs: self.details.unique_ids.get('tvdb'),
            'imdb': lambda **kwargs: self.details.unique_ids.get('tvshow.imdb'),
            'tvdb': lambda **kwargs: self.details.unique_ids.get('tvshow.tvdb'),
            'trakt': lambda **kwargs: self.details.unique_ids.get('tvshow.trakt'),
            'slug': lambda **kwargs: self.details.unique_ids.get('tvshow.slug'),
            'epid': lambda **kwargs: self.details.unique_ids.get('tvdb'),
            'eptvdb': lambda **kwargs: self.details.unique_ids.get('tvdb'),
            'eptmdb': lambda **kwargs: self.details.unique_ids.get('tmdb'),
            'epimdb': lambda **kwargs: self.details.unique_ids.get('imdb'),
            'eptrakt': lambda **kwargs: self.details.unique_ids.get('trakt'),
            'epslug': lambda **kwargs: self.details.unique_ids.get('slug'),
            'originaltitle': lambda **kwargs: self.details.infoproperties.get('tvshow.originaltitle'),
            'season': lambda **kwargs: self.season,
            'episode': lambda **kwargs: self.episode,
            'showpremiered': lambda **kwargs: self.details.infoproperties.get('tvshow.premiered'),
            'showyear': lambda **kwargs: self.details.infoproperties.get('tvshow.year'),
            'showname': self.get_tvshowtitle,
            'clearname': self.get_tvshowtitle,
            'tvshowtitle': self.get_tvshowtitle,
        })
        return routes

    def get_title(self, language=None, **kwargs):
        title = self.details.infoproperties.get(f'{language}_title') if language else self.details.infolabels.get('title')
        title = title or self.details.infolabels.get('originaltitle')
        return (title or self['title']) if language else title

    def get_tvshowtitle(self, language=None, **kwargs):
        tvshowtitle = self.details.infoproperties.get(f'{language}_tvshowtitle') if language else self.details.infolabels.get('tvshowtitle')
        tvshowtitle = tvshowtitle or self.details.infoproperties.get('tvshow.originaltitle')
        return (tvshowtitle or self['tvshowtitle']) if language else tvshowtitle

    def get_name(self, language=None, **kwargs):
        name = self[f'{language}_tvshowtitle' if language else 'tvshowtitle']
        name = f'{name} S{try_int(self["season"]):02d}E{try_int(self["episode"]):02d}'
        return name


def PlayerDictionary(tmdb_type, tmdb_id, season=None, episode=None, details=None):
    itemdict = (
        PlayerDictionaryDictMovie
        if tmdb_type != 'tv' or season is None or episode is None else
        PlayerDictionaryDictEpisode
    )
    itemdict = itemdict(tmdb_id, details, season=season, episode=episode)
    itemdict.initialise_standard_keys()
    return itemdict
