from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties, UncachedItemsPage
from tmdbhelper.lib.addon.plugin import get_setting, convert_type, get_localized
from tmdbhelper.lib.files.ftools import cached_property
from jurialmunkey.parser import try_int


PAGES_LENGTH = get_setting('pagemulti_trakt', 'int') or 1


class UncachedTraktItemsPage(UncachedItemsPage):
    def __init__(self, outer_class, page):
        self.outer_class = outer_class
        self.page = page

    @cached_property
    def results(self):
        try:
            results = self.response.json()
        except (TypeError, KeyError):
            return []
        try:
            self.outer_class.total_pages = try_int(self.response.headers.get('x-pagination-page-count', 0))
            self.outer_class.total_items = try_int(self.response.headers.get('x-pagination-item-count', 0))
        except (TypeError, KeyError):
            self.outer_class.total_pages = 0
            self.outer_class.total_items = 0
        return results


class ListTraktStandardProperties(ListStandardProperties):

    class_pages = UncachedTraktItemsPage
    trakt_filters = {}
    trakt_authorization = False

    sub_type = False
    sub_type_map = {
        'movie': 'movie',
        'tv': 'show',
    }

    @property
    def next_page(self):
        return self.page + 1

    @cached_property
    def limit(self):
        return self.length * 20

    @cached_property
    def cache_name(self):
        return '_'.join(map(str, self.cache_name_tuple))

    @cached_property
    def cache_name_tuple(self):
        cache_name_tuple = [f'{k}={v}' for k, v in self.trakt_filters.items()]
        cache_name_tuple = sorted(cache_name_tuple)
        cache_name_tuple = [self.class_name, self.tmdb_type] + cache_name_tuple
        cache_name_tuple = cache_name_tuple + [self.page, self.limit]
        return tuple(cache_name_tuple)

    @cached_property
    def trakt_type(self):
        return self.sub_type_map[self.tmdb_type]

    @cached_property
    def url(self):
        return self.request_url.format(trakt_type=self.trakt_type)

    @cached_property
    def mapper(self):
        from tmdbhelper.lib.api.trakt.mapping import ItemMapper
        return ItemMapper()

    def get_uncached_items(self):
        return {
            'items': self.class_pages(self, self.page).items,
            'pages': self.total_pages,
            'count': self.total_items,
        }

    def get_uncached_response(self, page=1):
        if self.trakt_authorization and not self.trakt_api.authorization:
            if self.trakt_api.attempted_login or not self.trakt_api.authorize(login=True):
                return
        return self.trakt_api.get_response(self.url, page=page, limit=self.limit, **self.trakt_filters)

    def get_sub_typed_item(self, item):
        if not self.sub_type:
            return item
        item.update(item.pop(self.trakt_type, {}))
        return item

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.mapper.get_info(
            self.get_sub_typed_item(item),
            self.tmdb_type,
            add_infoproperties=add_infoproperties)


class ListTraktRandomisedProperties(ListTraktStandardProperties):

    @cached_property
    def limit(self):
        return self.length * 40  # Use double normal limit to get a decent sample size

    @cached_property
    def sample_limit(self):
        return min((self.length * 20), len(self.filtered_items))  # Make sure we dont try to sample more items than we have

    @cached_property
    def sorted_items(self):
        import random
        return random.sample(self.filtered_items, self.sample_limit)


class ListTraktStandard(ListStandard):

    list_properties_class = ListTraktStandardProperties

    def get_items(self, *args, length=None, tmdb_type=None, **kwargs):
        length = try_int(length) or PAGES_LENGTH

        if tmdb_type == 'both':  # Only used for randomised so combine randomised then resample
            import random
            items = super().get_items(*args, length=length, tmdb_type='movie', **kwargs) or []
            self.list_properties = self.configure_list_properties(self.list_properties_class())
            items += super().get_items(*args, length=length, tmdb_type='tv', **kwargs) or []
            items = random.sample(items, min((self.list_properties.length * 20), len(items)))
            self.plugin_category = self.list_properties.plugin_name.format(localized=self.list_properties.localized, plural=convert_type('both', 'plural'))
            self.container_content = convert_type('both', 'container', items=items)
            return items

        return super().get_items(*args, length=length, tmdb_type=tmdb_type, **kwargs)


