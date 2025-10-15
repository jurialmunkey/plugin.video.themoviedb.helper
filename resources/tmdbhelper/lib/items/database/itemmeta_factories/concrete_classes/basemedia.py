from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.mappings import ItemMapperMethods
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseclass import BaseItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseroutes import MediaItemInfoLabelItemRoutes
from tmdbhelper.lib.addon.plugin import get_setting


class MediaItemArtworkRoutes:

    def __init__(self, parent_type=None):
        self.parent_type = parent_type

    routes = {
        'fanart_tv_poster': {
            'affixes': (None, 'language', 'english', 'null'),
            'outputs': 'poster',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'ftv',
        },
        'fanart_tv_landscape': {
            'affixes': (None, 'language', 'english'),
            'outputs': 'landscape',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'ftv',
        },
        'fanart_tv_clearlogo': {
            'affixes': (None, 'language', 'english', 'null'),
            'outputs': 'clearlogo',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'ftv',
        },
        'fanart_tv_fanart': {
            'affixes': (None, ),
            'outputs': 'fanart',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'ftv',
        },
        'fanart_tv_clearart': {
            'affixes': (None, ),
            'outputs': 'clearart',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'ftv',
        },
        'fanart_tv_discart': {
            'affixes': (None, ),
            'outputs': 'discart',
            'parents': (None, ),
            'art_api': 'ftv',
        },
        'fanart_tv_banner': {
            'affixes': (None, ),
            'outputs': 'banner',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'ftv',
        },
        'art_poster': {
            'affixes': (None, 'language', 'english', 'null'),
            'outputs': 'poster',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'tmdb',
        },
        'art_landscape': {
            'affixes': (None, 'language', 'english'),
            'outputs': 'landscape',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'tmdb',
        },
        'art_clearlogo': {
            'affixes': (None, 'language', 'english', 'null'),
            'outputs': 'clearlogo',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'tmdb',
        },
        'art_fanart': {
            'affixes': (None, ),
            'outputs': 'fanart',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'tmdb',
        },
        'art_thumbs': {
            'affixes': (None, ),
            'outputs': 'thumb',
            'parents': (None, ),
            'art_api': 'tmdb',
        },
        'art_profile': {
            'affixes': (None, ),
            'outputs': 'thumb',
            'parents': (None, ),
            'art_api': 'tmdb',
        },
        'art_extrafanart': {
            'affixes': (None, ),
            'outputs': 'fanart',
            'parents': (None, ),
            'art_api': 'tmdb',
        },
        'user_art_poster': {
            'affixes': (None, ),
            'outputs': 'poster',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'user',
        },
        'user_art_landscape': {
            'affixes': (None, ),
            'outputs': 'landscape',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'user',
        },
        'user_art_clearlogo': {
            'affixes': (None, ),
            'outputs': 'clearlogo',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'user',
        },
        'user_art_fanart': {
            'affixes': (None, ),
            'outputs': 'fanart',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'user',
        },
        'user_art_thumb': {
            'affixes': (None, ),
            'outputs': 'thumb',
            'parents': (None, 'tvshow', 'season'),
            'art_api': 'user',
        },
    }

    def get_art_list(self, affix=None, allow_ftv=False, allow_tmdb=False, allow_user=False, no_affix=False):

        def get_art_tuple(route):
            definition = self.routes[route]
            if not allow_ftv and definition['art_api'] == 'ftv':
                return
            if not allow_tmdb and definition['art_api'] == 'tmdb':
                return
            if not allow_user and definition['art_api'] == 'user':
                return
            if no_affix and len(definition['affixes']) != 1:
                return
            if affix not in definition['affixes']:
                return
            if self.parent_type not in definition['parents']:
                return
            art_route = f'{route}_{affix}' if affix is not None else route
            return ((art_route, self.parent_type), definition['outputs'])

        return [
            i for i in (
                get_art_tuple(route)
                for route in self.routes.keys())
            if i]

    def get_art_list_language(self, allow_ftv=False, allow_tmdb=False):
        return self.get_art_list('language', allow_ftv=allow_ftv, allow_tmdb=allow_tmdb)

    def get_art_list_english(self, allow_ftv=False, allow_tmdb=False):
        return self.get_art_list('english', allow_ftv=allow_ftv, allow_tmdb=allow_tmdb)

    def get_art_list_null(self, allow_ftv=False, allow_tmdb=False):
        return self.get_art_list('null', allow_ftv=allow_ftv, allow_tmdb=allow_tmdb)

    def get_art_list_extra(self, allow_ftv=False, allow_tmdb=False):
        return self.get_art_list(None, allow_ftv=allow_ftv, allow_tmdb=allow_tmdb, no_affix=True)

    def get_art_list_tmdb_preferred(self, affix=None):
        return self.get_art_list(affix, allow_tmdb=True) + self.get_art_list(affix, allow_ftv=True)

    def get_art_list_ftv_preferred(self, affix=None):
        return self.get_art_list(affix, allow_ftv=True) + self.get_art_list(affix, allow_tmdb=True)

    def get_art_list_tmdb_language(self):
        return self.get_art_list_extra(allow_ftv=True, allow_tmdb=True) \
            + self.get_art_list_language(allow_tmdb=True) \
            + self.get_art_list_language(allow_ftv=True) \
            + self.get_art_list_english(allow_tmdb=True) \
            + self.get_art_list_english(allow_ftv=True) \
            + self.get_art_list_null(allow_tmdb=True) \
            + self.get_art_list_null(allow_ftv=True)

    def get_art_list_ftv_language(self):
        return self.get_art_list_extra(allow_ftv=True, allow_tmdb=True) \
            + self.get_art_list_language(allow_ftv=True) \
            + self.get_art_list_language(allow_tmdb=True) \
            + self.get_art_list_english(allow_ftv=True) \
            + self.get_art_list_english(allow_tmdb=True) \
            + self.get_art_list_null(allow_ftv=True) \
            + self.get_art_list_null(allow_tmdb=True)

    @property
    def base_configured_routes(self):
        if not get_setting('fanarttv_lookup'):
            return self.get_art_list(allow_tmdb=True)
        if not get_setting('language_lookup'):
            if get_setting('fanarttv_prefer'):
                return self.get_art_list_ftv_preferred()
            return self.get_art_list_tmdb_preferred()
        if not get_setting('fanarttv_prefer'):
            return self.get_art_list_tmdb_language()
        return self.get_art_list_ftv_language()

    @property
    def user_configured_routes(self):
        return self.get_art_list(allow_user=True)

    @property
    def configured_routes(self):
        return self.user_configured_routes + self.base_configured_routes


