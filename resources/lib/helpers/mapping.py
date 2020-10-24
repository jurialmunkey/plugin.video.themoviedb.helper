from resources.lib.helpers.parser import try_type
from resources.lib.helpers.plugin import viewitems, convert_type, TYPE_DB
from resources.lib.helpers.timedate import age_difference

UPDATE_BASEKEY = 1


def get_empty_item():
    return {
        'art': {},
        'cast': [],
        'infolabels': {},
        'infoproperties': {},
        'unique_ids': {},
        'params': {}}


def set_show(item, base_item=None):
    if not base_item:
        return item
    item['art'].update(
        {'tvshow.{}'.format(k): v for k, v in viewitems(base_item.get('art', {}))})
    item['unique_ids'].update(
        {'tvshow.{}'.format(k): v for k, v in viewitems(base_item.get('unique_ids', {}))})
    item['infoproperties'].update(
        {'tvshow.{}'.format(k): v for k, v in viewitems(base_item.get('infolabels', {})) if type(v) in [str, int]})
    item['infolabels']['tvshowtitle'] = base_item['infolabels'].get('title')
    item['unique_ids']['tmdb'] = item['unique_ids'].get('tvshow.tmdb')
    return item


class _ItemMapper(object):
    def add_base(self, item, base_item=None, tmdb_type=None):
        if not base_item:
            return item
        for d in ['infolabels', 'infoproperties', 'art']:
            for k, v in viewitems(base_item.get(d, {})):
                if not v or item[d].get(k):
                    continue
                item[d][k] = v
        return set_show(item, base_item) if tmdb_type in ['season', 'episode', 'tv'] else item

    def finalise_image(self, item):
        item['infolabels']['title'] = '{}x{}'.format(
            item['infoproperties'].get('width'),
            item['infoproperties'].get('height'))
        item['params'] = -1
        item['path'] = item['art'].get('thumb') or item['art'].get('poster') or item['art'].get('fanart')
        item['is_folder'] = False
        item['library'] = 'pictures'
        return item

    def finalise_person(self, item):
        if item['infoproperties'].get('birthday'):
            item['infoproperties']['age'] = age_difference(
                item['infoproperties']['birthday'],
                item['infoproperties'].get('deathday'))
        return item

    def finalise(self, item, tmdb_type):
        if tmdb_type == 'image':
            item = self.finalise_image(item)
        elif tmdb_type == 'person':
            item = self.finalise_person(item)
        item['label'] = item['infolabels'].get('title')
        item['infoproperties']['tmdb_type'] = tmdb_type
        item['infolabels']['mediatype'] = item['infoproperties']['dbtype'] = convert_type(tmdb_type, TYPE_DB)
        item['art']['thumb'] = item['art'].get('thumb') or item['art'].get('poster')
        for k, v in viewitems(item['unique_ids']):
            item['infoproperties']['{}_id'.format(k)] = v
        return item

    def map_item(self, item, i):
        sm = self.standard_map or {}
        am = self.advanced_map or {}

        # Iterate over item retrieved from api list
        for k, pv in viewitems(i):
            # Skip empty objects
            if not pv and pv is not 0:
                continue
            # Simple mapping is quicker so do that first if we can
            if k in sm:
                item[sm[k][0]][sm[k][1]] = pv
                continue
            # Check key is in advanced map before trying to map it
            if k not in am:
                continue
            # Iterate over list of dictionaries
            for d in am[k]:
                # Make a quick copy of object
                if isinstance(pv, dict):
                    v = pv.copy()
                elif isinstance(pv, list):
                    v = pv[:]
                else:
                    v = pv
                # Get subkeys
                if 'subkeys' in d:
                    for ck in d['subkeys']:
                        v = v.get(ck) or {}
                    if not v:
                        continue
                # Run through type conversion
                if 'type' in d:
                    v = try_type(v, d['type'])
                # Run through func
                if 'func' in d:
                    v = d['func'](v, *d.get('args', []), **d.get('kwargs', {}))
                # Check not empty
                if not v and v is not 0:
                    continue
                # Map value onto item dict parent/child keys
                for p, c in d['keys']:
                    if c == UPDATE_BASEKEY:
                        item[p].update(v)
                    elif c is None:
                        item[p] = v
                    elif 'extend' in d and isinstance(item[p].get(c), list) and isinstance(v, list):
                        item[p][c] += v
                    else:
                        item[p][c] = v
        return item
