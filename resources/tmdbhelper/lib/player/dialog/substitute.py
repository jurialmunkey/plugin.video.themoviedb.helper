import re
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.player.dialog.dictionary import PlayerDictionary


class PlayerSubstitute:

    def __init__(self, item, substitutions):
        self.item = item
        self.substitutions = substitutions

    @cached_property
    def dictionary(self):
        return self.get_dictionary()

    def get_dictionary(self):
        dictionary = PlayerDictionary(
            tmdb_type=self.item.tmdb_type,
            tmdb_id=self.item.tmdb_id,
            season=self.item.get('season'),
            episode=self.item.get('episode'),
            details=self.item.details,
        )
        for key, substitution in self.substitutions.items():
            dictionary[key] = self.get_substitution(dictionary, substitution)
        return dictionary

    def get_substitution(self, dictionary, substitution):
        return re.sub(
            pattern=substitution['pattern'],
            repl=substitution['replacement'],
            string=dictionary.string_format_map(substitution['string']),
            count=int(substitution.get('count', 0)),
        )
