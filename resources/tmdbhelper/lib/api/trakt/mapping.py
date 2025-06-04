from tmdbhelper.lib.api.mapping import _ItemMapper, get_empty_item, UPDATE_BASEKEY


PARAMS_DEF = {
    'movie': {'info': 'details', 'tmdb_type': 'movie', 'tmdb_id': '{unique_ids[tmdb]}'},
    'tv': {'info': 'details', 'tmdb_type': 'tv', 'tmdb_id': '{unique_ids[tmdb]}'}
}
MEDIATYPE = {
    'movie': 'movie',
    'tv': 'tvshow',
}


class ItemMapperMethods:
    pass


class ItemMapper(_ItemMapper, ItemMapperMethods):
    def __init__(self):
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
            'ids': [{
                'keys': [('unique_ids', UPDATE_BASEKEY)]
            }],
        }
        self.standard_map = {
            'title': ('infolabels', 'title'),
            'year': ('infolabels', 'year'),
            'watchers': ('infoproperties', 'watchers'),
            'watcher_count': ('infoproperties', 'watchers'),
            'play_count': ('infoproperties', 'plays'),
            'collected_count': ('infoproperties', 'collectors'),
            'list_count': ('infoproperties', 'lists'),
        }

    def finalise(self, item, info_item, tmdb_type, add_infoproperties=None, **kwargs):
        item['params'] = {k: v.format(**item) for k, v in PARAMS_DEF[tmdb_type].items()}
        item['infoproperties'].update({k: v for k, v in (add_infoproperties or ())})
        item['infoproperties']['tmdb_type'] = tmdb_type
        item['infolabels']['mediatype'] = MEDIATYPE[tmdb_type]
        return item

    def get_info(self, info_item, tmdb_type, add_infoproperties=None, **kwargs):
        item = get_empty_item()
        item = self.map_item(item, info_item)
        item = self.finalise(item, info_item, tmdb_type, add_infoproperties, **kwargs)
        return item
