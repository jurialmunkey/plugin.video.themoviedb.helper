from json import loads
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import boolean
from tmdbhelper.lib.files.futils import read_file
from tmdbhelper.lib.addon.plugin import get_condvisibility
from tmdbhelper.lib.addon.consts import PLAYERS_PRIORITY


class PlayerMeta:

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

    def __init__(self, folder, filename, providers=None, show_disabled=False):
        self.folder = folder
        self.filename = filename
        self.providers = providers
        self.show_disabled = show_disabled

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
        if self.is_disabled:
            return False
        return all((
            get_condvisibility(f'System.AddonIsEnabled({i})')
            for i in self.plugins
        ))

    @cached_property
    def is_disabled(self):
        if self.show_disabled:
            return False
        return boolean(self.meta.get('disabled'))

    @cached_property
    def requires_translation(self):
        return boolean(self.meta.get('language'))

    @cached_property
    def requires_ids(self):
        return any((
            bool(i in self.data)
            for i in self.required_ids
        ))

    @cached_property
    def priority_provider(self):
        try:
            priority = self.providers.index(self.meta['provider'])
            priority += 1  # Add 1 to avoid 0 index for sorting
            priority += self.priority_baseline / 100000  # If 2+ providers with same index we order by baseline priority at fractions
            return priority
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
