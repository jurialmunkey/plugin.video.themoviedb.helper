"""Conservative title matching for awards items without external ID matches."""
from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class TMDbMatch:
    tmdb_id: int = None
    method: str = ''
    reason: str = ''

    @property
    def is_ambiguous(self):
        return self.reason.startswith('ambiguous_')


class TMDbCandidateMatcher:
    def __init__(self, tmdb_type, names, year):
        self.tmdb_type = tmdb_type
        self.year = int(year) if year else None
        self.names = frozenset(self.normalise_name(name) for name in names)

    @property
    def title_keys(self):
        return ('title', 'original_title') if self.tmdb_type == 'movie' else ('name', 'original_name')

    @property
    def date_key(self):
        return 'release_date' if self.tmdb_type == 'movie' else 'first_air_date'

    @staticmethod
    def get_search_name(name):
        return re.sub(r'\s+\(\d{4}\)\s*$', '', name).strip()

    @staticmethod
    def normalise_name(name):
        name = unicodedata.normalize('NFKC', TMDbCandidateMatcher.get_search_name(name)).casefold()
        return ' '.join(''.join(character if character.isalnum() else ' ' for character in name).split())

    def has_matching_title(self, candidate):
        return any(
            self.normalise_name(candidate[key]) in self.names
            for key in self.title_keys if candidate.get(key))

    def get_year_difference(self, candidate):
        if self.year is None:
            return 0
        date = candidate.get(self.date_key)
        return abs(int(date[:4]) - self.year) if date else None

    def get_match(self, candidates, year_tolerance=0):
        titles = {candidate['id']: candidate for candidate in candidates if self.has_matching_title(candidate)}
        if not titles:
            return TMDbMatch(reason='no_matching_title')
        differences = {identifier: self.get_year_difference(candidate) for identifier, candidate in titles.items()}
        identifiers = [identifier for identifier, difference in differences.items() if difference == 0]
        method = 'normalised_title'
        if not identifiers and year_tolerance:
            identifiers = [
                identifier for identifier, difference in differences.items()
                if difference is not None and difference <= year_tolerance]
            method = 'normalised_title_nearby_year'
        if len(identifiers) > 1:
            return TMDbMatch(reason='ambiguous_title_matches')
        if identifiers:
            return TMDbMatch(identifiers[0], method)
        return TMDbMatch(reason='title_year_mismatch')
