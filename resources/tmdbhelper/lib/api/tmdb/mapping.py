from jurialmunkey.parser import try_int, try_float, get_params, IterProps
from tmdbhelper.lib.api.mapping import UPDATE_BASEKEY, _ItemMapper, get_empty_item
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_mpaa_prefix, get_language, convert_type, get_localized
from tmdbhelper.lib.addon.consts import ITER_PROPS_MAX


class ItemMapperMethods:

    @cached_property
    def tmdb_imagepath(self):
        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
        return TMDbImagePath()

    @cached_property
    def iter_props(self):
        return IterProps(ITER_PROPS_MAX).iter_props

    """
    RUNTIME
    """

    @staticmethod
    def get_runtime(v, *args, **kwargs):
        if isinstance(v, list):
            v = v[0]
        return try_int(v) * 60

    """
    COLLECTION
    """

    def get_collection(self, v):
        infoproperties = {}
        infoproperties['set.tmdb_id'] = v.get('id')
        infoproperties['set.name'] = v.get('name')
        infoproperties['set.poster'] = self.tmdb_imagepath.get_imagepath_poster(v.get('poster_path'))
        infoproperties['set.fanart'] = self.tmdb_imagepath.get_imagepath_fanart(v.get('backdrop_path'))
        return infoproperties

    def get_collection_properties(self, v):
        ratings = []
        infoproperties = {}
        year_l, year_h, votes = 9999, 0, 0
        genres = set()
        for p, i in enumerate(v, start=1):
            genre = self.get_genres_by_id(i.get('genre_ids'))
            genres.update(genre)

            infoproperties[f'set.{p}.genre'] = ' / '.join(genre)
            infoproperties[f'set.{p}.title'] = i.get('title', '')
            infoproperties[f'set.{p}.tmdb_id'] = i.get('id', '')
            infoproperties[f'set.{p}.originaltitle'] = i.get('original_title', '')
            infoproperties[f'set.{p}.plot'] = i.get('overview', '')
            infoproperties[f'set.{p}.premiered'] = i.get('release_date', '')
            infoproperties[f'set.{p}.year'] = i.get('release_date', '')[:4]
            infoproperties[f'set.{p}.rating'] = f'{try_float(i.get("vote_average")):0,.1f}'
            infoproperties[f'set.{p}.votes'] = i.get('vote_count', '')
            infoproperties[f'set.{p}.poster'] = self.tmdb_imagepath.get_imagepath_poster(i.get('poster_path', ''))
            infoproperties[f'set.{p}.fanart'] = self.tmdb_imagepath.get_imagepath_fanart(i.get('backdrop_path', ''))

            year_l = min(try_int(i.get('release_date', '')[:4]), year_l)
            year_h = max(try_int(i.get('release_date', '')[:4]), year_h)
            if i.get('vote_average'):
                ratings.append(i['vote_average'])
            votes += try_int(i.get('vote_count', 0))
        if year_l == 9999:
            year_l = None
        if year_l:
            infoproperties['set.year.first'] = year_l
        if year_h:
            infoproperties['set.year.last'] = year_h
        if year_l and year_h:
            infoproperties['set.years'] = f'{year_l} - {year_h}'
        if len(ratings):
            infoproperties['set.rating'] = infoproperties['tmdb_rating'] = f'{sum(ratings) / len(ratings):0,.1f}'
        if votes:
            infoproperties['set.votes'] = infoproperties['tmdb_votes'] = f'{votes:0,.0f}'
        if genres:
            infoproperties['set.genres'] = ' / '.join(genres)
        infoproperties['set.numitems'] = p
        return infoproperties


