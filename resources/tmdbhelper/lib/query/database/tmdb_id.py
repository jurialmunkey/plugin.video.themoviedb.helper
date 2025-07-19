import operator
from tmdbhelper.lib.files.dbdata import DatabaseStatements
from jurialmunkey.ftools import cached_property


class TableID:

    table = 'tmdb_id'
    values = None
    conditions = None
    keys = ('tmdb_id', )

    update_keys = ()
    update_values = ()

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

    def get_id_results(self, data):
        try:
            return data[0]['tmdb_id']  # return data[0] for multi
        except (AttributeError, KeyError, TypeError, IndexError):
            return

    def get_id(self):
        with self.access.connection.open():
            return self.get_id_results(self.access.get_cached_list_values(
                self.table,
                keys=self.keys,
                values=self.values,
                conditions=self.conditions))

    def set_id(self):
        if not self.tmdb_id or not self.tmdb_type:
            return

        statement_insert = DatabaseStatements.insert_or_ignore(self.table, ('tmdb_id', 'tmdb_type'))
        statement_update = DatabaseStatements.update_if_null(
            self.table, self.update_keys, conditions="tmdb_type=? AND tmdb_id=?")

        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            connection.execute(statement_insert, (self.tmdb_id, self.tmdb_type))
            connection.execute(statement_update, self.update_values)
            connection.execute('COMMIT')

        return self.get_id()


