from tmdbhelper.lib.files.dbdata import DatabaseStatements


class TableTMDbID:
    table = 'tmdb_id'
    tmdb_type = None
    imdb_id = None
    tvdb_id = None
    query = None
    year = None
    raw_data = False

    def __init__(self, parent):
        self.parent = parent

    @property
    def tmdb_api(self):
        return self.parent.tmdb_api

    @property
    def access(self):
        return self.parent.access

    @property
    def func(self):
        return self.tmdb_api.get_response_json

    def get_id(self, values, conditions, keys=None):
        with self.access.connection.open():
            data = self.access.get_cached_list_values(
                self.table,
                keys=('tmdb_id', ) if not keys else keys,
                values=values,
                conditions=conditions)
        if not data:
            return
        return data[0]['tmdb_id'] if not keys else data[0]

    def set_id(self, data_id, external_source, tmdb_id):
        statement_insert = DatabaseStatements.insert_or_ignore(self.table, ('tmdb_id', 'tmdb_type'))
        statement_update = DatabaseStatements.update_if_null(
            self.table, (external_source, ), conditions="tmdb_type=? AND tmdb_id=?")

        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            connection.execute(statement_insert, (tmdb_id, self.tmdb_type))
            connection.execute(statement_update, (data_id, self.tmdb_type, tmdb_id, ))
            connection.execute('COMMIT')

    def find_id(self, data_id, external_source):
        try:
            data = self.func('find', data_id, language=self.tmdb_api.req_language, external_source=external_source)
            return data[f'{self.tmdb_type}_results'][0]['id']
        except (AttributeError, KeyError, TypeError, IndexError):
            pass
        if self.tmdb_type != 'tv':
            return
        try:
            return data['tv_episode_results'][0]['show_id']
        except (AttributeError, KeyError, TypeError, IndexError):
            return

    def get_imdb_id(self):
        return self.get_id((self.tmdb_type, self.imdb_id), 'tmdb_type=? AND imdb_id=?')

    def set_imdb_id(self):
        tmdb_id = self.find_id(self.imdb_id, external_source='imdb_id')
        if not tmdb_id:
            return
        self.set_id(self.imdb_id, external_source='imdb_id', tmdb_id=tmdb_id)
        return self.get_imdb_id()

    def get_tvdb_id(self):
        return self.get_id((self.tmdb_type, self.tvdb_id), 'tmdb_type=? AND tvdb_id=?')

    def set_tvdb_id(self):
        tmdb_id = self.find_id(self.tvdb_id, external_source='tvdb_id')
        if not tmdb_id:
            return
        self.set_id(self.tvdb_id, external_source='tvdb_id', tmdb_id=tmdb_id)
        return self.get_tvdb_id()

    def find_query(self):
        from urllib.parse import quote_plus
        args = ('search', self.tmdb_type)
        kwgs = {'language': self.tmdb_api.req_language, 'query': quote_plus(self.query)}

        def configure_find_query_kwgs():
            if not self.year:
                return kwgs
            if self.tmdb_type == 'tv':
                kwgs['first_air_date_year'] = self.year
                return kwgs
            if self.tmdb_type == 'movie':
                kwgs['year'] = self.year
                return kwgs

        kwgs = configure_find_query_kwgs()

        try:
            data = self.func(*args, **kwgs)
            data = data['results']
        except (TypeError, KeyError):
            return
        if not data:
            return
        if self.raw_data:
            return data

        def return_next_matching_result():
            if self.year and self.tmdb_type == 'movie':
                return next((
                    i['id'] for i in data
                    if (i['title'] or '').casefold() == self.query and (i['release_date'] or '').startswith(str(self.year))), None)
            if self.year and self.tmdb_type == 'tv':
                return next((
                    i['id'] for i in data
                    if (i['name'] or '').casefold() == self.query and (i['first_air_date'] or '').startswith(str(self.year))), None)
            return next((
                i['id'] for i in data
                if (i.get('name') or i.get('title') or '').casefold() == self.query), None)

        return return_next_matching_result()

    def find_multisearch_query(self):
        from urllib.parse import quote_plus
        args = ('search', 'multi')
        kwgs = {'language': self.tmdb_api.req_language, 'query': quote_plus(self.query)}
        try:
            data = self.func(*args, **kwgs)
            data = data['results']
        except (TypeError, KeyError):
            return
        if not data:
            return
        return next(
            (
                {'tmdb_id': i['id'], 'tmdb_type': i['media_type']} for i in data
                if i.get('media_type') in (self.tmdb_type or 'movie', self.tmdb_type or 'tv')  # If we've got a tmdb_type we only check that otherwise fallback to movie/tv
                and (
                    (i.get('name') or '').casefold() == self.query
                    or (i.get('title') or '').casefold() == self.query
                    or (i.get('original_name') or '').casefold() == self.query
                    or (i.get('original_title') or '').casefold() == self.query
                )
            ),
            None
        )

    def get_name_id(self):
        if not self.year:
            return self.get_id((self.tmdb_type, self.query), 'tmdb_type=? AND title=?')
        return self.get_id((self.tmdb_type, self.query, self.year), 'tmdb_type=? AND title=? AND year=?')

    def set_name_id(self):
        tmdb_id = self.find_query()
        if not tmdb_id:
            return

        statement_insert = DatabaseStatements.insert_or_ignore(self.table, ('tmdb_id', 'tmdb_type'))
        statement_update = DatabaseStatements.update_if_null(
            self.table, ('title', 'year'), conditions="tmdb_type=? AND tmdb_id=?")

        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            connection.execute(statement_insert, (tmdb_id, self.tmdb_type))
            connection.execute(statement_update, (self.query, self.year, self.tmdb_type, tmdb_id, ))
            connection.execute('COMMIT')

        return self.get_name_id()

    def get_multisearch_query(self):
        lookup = self.get_id(
            (self.query, self.tmdb_type or 'movie', self.tmdb_type or 'tv'),  # IF we've got a tmdb_type only use that otherwise fallback to using movie/tv
            'title=? AND (tmdb_type=? OR tmdb_type=?)',
            keys=('tmdb_id', 'tmdb_type'))
        if not lookup:
            return
        return (lookup['tmdb_id'], lookup['tmdb_type'])

    def set_multisearch_query(self):
        lookup = self.find_multisearch_query()
        if not lookup:
            return

        tmdb_id = lookup['tmdb_id']
        tmdb_type = lookup['tmdb_type']

        statement_insert = DatabaseStatements.insert_or_ignore(self.table, ('tmdb_id', 'tmdb_type'))
        statement_update = DatabaseStatements.update_if_null(
            self.table, ('title', ), conditions="tmdb_type=? AND tmdb_id=?")

        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            connection.execute(statement_insert, (tmdb_id, tmdb_type))
            connection.execute(statement_update, (self.query, tmdb_type, tmdb_id, ))
            connection.execute('COMMIT')

        return self.get_multisearch_query()


