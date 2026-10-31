from dataclasses import dataclass, replace
from tmdbhelper.lib.addon.plugin import convert_type, get_language


ITEM_TYPES = (
    'movie', 'tvshow', 'season', 'episode', 'person', 'set',
    'episode_group', 'episode_group_season',
)


@dataclass(frozen=True)
class DetailsRequest:
    mediatype: str
    tmdb_id: object
    season: object = None
    episode: object = None
    tvshow_tmdb_id: object = None
    cache_refresh: object = None
    cache_translations: bool = False
    extendedinfo: bool = False
    language: str = ''
    clear_user_art: bool = False

    def __post_init__(self):
        if self.mediatype not in ITEM_TYPES:
            raise ValueError(f'Unsupported item detail type: {self.mediatype}')
        if self.cache_refresh not in (None, 'basic', 'never', 'force'):
            raise ValueError(f'Unsupported cache refresh level: {self.cache_refresh}')
        identifier = self.tmdb_id
        if self.mediatype not in ('episode_group', 'episode_group_season'):
            identifier = int(identifier)
        else:
            identifier = str(identifier)
        object.__setattr__(self, 'tmdb_id', identifier)
        object.__setattr__(self, 'language', self.language or get_language())
        for name in ('season', 'episode', 'tvshow_tmdb_id'):
            object.__setattr__(self, name, self.get_optional_int(getattr(self, name)))

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
        return replace(
            self, mediatype=mediatype, extendedinfo=False,
            clear_user_art=False, **kwargs)

    def as_dict(self):
        return dict(self.__dict__)
