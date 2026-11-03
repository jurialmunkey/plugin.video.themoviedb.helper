from jurialmunkey.ftools import cached_property


class PlayerDetails:

    def __init__(
            self, tmdb_type, tmdb_id, season=None, episode=None, translation=False, provider_ids=False):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        self.translation = translation
        self.provider_ids = provider_ids

    @cached_property
    def lidc(self):
        return self.get_lidc()

    def get_lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        lidc = ListItemDetails()
        lidc.cache_refresh = None
        lidc.cache_translations = bool(self.translation)
        lidc.extendedinfo = True
        return lidc

    @cached_property
    def details(self):
        return self.get_enriched_details()

    def get_enriched_details(self):
        details = self.get_details()
        if details is None:
            return
        details.set_details(details=self.external_ids)
        return details

    def get_details(self, language=None):
        from tmdbhelper.lib.items.listitem import ListItem
        details = self.lidc.get_item(self.tmdb_type, self.tmdb_id, self.season, self.episode)
        return ListItem(**details) if details else None

    @cached_property
    def find_queries_db(self):
        return self.get_find_queries_db()

    def get_find_queries_db(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    @cached_property
    def external_ids(self):
        return self.get_external_ids()

    def get_external_ids(self):
        return {'unique_ids': self.get_unique_ids()}

    def get_unique_ids(self):
        tmdb_ids = self.get_tmdb_ids()
        return {**self.get_provider_ids(), **tmdb_ids}

    def get_provider_ids(self):
        if not self.provider_ids:
            return {}
        from tmdbhelper.lib.sync.providers.identifiers import IdentifierResolvers
        return IdentifierResolvers().get_ids(self.tmdb_type, self.tmdb_id, self.season, self.episode)

    @cached_property
    def root_ids(self):
        return self.get_root_ids()

    def get_root_ids(self):
        return dict(
            self.find_queries_db.get_external_ids(self.tmdb_type, self.tmdb_id),
            tmdb=self.tmdb_id)

    def get_tmdb_ids(self):
        if self.tmdb_type == 'movie':
            return self.root_ids
        return {**self.get_tvshow_ids(), **self.get_tv_item_ids()}

    def get_tvshow_ids(self):
        return {f'tvshow.{key}': value for key, value in self.root_ids.items()}

    def get_tv_item_ids(self):
        if self.season is None:
            return self.root_ids
        if self.episode is None:
            return {}
        return self.find_queries_db.get_external_ids(
            self.tmdb_type, self.tmdb_id, self.season, self.episode)
