#!/usr/bin/env python3
"""Run with: python scripts/build_awards.py (Kodi is not required)."""
from pathlib import Path
import sqlite3
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'resources'))

from tmdbhelper.lib.awards.builder import AwardsBuilder, AwardsUpdater
from tmdbhelper.lib.awards.client import AwardsAPIError, TMDbClient, TVDbClient
from tmdbhelper.lib.awards.credentials import AddonCredentials
from tmdbhelper.lib.awards.database import DATABASE_PATH


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        credentials = AddonCredentials()
        tvdb_api = TVDbClient(credentials.get_api_key('tvdb'))
        tmdb_api = TMDbClient(credentials.get_api_key('tmdb'))
        builder_class = AwardsUpdater if DATABASE_PATH.exists() else AwardsBuilder
        builder_class(tvdb_api, tmdb_api).run()
    except (AwardsAPIError, OSError, sqlite3.Error, ValueError, KeyError, TypeError) as error:
        sys.exit(f'Build failed: {error}')


if __name__ == '__main__':
    main()
