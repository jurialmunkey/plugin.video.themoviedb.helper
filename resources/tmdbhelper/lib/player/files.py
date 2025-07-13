from json import loads
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.files.futils import get_files_in_folder, read_file
from tmdbhelper.lib.addon.plugin import get_setting, get_condvisibility
from tmdbhelper.lib.addon.consts import (
    PLAYERS_BASEDIR_BUNDLED,
    PLAYERS_BASEDIR_USER,
    PLAYERS_BASEDIR_SAVE,
)


class PlayerFileMetaData:

    lookup_required_ids = (
        '{imdb}',
        '{tvdb}',
        '{trakt}',
        '{slug}',
        '{eptvdb}',
        '{epimdb}',
        '{eptrakt}',
        '{epslug}',
        '{epid}'
    )

    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename

    @cached_property
    def filenameandpath(self):
        return self.folder + self.filename

    @cached_property
    def data(self):
        return read_file(self.filenameandpath)

    @cached_property
    def meta(self):
        return loads(self.data) or {}

    @cached_property
    def plugins(self):
        plugins = self.meta.get('plugin') or 'plugin.undefined'  # Give dummy name to undefined plugins so that they fail the check
        plugins = plugins if isinstance(plugins, list) else [plugins]  # Listify for simplicity of code
        return plugins

    @cached_property
    def is_enabled(self):
        return all((
            get_condvisibility(f'System.AddonIsEnabled({i})')
            for i in self.plugins
        ))

    @cached_property
    def require_id(self):
        return any((
            bool(i in self.data)
            for i in self.lookup_required_ids
        ))

    @cached_property
    def metadata(self):
        metadata = self.meta.copy()
        metadata.update({
            k: v for k, v in (
                ('requires_ids', self.require_id),
                ('plugin', self.plugins[0]),
            ) if v
        })
        return metadata


class PlayerFiles:

    basedir_user = PLAYERS_BASEDIR_USER
    basedir_save = PLAYERS_BASEDIR_SAVE

    @cached_property
    def basedir_bundled(self):
        if not get_setting('bundled_players'):
            return
        return PLAYERS_BASEDIR_BUNDLED

    @cached_property
    def basedirs(self):
        basedirs = [i for i in (
            self.basedir_user,
            self.basedir_bundled,
            self.basedir_save,
        ) if i]
        return basedirs

    @cached_property
    def player_file_metadata_list(self):
        player_file_metadata_list = [
            PlayerFileMetaData(folder, filename)
            for folder in self.basedirs
            for filename in get_files_in_folder(folder, r'.*\.json')
        ]
        return player_file_metadata_list

    @cached_property
    def dictionary(self):
        return {
            i.filename: i.metadata
            for i in self.player_file_metadata_list
            if i.is_enabled
        }
