from tmdbhelper.lib.api.mapping import _ItemMapper
from jurialmunkey.parser import get_between_strings, try_type


class ItemMapper(_ItemMapper):
    def __init__(self):
        self.blacklist = ['N/A', '0.0', '0']
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
            'awards': [{
                'keys': [('awards', None)]}, {
                # ---
                'keys': [('oscar_wins', None)],
                'func': lambda v: try_type(get_between_strings(v or '', 'Won ', ' Oscar'), int)}, {
                # ---
                'keys': [('emmy_wins', None)],
                'func': lambda v: try_type(get_between_strings(v or '', 'Won ', ' Primetime Emmy'), int)}, {
                # ---
                'keys': [('award_wins', None)],
                'func': lambda v: try_type(get_between_strings(v or '', '.* ', ' win') or get_between_strings(v or '', '', ' win'), int)}, {
                # ---
                'keys': [('oscar_nominations', None)],
                'func': lambda v: try_type(get_between_strings(v or '', 'Nominated for ', ' Oscar'), int)}, {
                # ---
                'keys': [('emmy_nominations', None)],
                'func': lambda v: try_type(get_between_strings(v or '', 'Nominated for ', ' Primetime Emmy'), int)}, {
                # ---
                'keys': [('award_nominations', None)],
                'func': lambda v: try_type(get_between_strings(v or '', 'wins? & ', ' nomination') or get_between_strings(v or '', '', ' nomination'), int)
            }],
            'tomatoReviews': [{
                'keys': [('rottentomatoes_reviewstotal', None)],
                'type': int,
            }],
            'tomatoFresh': [{
                'keys': [('rottentomatoes_reviewsfresh', None)],
                'type': int,
            }],
            'tomatoRotten': [{
                'keys': [('rottentomatoes_reviewsrotten', None)],
                'type': int,
            }],
            'tomatoUserReviews': [{
                'keys': [('rottentomatoes_userreviews', None)],
                'type': int,
            }],
            'metascore': [{
                'keys': [('metacritic_rating', None)],
                'type': int,
            }],
            'imdbRating': [{
                'keys': [('imdb_rating', None)],
                'func': lambda v: try_type(try_type(v, float) * 10, int)
            }],
            'imdbVotes': [{
                'keys': [('imdb_votes', None)],
                'func': lambda v: try_type(v.replace(',', ''), int)
            }],
            'tomatoMeter': [{
                'keys': [('rottentomatoes_rating', None)],
                'type': int,
            }],
            'tomatoImage': [{
                'keys': [('rottentomatoes_image', None)],
            }],
            'tomatoConsensus': [{
                'keys': [('rottentomatoes_consensus', None)],
            }],
            'tomatoUserMeter': [{
                'keys': [('rottentomatoes_usermeter', None)],
                'type': int,
            }],
        }
        self.standard_map = {}

    def get_info(self, info_item, tmdb_type=None, **kwargs):
        item = {}
        item = self.map_item(item, info_item)
        return item
