from tmdbhelper.lib.addon.plugin import get_language, get_setting
from tmdbhelper.lib.api.request import NoCacheRequestAPI
from tmdbhelper.lib.api.tmdb.mapping import ItemMapper
from tmdbhelper.lib.api.api_keys.tmdb import API_KEY
from jurialmunkey.ftools import cached_property


API_URL = 'https://api.themoviedb.org/3' if not get_setting('use_alternate_api_url') else 'https://api.tmdb.org/3'


class TMDbAPI(NoCacheRequestAPI):

    api_key = API_KEY
    api_url = API_URL
    append_to_response = ''
    append_to_response_person = ''
    api_name = 'TMDbAPI'

    def __init__(
            self,
            api_key=None,
            language=get_language()):
        api_key = api_key or self.api_key
        api_url = self.api_url
        api_name = self.api_name

        super(TMDbAPI, self).__init__(
            req_api_name=api_name,
            req_api_url=api_url,
            req_api_key=f'api_key={api_key}')
        self.language = language
        TMDb.api_key = api_key

    @property
    def req_strip(self):
        req_strip_add = [
            (self.append_to_response, 'standard'),
            (self.append_to_response_person, 'person'),
            (self.append_to_response_tvshow, 'tvshow'),
            (self.append_to_response_tvshow_simple, 'tvshow_simple'),
            (self.append_to_response_movies_simple, 'movies_simple'),
            (self.req_language, f'{self.iso_language}_en')
        ]
        try:
            return self._req_strip + req_strip_add
        except AttributeError:
            self._req_strip = [
                (self.req_api_url, self.req_api_name),
                (self.req_api_key, ''),
                ('is_xml=False', ''),
                ('is_xml=True', '')
            ]
            return self._req_strip + req_strip_add

    @req_strip.setter
    def req_strip(self, value):
        self._req_strip = value

    @property
    def req_language(self):
        return f'{self.iso_language}-{self.iso_country}'

    @property
    def iso_language(self):
        return self.language[:2]

    @property
    def iso_country(self):
        return self.language[-2:]

    @property
    def genres(self):
        return

    @property
    def mapper(self):
        try:
            return self._mapper
        except AttributeError:
            self._mapper = ItemMapper(self.language, self.genres)
            return self._mapper

    @staticmethod
    def get_url_separator(separator=None):
        if separator == 'AND':
            return '%2C'
        elif separator == 'OR':
            return '%7C'
        elif not separator:
            return '%2C'
        else:
            return False

    @staticmethod
    def get_paginated_items(items, limit=None, page=1, total_pages=None):
        from jurialmunkey.parser import try_int
        if total_pages and try_int(page) < try_int(total_pages):
            items.append({'next_page': try_int(page) + 1})
            return items
        if limit is not None:
            from tmdbhelper.lib.items.pages import PaginatedItems
            paginated_items = PaginatedItems(items, page=page, limit=limit)
            return paginated_items.items + paginated_items.next_page
        return items

    def configure_request_kwargs(self, kwargs):
        kwargs['language'] = self.req_language
        return kwargs

    def get_response_json(self, *args, postdata=None, headers=None, method=None, **kwargs):
        kwargs = self.configure_request_kwargs(kwargs)
        requrl = self.get_request_url(*args, **kwargs)
        return self.get_api_request_json(requrl, postdata=postdata, headers=headers, method=method)


class TMDb(TMDbAPI):
    append_to_response = 'credits,images,release_dates,external_ids,keywords,reviews,videos,watch/providers'
    append_to_response_tvshow = 'aggregate_credits,images,content_ratings,external_ids,keywords,reviews,videos,watch/providers'
    append_to_response_person = 'images,external_ids,movie_credits,tv_credits'
    append_to_response_movies_simple = 'images,external_ids,release_dates'
    append_to_response_tvshow_simple = 'images,external_ids,content_ratings'
    append_to_response_movies_translation = 'credits,images,release_dates,external_ids,keywords,reviews,videos,watch/providers,translations'
    append_to_response_tvshow_translation = 'aggregate_credits,images,content_ratings,external_ids,keywords,reviews,videos,watch/providers,translations'
    api_name = 'TMDb'

    @property
    def tmdb_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        tmdb_database = FindQueriesDatabase()
        tmdb_database.tmdb_api = self  # Must override attribute to avoid circular import
        return tmdb_database

    @property
    def get_tmdb_id(self):
        return self.tmdb_database.get_tmdb_id

    @cached_property
    def genres(self):
        return self.tmdb_database.genres

    @property
    def iso_region(self):
        if not self.setting_ignore_regionreleasefilter:
            return self.iso_country

    @property
    def setting_ignore_regionreleasefilter(self):
        try:
            return self._setting_ignore_regionreleasefilter
        except AttributeError:
            self._setting_ignore_regionreleasefilter = get_setting('ignore_regionreleasefilter')
            return self._setting_ignore_regionreleasefilter

    @property
    def include_image_language(self):
        return f'{self.iso_language},null,en'

    @property
    def include_video_language(self):
        return f'{self.iso_language},null,en'

    def configure_request_kwargs(self, kwargs):
        kwargs['region'] = self.iso_region
        kwargs['language'] = self.req_language
        kwargs['include_image_language'] = self.include_image_language
        kwargs['include_video_language'] = self.include_video_language
        return kwargs