class ListTraktFiltered(ListTraktStandard):
    def get_items(
        self, *args, length=None,
        genres=None,
        query=None,
        years=None,
        languages=None,
        countries=None,
        runtimes=None,
        studio_ids=None,
        certifications=None,
        network_ids=None,
        status=None,
        ratings=None,
        votes=None,
        tmdb_ratings=None,
        tmdb_votes=None,
        imdb_ratings=None,
        imdb_votes=None,
        rt_meters=None,
        rt_user_meters=None,
        metascores=None,
        **kwargs
    ):

        self.list_properties.trakt_filters = {
            k: v for k, v in (
                ('genres', genres),
                ('query', query),
                ('years', years),
                ('languages', languages),
                ('countries', countries),
                ('runtimes', runtimes),
                ('studio_ids', studio_ids),
                ('certifications', certifications),
                ('network_ids', network_ids),
                ('status', status),
                ('ratings', ratings),
                ('votes', votes),
                ('tmdb_ratings', tmdb_ratings),
                ('tmdb_votes', tmdb_votes),
                ('imdb_ratings', imdb_ratings),
                ('imdb_votes', imdb_votes),
                ('rt_meters', rt_meters),
                ('rt_user_meters', rt_user_meters),
                ('metascores', metascores),
            ) if k and v
        }

        return super().get_items(*args, length=try_int(length) or PAGES_LENGTH, **kwargs)


class ListTraktTrending(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/trending'
        list_properties.localize = 32204
        list_properties.sub_type = True
        return list_properties


class ListTraktTrendingRandomised(ListTraktTrending):
    list_properties_class = ListTraktRandomisedProperties
    pagination = False


class ListTraktPopular(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/popular'
        list_properties.localize = 32175
        list_properties.sub_type = False
        return list_properties


class ListTraktPopularRandomised(ListTraktPopular):
    list_properties_class = ListTraktRandomisedProperties
    pagination = False


class ListTraktMostPlayed(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/played/weekly'
        list_properties.localize = 32205
        list_properties.sub_type = True
        return list_properties


class ListTraktMostPlayedRandomised(ListTraktMostPlayed):
    list_properties_class = ListTraktRandomisedProperties
    pagination = False


class ListTraktMostWatched(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/watched/weekly'
        list_properties.localize = 32414
        list_properties.sub_type = True
        return list_properties


class ListTraktMostWatchedRandomised(ListTraktMostWatched):
    list_properties_class = ListTraktRandomisedProperties
    pagination = False


class ListTraktAnticipated(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/anticipated'
        list_properties.localize = 32206
        list_properties.sub_type = True
        return list_properties


class ListTraktAnticipatedRandomised(ListTraktAnticipated):
    list_properties_class = ListTraktRandomisedProperties
    pagination = False


class ListTraktBoxOffice(ListTraktStandard):  # Box Office doesn't support filters or pagination
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/boxoffice'
        list_properties.localize = 32207
        list_properties.sub_type = True
        return list_properties


class ListTraktRecommendations(ListTraktStandard):  # Box Office doesn't support filters or pagination
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.trakt_authorization = True
        list_properties.trakt_filters = {
            'ignore_collected': 'true',
            'ignore_watchlisted': 'true'
        }
        list_properties.request_url = 'recommendations/{trakt_type}s'
        list_properties.localize = 32198
        list_properties.sub_type = True
        return list_properties


class ListTraktMyCalendars(ListTraktFiltered):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.trakt_authorization = True
        list_properties.request_url = 'calendars/my/{trakt_type}s'
        list_properties.plugin_name = f'{get_localized(32201)} {{plural}} {{localized}}'
        list_properties.localize = 32202
        list_properties.sub_type = True
        return list_properties
