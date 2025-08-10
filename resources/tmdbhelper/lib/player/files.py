from json import loads
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.files.futils import get_files_in_folder, read_file
from tmdbhelper.lib.addon.plugin import get_setting, get_condvisibility
from tmdbhelper.lib.addon.consts import (
    PLAYERS_BASEDIR_BUNDLED,
    PLAYERS_BASEDIR_USER,
    PLAYERS_BASEDIR_SAVE,
    PLAYERS_PRIORITY
)


class PlayerFileMetaData:

    required_ids = (
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

    def __init__(self, folder, filename, providers=None):
        self.folder = folder
        self.filename = filename
        self.providers = providers

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
    def plugin(self):
        return self.plugins[0]

    @cached_property
    def is_enabled(self):
        return all((
            get_condvisibility(f'System.AddonIsEnabled({i})')
            for i in self.plugins
        ))

    @cached_property
    def requires_ids(self):
        return any((
            bool(i in self.data)
            for i in self.required_ids
        ))

    @cached_property
    def priority_provider(self):
        try:
            return self.providers.index(self.meta['provider']) + 1  # Add 1 to avoid 0 index for sorting
        except (KeyError, ValueError, TypeError, AttributeError):
            return 0

    @cached_property
    def priority_baseline(self):
        try:
            priority = int(self.meta['priority'])
        except (KeyError, TypeError):
            priority = None
        return priority or PLAYERS_PRIORITY

    @cached_property
    def priority_standard(self):
        return self.priority_baseline + 100  # Adjustment to put after providers

    @cached_property
    def priority(self):
        return self.priority_provider or self.priority_standard

    @cached_property
    def metadata(self):
        metadata = self.meta.copy()
        metadata.update({
            k: v for k, v in (
                ('requires_ids', self.requires_ids),
                ('plugin', self.plugin),
                ('priority', self.priority),
                ('is_provider', self.priority_provider),
            ) if v
        })
        return metadata


class PlayerFiles:

    basedir_user = PLAYERS_BASEDIR_USER
    basedir_save = PLAYERS_BASEDIR_SAVE

    def __init__(self, providers=None):
        self.providers = providers

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
    def player_file_and_path_list(self):
        player_file_metadata_list = {
            filename: folder
            for folder in self.basedirs
            for filename in get_files_in_folder(folder, r'.*\.json')
        }
        return player_file_metadata_list

    @cached_property
    def player_file_metadata_list(self):
        player_file_metadata_list = [
            PlayerFileMetaData(folder, filename, self.providers)
            for filename, folder in self.player_file_and_path_list.items()
        ]
        return player_file_metadata_list

    @cached_property
    def dictionary(self):
        return {
            i.filename: i.metadata
            for i in self.player_file_metadata_list
            if i.is_enabled
        }

    @cached_property
    def prioritise(self):
        return [
            (i.filename, i.metadata)
            for i in sorted(self.player_file_metadata_list, key=lambda x: (x.priority, x.plugin))
            if i.is_enabled
        ]
