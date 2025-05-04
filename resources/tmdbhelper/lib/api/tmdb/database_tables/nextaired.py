from tmdbhelper.lib.addon.consts import DEFAULT_EXPIRY, SHORTER_EXPIRY, TEMPDAY_EXPIRY
from tmdbhelper.lib.addon.tmdate import date_in_range


class TMDbDatabaseNextAired:
    nextaired_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'next_aired': {'data': 'TEXT'},
        'next_aired_long': {'data': 'TEXT'},
        'next_aired_short': {'data': 'TEXT'},
        'next_aired_day': {'data': 'TEXT'},
        'next_aired_day_short': {'data': 'TEXT'},
        'next_aired_year': {'data': 'TEXT'},
        'next_aired_episode': {'data': 'TEXT'},
        'next_aired_name': {'data': 'TEXT'},
        'next_aired_tmdb_id': {'data': 'TEXT'},
        'next_aired_plot': {'data': 'TEXT'},
        'next_aired_season': {'data': 'TEXT'},
        'next_aired_rating': {'data': 'TEXT'},
        'next_aired_votes': {'data': 'TEXT'},
        'next_aired_thumb': {'data': 'TEXT'},
        'next_aired_original': {'data': 'TEXT'},
        'next_aired_days_until_aired': {'data': 'TEXT'},
        'last_aired': {'data': 'TEXT'},
        'last_aired_long': {'data': 'TEXT'},
        'last_aired_short': {'data': 'TEXT'},
        'last_aired_day': {'data': 'TEXT'},
        'last_aired_day_short': {'data': 'TEXT'},
        'last_aired_year': {'data': 'TEXT'},
        'last_aired_episode': {'data': 'TEXT'},
        'last_aired_name': {'data': 'TEXT'},
        'last_aired_tmdb_id': {'data': 'TEXT'},
        'last_aired_plot': {'data': 'TEXT'},
        'last_aired_season': {'data': 'TEXT'},
        'last_aired_rating': {'data': 'TEXT'},
        'last_aired_votes': {'data': 'TEXT'},
        'last_aired_thumb': {'data': 'TEXT'},
        'last_aired_original': {'data': 'TEXT'},
        'last_aired_days_from_aired': {'data': 'TEXT'},
        'status': {'data': 'TEXT'},
    }

    """
    nextaired
    """

    def _get_nextaired(self, tmdb_id):
        from tmdbhelper.lib.items.database.mappings import ItemMapperMethods
        item_mapper_methods = ItemMapperMethods()

        def _get_nextaired_ip(response):
            ip = {}
            ip.update(item_mapper_methods.get_episode_to_air(response.get('next_episode_to_air'), 'next_aired'))
            ip.update(item_mapper_methods.get_episode_to_air(response.get('last_episode_to_air'), 'last_aired'))
            ip['status'] = response.get('status')
            return ip

        if not tmdb_id:
            return {}

        return _get_nextaired_ip(self.tmdb_api.get_response_json('tv', tmdb_id, language=self.tmdb_api.req_language) or {}) or {}

    def get_nextaired(self, tmdb_id):
        table = 'nextaired'
        keys = tuple(self.nextaired_columns.keys())

        def configure_dict(data):
            return {
                k.replace('next_aired_', 'next_aired.').replace('last_aired_', 'last_aired.'): data[k]
                for k in data.keys()
            } if data else {}

        def get_expiry(data):
            if data.get('status') in ('Cancelled', 'Ended'):
                return DEFAULT_EXPIRY
            item_airdate = data.get('next_aired_original') or data.get('last_aired_original')
            if date_in_range(item_airdate, 10, -2, date_fmt="%Y-%m-%d", date_lim=10):
                return TEMPDAY_EXPIRY
            return SHORTER_EXPIRY

        def get_cached():
            return self.get_cached_item_values(table, tmdb_id, keys, configure_dict)  # ADD mapping_function

        def set_cached():
            data = self._get_nextaired(tmdb_id)
            if not data:
                return
            data['id'] = tmdb_id
            self.set_cached_values(
                table, keys,
                values=tuple((data.get(k) for k in keys)),
                item_id=tmdb_id,
                expiry=get_expiry(data)
            )
            return get_cached()

        return get_cached() or set_cached()

    def get_nextaired_formatted(self, tmdb_id):
        from tmdbhelper.lib.addon.tmdate import format_date
        from tmdbhelper.lib.addon.plugin import get_infolabel

        def _get_formatted(ip):
            df = get_infolabel('Skin.String(TMDbHelper.Date.Format)') or '%d %b %Y'
            for i in ['next_aired', 'last_aired']:
                try:
                    air_date = ip[f'{i}.original']
                except KeyError:
                    continue
                ip[f'{i}.custom'] = format_date(air_date, df)
            return ip

        infoproperties = self.get_nextaired(tmdb_id)  # Need separate database objects for threading

        if not infoproperties:
            return {}

        return _get_formatted(infoproperties)
