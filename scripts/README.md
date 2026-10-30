# Updating awards

Run from the plugin's repository root with Python 3.8 or later. Kodi does not
need to be running. No additional Python packages are required.

```sh
python scripts/build_awards.py
```

The script retrieves awards, categories, and nominations from TheTVDB and updates
`resources/databases/awards.db`. If the database is absent, it builds one.

It reads TMDbHelper's existing API key definitions without importing
Kodi modules. It supports the current literal TMDB key and encoded TVDB key
definitions; a changed definition must be supported explicitly. Credentials are
never printed or stored in the generated database.

Existing TMDB mappings are preserved. Only new or unresolved items are matched,
using this sequence:

1. The original TVDB ID/title/year lookup.
2. Explicit TMDB identifiers from the item's TVDB extended record, checked against
   the corresponding TMDB movie or TV endpoint. Optional website title slugs are
   removed from these identifiers.
3. IMDb identifiers from that record, resolved through TMDB.
4. English or original titles matching TVDB's name or aliases after Unicode,
   punctuation, whitespace, and trailing year-suffix normalization.
5. A search without a year filter, accepting a unique matching title within one
   year of the TVDB release year. Exact-year matches take precedence.

Fallback searches examine all result pages. Conflicting external identifiers or
multiple qualifying title candidates remain unresolved. Missing release dates
cannot satisfy a known TVDB year. Unmatched items retain their nominations with
a null TMDB ID; `item.match_method` and `item.match_reason` record the result.
Kodi only retrieves matched items. Nominations referring only to people or
characters have no movie/series and are excluded.

Updates preserve TVDB award, category, and nomination IDs. They insert new records,
apply changed names/years/win status, and remove nominations or categories no
longer present in the refreshed source. Items with no remaining nominations are
removed. Repeated updates do not append duplicate nominations.

Each run currently fetches all category snapshots. It updates existing records
and reuses known TMDB mappings; it does not rebuild the whole database or repeat
every TMDB lookup. The TVDB change feed identifies changed nominations but does
not identify the category for newly created nomination IDs, so using that feed
alone would not provide a complete refresh.

The first update of a version 1 database refreshes its nomination data once to
acquire TVDB source IDs, retaining existing item mappings. Subsequent version 2
updates modify records by their source identifiers.

TMDB matching uses eight workers. SQLite writes stay on the main thread and
preserve source order.

The build logs progress and retries temporary connection, rate-limit, and server
errors. A missing TVDB/TMDB detail record can fall through to an unresolved result
or the next matching method. Other invalid API data or permanent failures abort
the update. Updates work on a temporary SQLite backup beside the destination,
check integrity and foreign keys, then atomically replace the destination.
An interrupted or failed update leaves the previous database intact.

The database contains `item`, `category`, `nomination`, and `metadata` tables. It retains
separate movie/TV identifiers, award/category names, award years, win status,
and source ordering. `metadata` records the UTC build/update times and counts;
`PRAGMA user_version` identifies the schema version. Multiple TVDB records
matching the same TMDB item contribute all their nominations.

Kodi opens this bundled database read-only for individual item lookups. Existing
award counts and skin-facing strings retain their formatting. Award browsing
directories continue to query TVDB directly.

