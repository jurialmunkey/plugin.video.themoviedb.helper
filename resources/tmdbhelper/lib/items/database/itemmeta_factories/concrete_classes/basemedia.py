from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseclass import BaseItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseroutes import MediaItemInfoLabelItemRoutes
from tmdbhelper.lib.addon.plugin import get_setting


class MediaItemArtworkRoutes:
    art_dbclist_routes_fanart_tv = (
        (('fanart_tv_poster', None), 'poster'),
        (('fanart_tv_fanart', None), 'fanart'),
        (('fanart_tv_landscape', None), 'landscape'),
        (('fanart_tv_clearlogo', None), 'clearlogo'),
        (('fanart_tv_clearart', None), 'clearart'),
        (('fanart_tv_banner', None), 'banner'),
        (('fanart_tv_discart', None), 'discart'),
    )

    art_dbclist_routes_tmdb = (
        (('art_poster', None), 'poster'),
        (('art_fanart', None), 'fanart'),
        (('art_landscape', None), 'landscape'),
        (('art_thumbs', None), 'thumb'),
        (('art_clearlogo', None), 'clearlogo'),
        (('art_extrafanart', None), 'fanart'),
    )


class MediaItem(BaseItem):

    @property
    def art_dbclist_routes(self):
        return (
            *MediaItemArtworkRoutes.art_dbclist_routes_tmdb,
        ) if not get_setting('fanarttv_lookup') else (
            *MediaItemArtworkRoutes.art_dbclist_routes_tmdb,
            *MediaItemArtworkRoutes.art_dbclist_routes_fanart_tv,
        ) if not get_setting('fanarttv_prefer') else (
            *MediaItemArtworkRoutes.art_dbclist_routes_fanart_tv,
            *MediaItemArtworkRoutes.art_dbclist_routes_tmdb,
        )

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

    def get_infoproperties_custom(self, infoproperties):
        for i in self.parent_db_cache.return_basemeta_db('custom').cached_data:
            infoproperties[i['key']] = i['value']
        return infoproperties

    def get_infoproperties_progress(self, infoproperties):
        duration = self.get_data_value('duration')
        if not duration:
            return infoproperties

        progress = self.get_instance_cached_data_value(self.parent_db_cache.return_basemeta_db('playprogress'), 'playback_progress')
        if not progress or progress < 4 or progress > 96:
            progress = 0

        infoproperties['ResumeTime'] = int(duration * progress // 100)
        infoproperties['TotalTime'] = int(duration)
        return infoproperties

    def get_unique_ids(self, unique_ids):
        for i in (self.parent_db_cache.return_basemeta_db('unique_id').cached_data or ()):
            unique_ids[i['key']] = i['value']
        unique_ids['tmdb'] = self.parent_db_cache.tmdb_id
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
            for i in self.parent_db_cache.return_basemeta_db('castmember').cached_data
        ]
