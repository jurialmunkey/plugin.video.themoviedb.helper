# Sync providers (interface version 3)

TMDbHelper discovers enabled, installed `script.module.tmdbhelper.sync.*` addons.
Each addon exposes a named Python package inside `resources/lib`. Derive its
name from the addon ID by removing `script.module.` and replacing dots with
underscores. The package's `__init__.py` exports its zero-argument `Provider`
subclass of `SyncProvider` using a named absolute import from its `provider.py`.
The loader imports the package directly from its installed path without changing
`sys.path`. Package names and locations come from the addon ID; the loader has
no built-in service names or provider imports. Relative and wildcard imports
are not permitted.

Both provider addons follow this layout:

```text
addon.xml
LICENSE.txt
resources/
    icon.png                # opaque 512 x 512 service icon
    fanart.jpg
    lib/
        <package_name>/
            __init__.py     # from <package_name>.provider import Provider
            provider.py
            scrobbler.py
            actions/
            sync/
```

The `xbmc.python.module` extension declares `resources/lib` as its library.
Artwork is declared in the metadata extension's `assets` element. Package only
the individual provider folder when distributing either addon.

Providers declare:

- `interface_version = 3` explicitly on the Provider class.
- `sync_classes`: sync-type names from `SYNC_FEATURES` to DataType subclasses,
  including class factories derived from DataType. Each declares a non-empty
  `method` string so invalidation can identify its activity timestamps.
- `action_classes`: action names from `ACTION_FEATURES` to action classes.
- `getter_classes`: `movies_to_watch`, `shows_to_watch`, and `shows_in_progress`
  getters for watched/progress list behaviour. All three are required when the
  provider declares the watched capability; every getter must be callable.
- `scrobbler_class`: an optional ScrobbleRequest subclass for the scrobbling feature.
- `is_authorized()` and `get_last_activities()`: provider authentication and activity
  timestamps grouped by plural item type and activity key.

`SyncData` owns one registry per configured context. Sync classes receive
`(syncdata, item_type, provider)` and provider-specific getters receive
`(syncdata, provider)`. Forward that provider into nested factories and snapshots;
do not construct another `Provider()` inside sync implementations or getters.

The action dispatcher supplies `syncdata`, `sync_provider`, and `sync_feature`
before accessing action properties. Authorization, reads, writes, and invalidation
within the operation therefore reuse the same provider and its cached API client.
Successful synced-state actions invalidate and resync their feature before
refreshing containers, restoring skin-facing values for other cached items too.
Shared action properties use `item_type` and `base_item_type` for media types;
these are Python properties and do not rename database columns. Service browsing
authorization belongs to the service API/directory layer. Next-episode identifier
extensions and service cache invalidation belong to concrete provider subclasses.
Directory properties configure service-specific sort fields before accessing a
sync list's cached properties; the shared list classes contain only common sorts.
Configured item lists retain their SyncData context. Scrobble requests receive
`(player, provider)` and read playback details from the core player coordinator.
They return a `ScrobbleResult(successful, history_changed)` after sending a request.
Explicit dependency injection is available through
`SyncData(registry=...)`; no implicit caller API inheritance or global singleton is used.
Action discovery is shared by Sync Options and context-menu availability. Each
container configures one discovery context for its list items before finalisation.

The available feature selectors are history/progress, watchlist, collection,
rating sync, favorites, and scrobbling. Each selector offers
None and only installed providers declaring that feature. The chosen provider ID
is stored as `sync_provider_<feature>`. Item actions use the provider selected for
the same feature. Unsupported synced-state actions are absent from Sync Options.
Personal-list actions for every authorized service, Trakt comments, and Trakt
rating dialogs remain in core and are available independently of these selectors.
Disabling rating sync does not disable submitting or removing a Trakt rating.
Service rating lookups cache complete snapshots for at most twenty minutes,
separately for each account token and media type. Each lookup checks that media
type's Trakt `rated_at` activity timestamp and refreshes the snapshot when it
changes. Successful writes invalidate that media type immediately; manual ratings
or all-data sync clears every service rating snapshot, even without a selected
rating-sync provider. Empty snapshots are cached; failed or incomplete responses
and snapshots without a valid activity timestamp are not.
List removal targets the service owning the displayed list; other services retain
their add-to-list action. The `sync_trakt` script route aliases `sync_options`.

Scrobbling has one independent provider selection. That provider receives playback
start and stop requests. Shared playback timing, completion thresholds, Kodi watched
updates, and TMDb rating prompts remain in TMDbHelper and run without a selected
or authorized scrobbler. Provider modules own payloads, service requests,
authentication, and interpretation of scrobble results. Core coordinates sync-cache
refreshes after successful stop requests and Trakt stats refreshes after a reported
history change. Stats retrieval, caching, scheduling, and skin properties remain
in core and are available independently of sync-provider selection.
The core Trakt playback refresh receives an explicit core API client and does
not require an undocumented API attribute on a provider.

TMDbHelper retains database infrastructure, common sync/mapping base classes,
list-item construction, directory configuration, and invalidation. Provider modules
own their concrete sync classes, source mappings, list getters, pagination, next
metadata, synced-state actions, and scrobbling requests. Core service-action bases
provide reusable service request handling without requiring a selected provider;
provider-action subclasses add synced-state reads and invalidation. Existing API
clients remain shared with TMDbHelper's non-sync browsing and metadata features.

Activity timestamps and timer locks include the provider ID. Changing a selector
clears that feature's local cached columns and provider activity caches. Missing,
disabled, unauthenticated, or unsupported providers disable the feature and clear
its stale local sync values when those values are requested. Cleanup for an
unavailable selected provider also clears its stored activity timestamps and timer
locks, allowing a full resync when it becomes available again. Unsupported sync
types do not invalidate the provider's supported data. Remote history and
lists are not deleted by selection changes or disabled-feature cleanup.
Directory watched/playback pre-sync reaches this cleanup even when the selected
provider is unavailable; cached item-details reads remain free of provider queries.

There are no built-in fallback providers, old setting aliases, or automatic
selections. Users must install their preferred provider modules and choose their
providers. The migration prompt is deferred. Duplicate IDs, incompatible interfaces,
and broken entry points produce explicit errors. Discovery and provider imports
are scoped to a Python invocation; reload after installing or updating addons.

Provider addons are maintained separately from the plugin. Install each provider
in its own `script.module.tmdbhelper.sync.<service>` folder alongside
`plugin.video.themoviedb.helper` in Kodi's addons directory. The plugin contains
the shared interfaces and registry; provider implementations and artwork belong
in the standalone modules.

Install the provider-enabled TMDbHelper build together with matching provider
versions. The dependency version alone cannot distinguish a development checkout
from an older checkout with the same version.
