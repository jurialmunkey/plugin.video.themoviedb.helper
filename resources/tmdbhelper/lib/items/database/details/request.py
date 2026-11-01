from tmdbhelper.lib.addon.plugin import convert_type, get_language


ITEM_TYPES = (
    'movie', 'tvshow', 'season', 'episode', 'person', 'set',
    'episode_group', 'episode_group_season',
)

CACHE_REFRESH_LEVELS = (None, 'basic', 'never', 'force')


class DetailsRequest:
    """Immutable item detail request.

    A plain class rather than a frozen dataclass: importing dataclasses (and inspect)
    costs every plugin invocation, and only this class needs it.
    """

    fields = (
        'mediatype', 'tmdb_id', 'season', 'episode', 'tvshow_tmdb_id', 'cache_refresh',
        'cache_translations', 'extendedinfo', 'language', 'clear_user_art', 'sync_details',
    )

    def __init__(
            self, mediatype, tmdb_id, season=None, episode=None, tvshow_tmdb_id=None,
            cache_refresh=None, cache_translations=False, extendedinfo=False, language='',
            clear_user_art=False, sync_details=True):
        if mediatype not in ITEM_TYPES:
            raise ValueError(f'Unsupported item detail type: {mediatype}')
        if cache_refresh not in CACHE_REFRESH_LEVELS:
            raise ValueError(f'Unsupported cache refresh level: {cache_refresh}')
        self.set_field('mediatype', mediatype)
        self.set_field('tmdb_id', self.get_identifier(mediatype, tmdb_id))
        self.set_field('season', self.get_optional_int(season))
        self.set_field('episode', self.get_optional_int(episode))
        self.set_field('tvshow_tmdb_id', self.get_optional_int(tvshow_tmdb_id))
        self.set_field('cache_refresh', cache_refresh)
        self.set_field('cache_translations', cache_translations)
        self.set_field('extendedinfo', extendedinfo)
        self.set_field('language', language or get_language())
        self.set_field('clear_user_art', clear_user_art)
        self.set_field('sync_details', sync_details)  # Permit synced play data; the service applies the user's setting

    def set_field(self, name, value):
        object.__setattr__(self, name, value)

    def __setattr__(self, name, value):
        raise AttributeError(f'cannot assign to field {name!r}')

    def __delattr__(self, name):
        raise AttributeError(f'cannot delete field {name!r}')

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.as_tuple() == other.as_tuple()

    def __hash__(self):
        return hash(self.as_tuple())

    def __repr__(self):
        values = ', '.join(f'{name}={getattr(self, name)!r}' for name in self.fields)
        return f'{self.__class__.__name__}({values})'

    @staticmethod
    def get_identifier(mediatype, tmdb_id):
        if mediatype in ('episode_group', 'episode_group_season'):
            return str(tmdb_id)
        return int(tmdb_id)

    @staticmethod
    def get_optional_int(value):
        """Empty values are unset; factory data conditions reject unset numbers."""
        if value in (None, ''):
            return
        return int(value)

    @classmethod
    def from_type(cls, tmdb_type, tmdb_id, season=None, episode=None, **kwargs):
        return cls(
            mediatype=convert_type(tmdb_type, 'dbtype', season, episode),
            tmdb_id=tmdb_id, season=season, episode=episode, **kwargs)

    @property
    def identity(self):
        return (
            self.mediatype, self.tmdb_id, self.season, self.episode,
            self.tvshow_tmdb_id, self.language,
        )

    def get_dependency(self, mediatype, **kwargs):
        changes = dict(mediatype=mediatype, extendedinfo=False, clear_user_art=False, **kwargs)
        return self.__class__(**{**self.as_dict(), **changes})

    def as_tuple(self):
        return tuple(getattr(self, name) for name in self.fields)

    def as_dict(self):
        return dict(self.__dict__)
