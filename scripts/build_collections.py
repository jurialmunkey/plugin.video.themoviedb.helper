#!/usr/bin/env python3
"""Build/update the TMDb collection baseline without Kodi or extra packages."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import argparse
import sqlite3
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'resources'))

from tmdbhelper.lib.awards.credentials import AddonCredentials
from tmdbhelper.lib.collections.builder import CollectionBuilder
from tmdbhelper.lib.collections.client import CollectionAPIError, CollectionClient
from tmdbhelper.lib.collections.database import DATABASE_PATH


def positive_int(value):
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError('Must be greater than zero')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DATABASE_PATH)
    parser.add_argument(
        '--snapshot-date', type=date.fromisoformat,
        default=(datetime.now(timezone.utc) - timedelta(days=1)).date())
    parser.add_argument('--cache', type=Path, default=Path('.cache/collections/exports'))
    parser.add_argument('--workers', type=positive_int, default=8)
    parser.add_argument('--requests-per-second', type=positive_int, default=10)
    parser.add_argument(
        '--max-requests', type=positive_int,
        help='Stop at this number of detail HTTP attempts, including retries; resume on the next run')
    parser.add_argument(
        '--due-only', action='store_true',
        help='Refresh only due entries, after populating new collections; default refreshes the entire baseline')
    args = parser.parse_args()
    try:
        client = CollectionClient(
            AddonCredentials().get_api_key('tmdb'), args.cache,
            requests_per_second=args.requests_per_second, max_requests=args.max_requests)
        result = CollectionBuilder(client, workers=args.workers).run(args.snapshot_date, args.output, args.due_only)
    except (CollectionAPIError, OSError, sqlite3.Error, ValueError, KeyError, TypeError) as error:
        sys.exit(f'Collection build failed: {error}')
    return 0 if result['published'] else 2


if __name__ == '__main__':
    sys.exit(main())