class MediaItem(BaseItem):

    @property
    def art_dbclist_routes(self):
        return MediaItemArtworkRoutes().configured_routes

    infolabels_dbclist_routes = (
        (('genre', None), 'name', 'genre'),
        (('country', None), 'name', 'country'),
        (('director', None), 'name', 'director'),
        (('writer', None), 'name', 'writer'),
    )

    infolabels_dbcitem_routes = (
        MediaItemInfoLabelItemRoutes.certification,
        MediaItemInfoLabelItemRoutes.trailer,
    )

    """
    instance: tuple of (attr, subtype) to retrieve self.db_{attr}_{subtype}_cache
    mappings: dictionary of {property_name: database_key} to map list as ListItem.Property({property_prefix}.{x}.{property_name}) = database[database_key]
    propname: tuple of property_prefix(es) to add values to (used mostly for backwards compatibility where multiple props reference same data)
    joinings: optional tuple of (property_name, dictionary_key) to map slash separated and [CR] separated properties as ListItem.Property(name), ListItem.Property(name_CR) e.g. 'Action / Adventure' 'Action[CR]Adventure'
    """
    infoproperties_dbclist_routes = (
        {
            'instance': ('genre', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id'},
            'propname': ('genre', ),
            'joinings': None
        },
        {
            'instance': ('country', None),
            'mappings': {'name': 'name', 'iso_country': 'iso_country'},
            'propname': ('country', ),
            'joinings': None
        },
        {
            'instance': ('studio', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'icon': 'logo', 'country': 'country'},
            'propname': ('studio', ),
            'joinings': None
        },
        {
            'instance': ('provider', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'type': 'availability', 'icon': 'logo'},
            'propname': ('provider', ),
            'joinings': ('providers', 'name')
        },
        {
            'instance': ('castmember', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'role': 'role', 'character': 'role', 'thumb': 'thumb'},
            'propname': ('cast', ),
            'joinings': ('cast', 'name')
        },
        {
            'instance': ('crewmember', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('crew', ),
            'joinings': ('crew', 'name')
        },
        {
            'instance': ('creator', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('creator', ),
            'joinings': ('creator', 'name')
        },
        {
            'instance': ('director', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('director', ),
            'joinings': ('director', 'name')
        },
        {
            'instance': ('writer', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('writer', ),
            'joinings': ('writer', 'name')
        },
        {
            'instance': ('screenplay', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('screenplay', ),
            'joinings': ('screenplay', 'name')
        },
        {
            'instance': ('producer', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('producer', ),
            'joinings': ('producer', 'name')
        },
        {
            'instance': ('sound_department', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('sound_department', ),
            'joinings': ('sound_department', 'name')
        },
        {
            'instance': ('art_department', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('art_department', ),
            'joinings': ('art_department', 'name')
        },
        {
            'instance': ('photography', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('photography', ),
            'joinings': ('photography', 'name')
        },
        {
            'instance': ('editor', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'department': 'department', 'role': 'role', 'job': 'role', 'thumb': 'thumb'},
            'propname': ('editor', ),
            'joinings': ('editor', 'name')
        },
    )

    def get_infoproperties_custom(self, infoproperties, subtype=None):
        for i in self.return_basemeta_db('custom', subtype).cached_data:
            infoproperties[self.get_subtype_key(i['key'], subtype)] = i['value']
        return infoproperties

    def get_infoproperties_translation(self, infoproperties, subtype=None):

        generator = (
            (
                f"{i['iso_language']}_{subtype or ''}{k}",
                f"{i['iso_language']}-{i['iso_country']}_{subtype or ''}{k}",
                i[k]
            )
            for i in self.return_basemeta_db('translation', subtype).cached_data
            for k in ('title', 'plot', 'tagline')
            if i[k]
        )

        for key_language, key_combined, value in generator:
            infoproperties[key_combined] = value
            infoproperties[key_language] = infoproperties.get(key_language) or value

        return infoproperties

    def get_infoproperties_progress(self, infoproperties):
        duration = self.get_data_value('duration')
        if not duration:
            return infoproperties

        progress = self.get_instance_cached_data_value(self.return_basemeta_db('playprogress'), 'playback_progress')
        if not progress or progress < 4 or progress > 96:
            progress = 0

        infoproperties['ResumeTime'] = int(duration * progress // 100)
        infoproperties['TotalTime'] = int(duration)
        return infoproperties

    def get_infoproperties_lastplayed(self, infoproperties):
        func_get = self.get_instance_cached_data_value
        func_dbc = self.return_basemeta_db
        lastplayed_timestamp = func_get(func_dbc('lastplayed'), 'lastplayed')
        if not lastplayed_timestamp:
            return infoproperties
        infoproperties.update(ItemMapperMethods.get_custom_date(
            lastplayed_timestamp, name='lastplayed'
        ))
        return infoproperties

    def get_infoproperties_ranks(self, infoproperties):
        func_get = self.get_instance_cached_data_value
        func_dbc = self.return_basemeta_db

        for database, column, name, func in (
            ('favorites_rank', 'favorites_rank', 'favorites_rank', None),
            ('watchlist_rank', 'watchlist_rank', 'watchlist_rank', None),
            ('collected_date', 'collection_last_collected_at', 'collected_date', lambda i: i[:10]),
        ):
            rank = func_get(func_dbc(database), column)
            if not rank:
                continue
            infoproperties[name] = func(rank) if func else rank

        return infoproperties

    def get_infoproperties_next_ep(self, infoproperties):

        try:
            for column in ('next_aired', 'last_aired'):

                episode_id = self.get_data_value(f'{column}_id')

                if not episode_id:
                    continue

                for affix in (
                    'id', 'episode', 'year', 'premiered', 'duration',
                    'rating', 'votes', 'popularity', 'title', 'plot'
                ):
                    infoproperties[f'{column}.{affix}'] = self.get_data_value(f'{column}_{affix}')

                id_split = episode_id.split('.')

                infoproperties.update({
                    f'{column}.tmdb_type': id_split[0],
                    f'{column}.tmdb_id': id_split[1],
                    f'{column}.season': id_split[2],
                    f'{column}.episode': id_split[3],
                })

                infoproperties.update(
                    ItemMapperMethods.get_custom_date(
                        self.get_data_value(f'{column}_premiered'), name=column
                    )
                )

                infoproperties.update(
                    ItemMapperMethods.get_custom_time(
                        self.get_data_value(f'{column}_duration'), name='duration'))

        except (TypeError, KeyError, IndexError):
            pass

        return infoproperties

    def get_unique_ids(self, unique_ids, subtype=None):
        for i in (self.return_basemeta_db('unique_id', subtype).cached_data or ()):
            unique_ids[self.get_subtype_key(i['key'], subtype)] = i['value']
        unique_ids[self.get_subtype_key('tmdb', subtype)] = self.parent_db_cache.tmdb_id
        return unique_ids

    @cached_property
    def cast(self):
        return [
            {
                'name': i['name'],
                'role': i['role'],
                'order': i['ordering'] or 999999,
                'thumbnail': self.parent_db_cache.common_apis.tmdb_imagepath.get_imagepath_poster(i['thumb'])
            }
            for i in self.return_basemeta_db('castmember').cached_data
        ]