API references: [TheTVDB v4](https://github.com/thetvdb/v4-api/blob/main/docs/swagger.yml),
[TMDB external ID lookup](https://developer.themoviedb.org/reference/find-by-id),
[movie search](https://developer.themoviedb.org/reference/search-movie), and
[TV search](https://developer.themoviedb.org/reference/search-tv).

# Building the collection baseline

Run with Python 3.8 or later, without Kodi or additional packages:

```sh
python scripts/build_collections.py
```

This builds or updates `resources/databases/collections.db`. It downloads the
previous UTC day's TMDb collection-ID export, then requests collection details
to populate movie IDs and release dates. It never requests individual movie
details. TMDb's existing API key is read using the awards builder's standalone
credential reader; credentials are not printed or stored in the database.

The initial baseline contains the entire exported collection inventory. Updates
populate new collections first and then refresh existing collections, longest
overdue first. By default a central baseline update refreshes every active
collection. `--due-only` instead applies these calendar-based refresh intervals:

| Most recent release | Refresh interval |
| --- | --- |
| Less than 4 years ago | 1 month |
| 4 to less than 8 years ago | 3 months |
| 8 to less than 16 years ago | 6 months |
| At least 16 years ago | 12 months |

Collections with upcoming movies, missing release dates, or no members use the
monthly tier. Each collection retains its own UTC `last_checked_at`; updating
the overall database timestamp does not extend individual check dates. Calendar
months and years account for month ends and leap years.

Useful options:

```sh
# Stop at 100 collection-detail HTTP attempts, including retry attempts.
python scripts/build_collections.py --max-requests 100

# Run again to resume; the limit is per invocation, not a client daily budget.
python scripts/build_collections.py --max-requests 100

# Refresh only new and due collections.
python scripts/build_collections.py --due-only

# Select a source export or write a separate baseline.
python scripts/build_collections.py --snapshot-date 2026-10-29 --output .cache/collections/example.db
```

The default is eight workers with a global ceiling of ten requests per second.
`--workers` and `--requests-per-second` adjust those settings. Temporary network,
server, and rate-limit failures retry with backoff; a 429 also pauses other
workers. Snapshot downloads do not consume the collection-detail request limit.
Compressed exports are validated and cached under `.cache/collections/exports`.

Progress is committed after each collection to an unpublished
`collections.work.db` checkpoint beside the output. A stopped or failed run
resumes from that checkpoint on the next invocation, using the same
`--due-only` setting. Do not run builders concurrently against the same output.
If the published baseline changed independently, the checkpoint is rejected
rather than overwriting that newer baseline.

Successful detail responses replace the collection's complete membership,
including removing obsolete members. Exact duplicate source parts are collapsed;
conflicting release dates for the same movie fail visibly. Empty parts are valid.
IDs missing from a later complete export become inactive; their previous details
are retained and can be reused if the ID reappears.

Failures preserve previous membership and never extend `last_checked_at`. A
detail 404 is recorded as unavailable with a seven-day retry; other exhausted
temporary failures use an increasing retry delay. A database can be published
with explicitly recorded 404s, but not with unresolved/unattempted entries or
other failed details. Exit status 2 means the checkpoint needs further work.
Integrity and foreign-key checks run before atomic replacement of the bundled
file; the previous baseline is preserved until publication succeeds.

The schema is identified by `PRAGMA user_version`. It contains:

- `collection`: discovery, successful check, attempt/retry dates and active state.
- `collection_movie`: collection/movie IDs and optional release dates, with a
  movie-ID lookup index. Multiple source collections may reference one movie.
- `metadata`: source export date/hash, build/update dates and record counts.

Standalone responsibilities remain in `tmdbhelper.lib.collections`: `client.py`
owns downloads and source validation; `database.py` owns schema, queries and
transactions; `refresh.py` owns refresh-date calculations; `builder.py` owns
checkpoint orchestration and publication. The existing item-details database,
sync providers, directory containers and mappers are not changed by this tooling.

# Collection index maintenance

The bundled baseline is intended to be rebuilt monthly and shipped with addon
updates. Client maintenance uses a separate profile-local database, discovers
new collection IDs from the daily TMDb export, and shares one persistent daily
request budget between new entries and overdue refreshes. The default budget is
25 detail attempts; requests are spread over background maintenance polls.

The runtime list is `sync_nextmovies` (`type=movie`), available as Your Next
Movies. It uses the configured History provider and the standard list-item
enrichment pipeline. Collection progress uses release order, skips earlier gaps,
and infers rewatches from strictly later local calendar days. Membership and
refresh bookkeeping are separate from synced user data and item-details caches.

Development benchmark scripts, reports and verification files are kept outside
the addon repository. They are not shipped as addon modules or scripts.
