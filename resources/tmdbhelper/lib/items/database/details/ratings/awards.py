from jurialmunkey.ftools import cached_property


class DetailsRatingsAwards:
    """Award properties for an item, read from the local awards database."""

    tvdb_awards_keys = {
        'Academy Awards': 'academy',
        'Golden Globe Awards': 'goldenglobe',
        'MTV Movie & TV Awards': 'mtv',
        'Critics\' Choice Awards': 'criticschoice',
        'Primetime Emmy Awards': 'emmy',
        'Screen Actors Guild Awards': 'sag',
        'BAFTA Awards': 'bafta'
    }

    def __init__(self, awards_database, tmdb_type, tmdb_id):
        self.awards_database = awards_database
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id

    @cached_property
    def info(self):
        return self.get_info()

    def get_info(self):
        info = {}
        awards = self.awards_database.get_item_awards(self.tmdb_type, self.tmdb_id)
        for t in ['awards_won', 'awards_nominated']:
            item_awards = awards.get(t)
            if not item_awards:
                continue
            all_awards, all_awards_cr = [], []
            for cat, lst in item_awards.items():
                all_awards_cr.append(f'[CR]{cat}' if all_awards else cat)
                all_awards_cr += lst
                all_awards += [(f'{cat} {i}') for i in lst]
                try:
                    info[f'{self.tvdb_awards_keys[cat]}_{t}'] = len(lst)
                except(KeyError, TypeError, AttributeError):
                    continue
            if all_awards:
                info[f'total_{t}'] = len(all_awards)
                info[t] = ' / '.join(all_awards)
                info[f'{t}_cr'] = '[CR]'.join(all_awards_cr)
        return info