class ItemMapper(_ItemMapper, ItemMapperMethods):
    def __init__(self, language=None, mpaa_prefix=None, genres=None):
        self.language = language or get_language()
        self.mpaa_prefix = mpaa_prefix or get_mpaa_prefix()
        self.iso_language = language[:2]
        self.iso_country = language[-2:]
        self.genres = genres or {}
        self.imagepath_quality = 'IMAGEPATH_ORIGINAL'
        self.blacklist = []
        """ Mapping dictionary
        keys:       list of tuples containing parent and child key to add value. [('parent', 'child')]
                    parent keys: art, unique_ids, infolabels, infoproperties, params
                    use UPDATE_BASEKEY for child key to update parent with a dict
        func:       function to call to manipulate values (omit to skip and pass value directly)
        (kw)args:   list/dict of args/kwargs to pass to func.
                    func is also always passed v as first argument
        type:       int, float, str - convert v to type using try_type(v, type)
        extend:     set True to add to existing list - leave blank to overwrite exiting list
        subkeys:    list of sub keys to get for v - i.e. v.get(subkeys[0], {}).get(subkeys[1]) etc.
                    note that getting subkeys sticks for entire loop so do other ops on base first if needed

        use standard_map for direct one-to-one mapping of v onto single property tuple
        """
        self.advanced_map = {
            'episodes': [{
                'keys': [('infolabels', 'episode')],
                'func': lambda v: f'{len(v)}'
            }],
            'poster_path': [{
                'keys': [('art', 'poster')],
                'func': self.tmdb_imagepath.get_imagepath_poster
            }],
            'profile_path': [{
                'keys': [('art', 'poster'), ('art', 'profile')],
                'func': self.tmdb_imagepath.get_imagepath_poster
            }],
            'file_path': [{
                'keys': [('art', 'poster'), ('art', 'file')],
                'func': self.tmdb_imagepath.get_imagepath_origin
            }],
            'still_path': [{
                'keys': [('art', 'thumb'), ('art', 'still')],
                'func': self.tmdb_imagepath.get_imagepath_thumbs
            }],
            'logo_path': [{
                'keys': [('art', 'thumb'), ('art', 'logo')],
                'func': self.tmdb_imagepath.get_imagepath_origin
            }],
            'backdrop_path': [{
                'keys': [('art', 'fanart'), ('art', 'backdrop')],
                'func': self.tmdb_imagepath.get_imagepath_fanart
            }],
            'release_date': [{
                'keys': [('infolabels', 'premiered')]}, {
                'keys': [('infolabels', 'year')],
                'func': lambda v: int(v[0:4])
            }],
            'first_air_date': [{
                'keys': [('infolabels', 'premiered')]}, {
                'keys': [('infolabels', 'year')],
                'func': lambda v: int(v[0:4])
            }],
            'air_date': [{
                'keys': [('infolabels', 'premiered')]}, {
                'keys': [('infolabels', 'year')],
                'func': lambda v: int(v[0:4])
            }],
            'genre_ids': [{
                'keys': [('infolabels', 'genre')],
                'func': self.get_genres_by_id
            }],
            'popularity': [{
                'keys': [('infoproperties', 'popularity')],
                'type': str
            }],
            'vote_count': [{
                'keys': [('infolabels', 'votes')],
                'type': int}, {
                'keys': [('infoproperties', 'tmdb_votes')],
                'type': float,
                'func': lambda v: f'{v:0,.0f}'
            }],
            'vote_average': [{
                'keys': [('infolabels', 'rating')],
                'type': float}, {
                'keys': [('infoproperties', 'tmdb_rating')],
                'type': float,
                'func': lambda v: f'{v:.1f}'
            }],
            'budget': [{
                'keys': [('infoproperties', 'budget')],
                'type': float,
                'func': lambda v: f'${v:0,.0f}'
            }],
            'revenue': [{
                'keys': [('infoproperties', 'revenue')],
                'type': float,
                'func': lambda v: f'${v:0,.0f}'
            }],
            'also_known_as': [{
                'keys': [('infoproperties', 'aliases')],
                'func': lambda v: ' / '.join([x for x in v or [] if x])
            }],
            'known_for': [{
                'keys': [('infoproperties', UPDATE_BASEKEY)],
                'func': self.iter_props,
                'args': ['known_for'],
                'kwargs': {'title': 'title', 'tmdb_id': 'id', 'rating': 'vote_average', 'tmdb_type': 'media_type'}}, {
                # ---
                'keys': [('infoproperties', 'known_for')],
                'func': lambda v: ' / '.join([x['title'] for x in v or [] if x.get('title')])
            }],
            'parts': [{
                'keys': [('infoproperties', UPDATE_BASEKEY)],
                'func': self.get_collection_properties
            }],
            'belongs_to_collection': [{
                'keys': [('infoproperties', UPDATE_BASEKEY)],
                'func': self.get_collection}, {
                # ---
                'keys': [('infolabels', 'set')],
                'subkeys': ['name']
            }],
            'episode_run_time': [{
                'keys': [('infolabels', 'duration')],
                'func': self.get_runtime
            }],
            'runtime': [{
                'keys': [('infolabels', 'duration')],
                'func': self.get_runtime
            }],
            'imdb_id': [{
                'keys': [('infolabels', 'imdbnumber'), ('unique_ids', 'imdb')]
            }],
            'episode_count': [{
                'keys': [('infolabels', 'episode'), ('infoproperties', 'episodes')]
            }],
            'group_count': [{
                'keys': [('infolabels', 'season'), ('infoproperties', 'seasons')]
            }],
            'character': [{
                'keys': [('infoproperties', 'role'), ('infoproperties', 'character'), ('label2', None)]
            }],
            'job': [{
                'keys': [('infoproperties', 'role'), ('infoproperties', 'job'), ('label2', None)]
            }],
            'biography': [{
                'keys': [('infoproperties', 'biography'), ('infolabels', 'plot')]
            }],
            'gender': [{
                'keys': [('infoproperties', 'gender')],
                'func': lambda v, d: d.get(v),
                'args': [{
                    1: get_localized(32071),
                    2: get_localized(32070)}]
            }]
        }
        self.standard_map = {
            'overview': ('infolabels', 'plot'),
            'content': ('infolabels', 'plot'),
            'tagline': ('infolabels', 'tagline'),
            'id': ('unique_ids', 'tmdb'),
            'provider_id': ('unique_ids', 'tmdb'),
            'original_title': ('infolabels', 'originaltitle'),
            'original_name': ('infolabels', 'originaltitle'),
            'title': ('infolabels', 'title'),
            'name': ('infolabels', 'title'),
            'author': ('infolabels', 'title'),
            'provider_name': ('infolabels', 'title'),
            'origin_country': ('infolabels', 'country'),
            'status': ('infolabels', 'status'),
            'season_number': ('infolabels', 'season'),
            'episode_number': ('infolabels', 'episode'),
            'season_count': ('infolabels', 'season'),
            'number_of_seasons': ('infolabels', 'season'),
            'number_of_episodes': ('infolabels', 'episode'),
            'department': ('infoproperties', 'department'),
            'known_for_department': ('infoproperties', 'department'),
            'place_of_birth': ('infoproperties', 'born'),
            'birthday': ('infoproperties', 'birthday'),
            'deathday': ('infoproperties', 'deathday'),
            'width': ('infoproperties', 'width'),
            'height': ('infoproperties', 'height'),
            'aspect_ratio': ('infoproperties', 'aspect_ratio'),
            'original_language': ('infoproperties', 'original_language')
        }

    def get_genres_by_id(self, v):
        genre_ids = v or []
        genre_map = {v: k for k, v in self.genres.items()}
        return [i for i in (genre_map.get(try_int(genre_id)) for genre_id in genre_ids) if i]

    def finalise(self, item, tmdb_type):
        if tmdb_type == 'tv':
            item['infolabels']['tvshowtitle'] = item['infolabels'].get('title')
        item['label'] = item['infolabels'].get('title')
        item['infoproperties']['tmdb_type'] = tmdb_type
        item['infolabels']['mediatype'] = item['infoproperties']['dbtype'] = convert_type(tmdb_type, 'dbtype')
        return item

    def add_infoproperties(self, item, infoproperties):
        if not infoproperties:
            return item
        for k, v in infoproperties:
            item['infoproperties'][k] = v
        return item

    def get_info(self, info_item, tmdb_type, base_item=None, add_infoproperties=None, **kwargs):
        item = get_empty_item()
        item = self.map_item(item, info_item)
        item = self.add_base(item, base_item, tmdb_type, key_blacklist=['year', 'premiered', 'season', 'episode'])
        item = self.add_infoproperties(item, add_infoproperties)
        item = self.finalise(item, tmdb_type)
        item['params'] = get_params(info_item, tmdb_type, params=item.get('params', {}), **kwargs)
        return item
