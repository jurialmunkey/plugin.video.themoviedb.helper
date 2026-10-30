"""Build or update awards from TVDB and resolve new items through TMDB."""
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from tmdbhelper.lib.awards.database import AwardsDatabaseWriter, DATABASE_PATH
from tmdbhelper.lib.awards.matching import TMDbCandidateMatcher, TMDbMatch
import os
import sqlite3


class AwardsBuilder:
    def __init__(self, tvdb_api, tmdb_api, progress=print, workers=8):
        self.tvdb_api = tvdb_api
        self.tmdb_api = tmdb_api
        self.progress = progress
        self.workers = workers

    def get_categories(self):
        awards = self.tvdb_api.get_data('awards')
        if not awards:
            raise ValueError('TVDB returned no awards')
        for award in awards:
            self.progress(f'Getting categories: {award["name"]}')
            record = self.tvdb_api.get_data(f'awards/{award["id"]}/extended')
            yield from record['categories']

    def add_category(self, writer, category, position):
        self.progress(f'Getting nominees: {category["name"]}')
        record = self.tvdb_api.get_data(f'awards/categories/{category["id"]}/extended')
        writer.set_category(record, position)
        for index, nominee in enumerate(record['nominees']):
            self.add_nominee(writer, record['id'], nominee, index)
        writer.remove_missing_nominations(record['id'])

    @staticmethod
    def add_nominee(writer, category_id, nominee, position):
        if nominee.get('movie'):
            tmdb_type, item = 'movie', nominee['movie']
        elif nominee.get('series'):
            tmdb_type, item = 'tv', nominee['series']
        else:
            return  # Person/character-only nominations have no movie or series.
        writer.set_item(tmdb_type, item)
        writer.set_nomination(category_id, position, tmdb_type, item['id'], nominee)

    def resolve_items(self, writer):
        items = writer.get_unmatched_items()
        self.progress(f'Matching {len(items)} new or unresolved items')
        unmatched = []
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            matches = executor.map(self.get_item_match, items)
            for index, (item, match) in enumerate(matches, 1):
                tmdb_type, tvdb_id, name, year = item
                writer.set_match(tmdb_type, tvdb_id, match)
                result = f'{match.tmdb_id} ({match.method})' if match.tmdb_id else f'UNMATCHED ({match.reason})'
                self.progress(f'Matching {index}/{len(items)}: {tmdb_type} {name}: {result}')
                if match.tmdb_id is None:
                    unmatched.append({'tmdb_type': tmdb_type, 'tvdb_id': tvdb_id, 'name': name, 'year': year})
        return unmatched

    def get_item_match(self, item):
        tmdb_id = self.tmdb_api.get_tmdb_id(*item)
        if tmdb_id:
            return item, TMDbMatch(tmdb_id, 'initial_lookup')
        details = self.tvdb_api.get_item_details(item[0], item[1])
        if details is None:
            return item, TMDbMatch(reason='tvdb_item_missing')
        match = self.get_external_match(item[0], details)
        if match.tmdb_id or match.is_ambiguous:
            return item, match
        return item, self.get_title_match(item, details)

    def get_external_match(self, tmdb_type, details):
        remote_ids = details.get('remoteIds') or []
        # TVDB can retain TMDB's optional website title slug after the ID.
        identifiers = {
            int(remote['id'].partition('-')[0]) for remote in remote_ids
            if remote['sourceName'].casefold() == 'themoviedb.com'}
        matched = {
            identifier for identifier in identifiers
            if self.tmdb_api.get_item_details(tmdb_type, identifier) is not None}
        if len(matched) > 1:
            return TMDbMatch(reason='ambiguous_tmdb_identifiers')
        if matched:
            return TMDbMatch(matched.pop(), 'tvdb_tmdb_identifier')
        imdb_ids = {remote['id'] for remote in remote_ids if remote['sourceName'].casefold() == 'imdb'}
        matched = set().union(*(self.tmdb_api.find_ids(tmdb_type, identifier, 'imdb_id') for identifier in imdb_ids))
        if len(matched) > 1:
            return TMDbMatch(reason='ambiguous_imdb_identifiers')
        if matched:
            return TMDbMatch(matched.pop(), 'tvdb_imdb_identifier')
        return TMDbMatch(reason='no_external_match')

    def get_title_match(self, item, details):
        tmdb_type, tvdb_id, name, year = item
        source_names = (
            value for value in (name, details['name'], *(alias['name'] for alias in details.get('aliases') or []))
            if value)
        names = tuple(dict.fromkeys(
            query for value in source_names for query in (value, TMDbCandidateMatcher.get_search_name(value))))
        matcher = TMDbCandidateMatcher(tmdb_type, names, year)
        candidates = (
            candidate for query in names for candidate in self.tmdb_api.search_items(tmdb_type, query, year))
        match = matcher.get_match(candidates)
        if match.tmdb_id or match.is_ambiguous or not year:
            return match
        candidates = (candidate for query in names for candidate in self.tmdb_api.search_items(tmdb_type, query))
        return matcher.get_match(candidates, year_tolerance=1)

    def populate(self, writer):
        writer.prepare_refresh()
        with writer.connection:
            for position, category in enumerate(self.get_categories()):
                self.add_category(writer, category, position)
            writer.remove_missing_categories()
            unmatched = self.resolve_items(writer)
            counts = writer.set_metadata(datetime.now(timezone.utc).isoformat())
        writer.validate()
        self.progress(f'Updated {counts[0]} matched items, {counts[1]} unmatched items, {counts[2]} nominations')
        return unmatched

    def initialise_database(self, connection, filename):
        writer = AwardsDatabaseWriter(connection)
        writer.create()
        return writer

    def run(self, filename=DATABASE_PATH):
        filename = Path(filename).resolve()
        filename.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(prefix='awards-', suffix='.db', dir=filename.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
        try:
            with closing(sqlite3.connect(temporary_path)) as connection:
                writer = self.initialise_database(connection, filename)
                unmatched = self.populate(writer)
            os.replace(temporary_path, filename)
        finally:
            temporary_path.unlink(missing_ok=True)
        return unmatched


class AwardsUpdater(AwardsBuilder):
    def initialise_database(self, connection, filename):
        with closing(sqlite3.connect(f'{filename.as_uri()}?mode=ro', uri=True)) as source:
            source.backup(connection)
        writer = AwardsDatabaseWriter(connection)
        writer.upgrade()
        return writer
