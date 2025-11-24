from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.builder.media import LibraryBuilderMedia


class LibraryBuilderTvshows(LibraryBuilderMedia):

    tmdb_type = 'tv'

    @cached_property
    def library_item_class(self):
        from tmdbhelper.lib.update.items.tvshow import LibraryTvshow
        return LibraryTvshow

    def create(self, tmdb_id, **kwargs):
        return self.add_library_item_tvshow(self.get_library_item(tmdb_id))

    def add_library_item_tvshow(self, tvshow):
        if self.add_library_item(tvshow, tvshow.log_check):
            return
        if self.add_library_item(tvshow, tvshow.log_error):
            return
        self.add_library_item_seasons(tvshow)
        tvshow.cache.set_cache()  # Store details about what we did into the cache

    def add_library_item_seasons(self, tvshow):
        from tmdbhelper.lib.addon.plugin import get_localized
        total = len(tvshow.seasons)
        for count, season in enumerate(tvshow.seasons):
            message = f'{get_localized(32167)} {tvshow.name} - {get_localized(20373)} {season.season}...'
            self.dialog_msg(count, total, message=message)  # Update our progress dialog
            self.add_library_item_episodes(season)

    def add_library_item_episodes(self, season):
        total = len(season.episodes)
        for count, episode in enumerate(season.episodes, 1):
            self.set_library_item(episode)
            self.dialog_msg(count, total)