class TMDbDatabaseTMDbID:
    tmdb_id_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'indexed': True,
            'unique': True
        },
        'tmdb_type': {
            'data': 'TEXT',
            'unique': True
        },
        'imdb_id': {
            'data': 'TEXT',
            'indexed': True
        },
        'tvdb_id': {
            'data': 'INTEGER',
            'indexed': True
        },
        'title': {
            'data': 'TEXT',
            'indexed': True
        },
        'year': {
            'data': 'INTEGER',
            'indexed': True
        },
    }

    """
    tmdb_id
    """

    def get_tmdb_id(self, tmdb_type=None, imdb_id=None, tvdb_id=None, query=None, year=None, raw_data=False, use_multisearch=False, **kwargs):
        table_obj = TableTMDbID(self)
        table_obj.tmdb_type = tmdb_type
        table_obj.imdb_id = imdb_id
        table_obj.query = (query or '').casefold()  # Case fold query to avoid case sensitivity issues
        table_obj.year = year
        table_obj.raw_data = raw_data

        if use_multisearch or tmdb_type is None:
            if not use_multisearch:
                return
            return table_obj.get_multisearch_query() or table_obj.set_multisearch_query() or (None, None)

        def try_imdb_id():
            if not imdb_id:
                return
            return table_obj.get_imdb_id() or table_obj.set_imdb_id()

        def try_tvdb_id():
            if not tvdb_id:
                return
            return table_obj.get_tvdb_id() or table_obj.set_tvdb_id()

        def try_name_id():
            if not query:
                return
            return table_obj.get_name_id() or table_obj.set_name_id()

        if raw_data and query:
            return table_obj.find_query()

        tmdb_id = try_imdb_id() or try_tvdb_id() or try_name_id()
        if not tmdb_id:
            return (None, None) if use_multisearch else None
        return (tmdb_id, tmdb_type) if use_multisearch else tmdb_id

    def get_tmdb_id_from_query(self, tmdb_type, query, header=None, use_details=False, get_listitem=False, auto_single=False):
        """
        Method to select matching item from dialog
        """
        from xbmcgui import Dialog
        from tmdbhelper.lib.items.listitem import ListItem
        if not query or not tmdb_type:
            return
        response = self.get_tmdb_id(tmdb_type, query=query, raw_data=True)
        if not response:
            return
        items = [ListItem(**self.tmdb_api.mapper.get_info(i, tmdb_type)).get_listitem() for i in response]
        if not items:
            return
        x = 0
        if not auto_single or len(items) != 1:
            x = Dialog().select(header, items, useDetails=use_details)
        if x == -1:
            return
        return items[x] if get_listitem else items[x].getUniqueID('tmdb')
