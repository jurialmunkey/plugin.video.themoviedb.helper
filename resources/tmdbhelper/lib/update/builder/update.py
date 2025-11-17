from tmdbhelper.lib.addon.tmdate import get_current_date_time
from tmdbhelper.lib.addon.plugin import get_localized, set_setting
from tmdbhelper.lib.update.builder.tvshows import LibraryBuilderTvshows


class LibraryBuilderUpdate(LibraryBuilderTvshows):
    def create(self, **kwargs):
        f_dir = self.get_listdir_basedir(self.get_basedir('tvshows'))

        total = len(f_dir)
        for count, (tmdb_id, folder) in enumerate(f_dir):
            self.dialog_msg(count, total, message=f'{get_localized(32167)} {folder}...')
            self.add_library_item_tvshow(self.get_library_item(tmdb_id))

        set_setting('last_autoupdate', f'Last updated {get_current_date_time()}', 'str')
