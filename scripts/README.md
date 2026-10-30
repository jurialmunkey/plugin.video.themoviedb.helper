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