class TableFindID(TableID):

    external_source = None
    data_id = None

    def __init__(self, tmdb_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tmdb_type = tmdb_type

    @property
    def update_keys(self):
        return (self.external_source, )

    @property
    def update_values(self):
        return (self.data_id, self.tmdb_type, self.tmdb_id, )

    @property
    def func_args(self):
        return ('find', self.data_id)

    @property
    def func_kwgs(self):
        return {'language': self.tmdb_api.req_language, 'external_source': self.external_source}

    @cached_property
    def func_data(self):
        return self.func(*self.func_args, **self.func_kwgs)

    @cached_property
    def func_base_id(self):
        try:
            return self.func_data[f'{self.tmdb_type}_results'][0]['id']
        except (AttributeError, KeyError, TypeError, IndexError):
            pass

    @cached_property
    def func_show_id(self):
        if self.tmdb_type != 'tv':
            return
        try:
            return self.func_data['tv_episode_results'][0]['show_id']
        except (AttributeError, KeyError, TypeError, IndexError):
            return

    @cached_property
    def tmdb_id(self):
        return self.func_base_id or self.func_show_id

    @property
    def values(self):
        return (self.tmdb_type, self.data_id)


class TableIMDbID(TableFindID):
    conditions = 'tmdb_type=? AND imdb_id=?'
    external_source = 'imdb_id'


class TableTVDbID(TableFindID):
    conditions = 'tmdb_type=? AND tvdb_id=?'
    external_source = 'tvdb_id'


class TableSearchID(TableID):

    year = None
    episode_year = None
    update_keys = ('title', 'year')

    @property
    def update_values(self):
        return (self.query, self.tmdb_year, self.tmdb_type, self.tmdb_id, )

    @property
    def func_args(self):
        return ('search', self.tmdb_type)

    @property
    def func_additional_kwgs(self):

        if self.tmdb_type == 'movie':
            return (
                {'year': self.year}
                if self.year else
                {}
            )

        if self.tmdb_type == 'tv':
            return (
                {'first_air_date_year': self.year}  # Search specific year for tvshow
                if self.year else
                {'year': self.episode_year}  # Search all episode years
                if self.episode_year else
                {}
            )

        return {}

    @property
    def func_kwgs(self):
        from urllib.parse import quote_plus
        func_kwgs = {'language': self.tmdb_api.req_language, 'query': quote_plus(self.query)}
        func_kwgs.update(self.func_additional_kwgs)
        return func_kwgs

    @cached_property
    def func_data(self):
        return self.func(*self.func_args, **self.func_kwgs)

    @cached_property
    def func_data_results(self):
        try:
            return self.func_data['results']
        except (TypeError, KeyError):
            return

    @staticmethod
    def func_data_id_year_comparison(item, key, value, operator_type='eq'):
        comparison = getattr(operator, operator_type)
        return comparison(int((item[key] or '9999')[:4]), int(value))

    @cached_property
    def func_data_id_generator(self):
        return (
            (
                i for i in self.func_data_results
                if (i['title'] or '').casefold() == self.query
                and self.func_data_id_year_comparison(i, 'release_date', self.year)
            )
            if self.year and self.tmdb_type == 'movie' else
            (
                i for i in self.func_data_results
                if (i['name'] or '').casefold() == self.query
                and self.func_data_id_year_comparison(i, 'first_air_date', self.year)
            )
            if self.year and self.tmdb_type == 'tv' else
            (
                i for i in self.func_data_results
                if (i['name'] or '').casefold() == self.query
                and self.func_data_id_year_comparison(i, 'first_air_date', self.episode_year, operator_type='le')
            )
            if self.episode_year and self.tmdb_type == 'tv' else
            (
                i for i in self.func_data_results
                if (i.get('name') or i.get('title') or '').casefold() == self.query
            )
        )

    @cached_property
    def func_data_id_generator_results(self):
        if not self.func_data_results:
            return
        return next(self.func_data_id_generator, None)

    @cached_property
    def tmdb_id(self):
        try:
            return self.func_data_id_generator_results['id']
        except (KeyError, TypeError):
            return

    @cached_property
    def tmdb_year(self):
        try:
            return self.func_data_id_generator_results['release_date'][:4]
        except (KeyError, TypeError):
            pass
        try:
            return self.func_data_id_generator_results['first_air_date'][:4]
        except (KeyError, TypeError):
            pass

    @property
    def values(self):
        return (

            (self.tmdb_type, self.query, self.year)
            if self.year else
            (self.tmdb_type, self.query, self.episode_year)
            if self.episode_year else
            (self.tmdb_type, self.query)
        )

    @property
    def conditions(self):
        return (
            'tmdb_type=? AND title=? AND year=?'
            if self.year else
            'tmdb_type=? AND title=? AND year<=?'
            if self.episode_year else
            'tmdb_type=? AND title=?'
        )


class TableNameID(TableSearchID):
    def __init__(self, tmdb_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tmdb_type = tmdb_type


class TableMultiSearchID(TableSearchID):
    def __init__(self, tmdb_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_tmdb_type(tmdb_type)

    allowed_media_types = ('movie', 'tv')

    def init_tmdb_type(self, tmdb_type):
        if not tmdb_type:  # Check first as we want to keep cached_property getter intact otherwise
            return
        self.tmdb_type = tmdb_type
        self.allowed_media_types = (tmdb_type, tmdb_type)

    keys = ('tmdb_id', 'tmdb_type')
    conditions = 'title=? AND (tmdb_type=? OR tmdb_type=?)'

    @property
    def values(self):
        return (self.query, *self.allowed_media_types)

    @cached_property
    def func_data_id_generator(self):
        return (
            i for i in self.func_data_results
            if i.get('media_type') in self.allowed_media_types  # If we've got a tmdb_type we only check that otherwise fallback to movie/tv
            and (
                (i.get('name') or '').casefold() == self.query
                or (i.get('title') or '').casefold() == self.query
                or (i.get('original_name') or '').casefold() == self.query
                or (i.get('original_title') or '').casefold() == self.query
            )
        )

    func_args = ('search', 'multi')
    func_additional_kwgs = {}

    def get_id_results(self, data):
        try:
            return (data[0]['tmdb_id'], data[0]['tmdb_type'])
        except (AttributeError, KeyError, TypeError, IndexError):
            return

    @cached_property
    def tmdb_id(self):
        try:
            return self.func_data_id_generator_results['id']
        except (AttributeError, KeyError, TypeError, IndexError):
            return

    @cached_property
    def tmdb_type(self):
        try:
            return self.func_data_id_generator_results['media_type']
        except (AttributeError, KeyError, TypeError, IndexError):
            return


class FindQueriesDatabaseTMDbID:
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

    def get_tmdb_id(self, tmdb_type=None, imdb_id=None, tvdb_id=None, query=None, year=None, episode_year=None, use_multisearch=False, **kwargs):

        if tmdb_type is None and not use_multisearch:
            return

        if use_multisearch:
            table_obj = TableMultiSearchID(parent=self, tmdb_type=tmdb_type)
            table_obj.query = (query or '').casefold()  # Case fold query to avoid case sensitivity issues
            table_obj.year = year
            table_obj.episode_year = episode_year
            return table_obj.get_id() or table_obj.set_id() or (None, None)

        def try_imdb_id():
            if not imdb_id:
                return
            table_obj = TableIMDbID(parent=self, tmdb_type=tmdb_type)
            table_obj.data_id = imdb_id
            return table_obj.get_id() or table_obj.set_id()

        def try_tvdb_id():
            if not tvdb_id:
                return
            table_obj = TableTVDbID(parent=self, tmdb_type=tmdb_type)
            table_obj.data_id = tvdb_id
            return table_obj.get_id() or table_obj.set_id()

        def try_name_id():
            if not query:
                return
            table_obj = TableNameID(parent=self, tmdb_type=tmdb_type)
            table_obj.query = (query or '').casefold()  # Case fold query to avoid case sensitivity issues
            table_obj.year = year
            table_obj.episode_year = episode_year
            return table_obj.get_id() or table_obj.set_id()

        return try_imdb_id() or try_tvdb_id() or try_name_id() or None

    def get_tmdb_id_from_query(self, tmdb_type, query, header=None, use_details=False, get_listitem=False, auto_single=False):
        """
        Method to select matching item from dialog
        """
        from xbmcgui import Dialog
        from tmdbhelper.lib.items.listitem import ListItem

        if not query or not tmdb_type:
            return

        table_obj = TableNameID(parent=self, tmdb_type=tmdb_type)
        table_obj.query = (query or '').casefold()  # Case fold query to avoid case sensitivity issues

        response = table_obj.func_data_results
        if not response:
            return

        items = [ListItem(**self.tmdb_api.mapper.get_info(i, tmdb_type)).get_listitem(finalise=True) for i in response]
        if not items:
            return

        x = 0
        if not auto_single or len(items) != 1:
            x = Dialog().select(header, items, useDetails=bool(use_details))
        if x == -1:
            return

        return items[x] if get_listitem else items[x].getUniqueID('tmdb')
