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

Provider addons follow this layout:

```text
addon.xml
LICENSE.txt
resources/
    icon.png                # provider icon
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
and scrobbling. Each selector offers
None, enabled providers declaring that feature, and installation/enabling options
from `catalog.py`. The catalogue records trusted addon IDs, display names, and
supported capabilities so missing or disabled modules are offered only for
features they support. Combined-list setup offers a catalogue provider when it
supports at least one requested feature. Loaded providers determine actual
capabilities; selection rechecks those declarations after installing/enabling
and before assigning a provider to a feature. Keep catalogue capabilities aligned
with the corresponding provider declarations when support changes.
Each `sync_provider_<feature>` setting stores an empty value for an unconfigured
feature, `never` for an explicitly disabled feature, or the chosen provider ID.
Empty settings keep associated directory lists visible for discovery and setup;
`never` hides them and suppresses setup. Choosing None in a feature selector
stores `never`; selecting a provider enables the feature again. For an
unconfigured feature, the selector preselects an enabled, capable provider already
assigned to another feature, taking the first in the displayed provider order
when several qualify. Preselection does not save a setting until confirmed.
Selecting an enabled provider outside the trusted catalogue requires confirming
a warning about trusting the third-party service and the risks of sharing viewing
activity and account data. Cancel is focused by default; declining or closing the
warning preserves existing selections. The loader attaches the actual addon ID to
each provider as `addon_id`, so trust checks use catalogue addon IDs rather than
provider-declared IDs or display names. List setup inherits the same confirmation.
Item actions use the provider selected for
the same feature. Unsupported synced-state actions are absent from Sync Options.
Personal-list actions for every authorized service, Trakt comments, ratings, and
favorites belong to core and are available independently of these selectors.
Ratings and favorites sync directly through the authenticated Trakt API without
requiring the Trakt provider addon. Their sync implementations, source-to-database
mapping, and activity tracking live in `sync/trakt/`. `SyncData` dispatches these
core sync types separately from provider types; provider registrations must not
declare `SyncRatings`, `SyncFavorites`, or the `favorites` action. Favorites lists
use Trakt authorization and never offer provider setup. Existing database columns,
sorting, pagination, and manual ratings/favorites/all-data sync remain supported.
Service rating lookups cache complete snapshots for at most twenty minutes,
separately for each account token and media type. Each lookup checks that media
type's Trakt `rated_at` activity timestamp and refreshes the snapshot when it
changes. Successful writes invalidate that media type and its synced database
values immediately; manual ratings or all-data sync clears every service rating
snapshot. Empty snapshots are cached; failed or incomplete responses
and snapshots without a valid activity timestamp are not.
List removal targets the service owning the displayed list; other services retain
their add-to-list action. The `sync_trakt` script route aliases `sync_options`.

Scrobbling has one independent provider selection. That provider receives playback
start and stop requests. Shared playback timing, completion thresholds, and TMDb
rating prompts remain in TMDbHelper. Rating prompts run without a selected or
authorized scrobbler. Watched writes belong exclusively to the selected scrobbling
provider; core does not also increment the Kodi library playcount. Provider modules
own payloads, service requests,
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
selections. Opening an unconfigured provider sync list or a list with an unavailable
selected provider offers setup, including from widgets. Installation and enabling
use Kodi's built-in
`InstallAddon` and `EnableAddon` commands, followed by a fresh discovery check.
Installations use the user's installed repositories; core does not download
provider packages or add repositories.

Skin-only history statistics never offer provider setup. Daily and monthly
statistics return no entries when the selected watched provider is unavailable
or unauthorized.

For provider setup, requests are treated as widgets unless `MyVideoNav.xml` is
active. This window state is captured when setup is created and remains fixed
for that attempt. Background lists loaded while the video browser is active also
receive standard directory behavior. The URL's `widget` parameter and container
paths do not determine setup prompt behavior.
Widget setup offers OK, Later, and Never. Later suppresses widget prompts through
a Home window property until Kodi restarts; standard directory requests ignore
Later. Never stores `never` for the requested feature. Users can enable that
feature later through its existing provider selector in the addon settings.
There is no separate global Never setting. Combined To watch lists remain visible
while either watched/progress or watchlist is not `never`. Their setup offers only
features not marked `never`; choosing Never disables those remaining features.
Setup uses the shared property mutex and rechecks availability
and prompt state after acquiring it. A prompt-generation property prevents
already-queued widget requests from repeating the same setup attempt.

`SyncProviderOnboarding(addon_id).configure()` installs or enables a catalogue
provider and offers `SyncProviderDefaultSelection(provider)`. The dialog offers
Default, Cancel, and Custom, with Default focused. Default replaces every feature's
provider selection, including `never`, with the selected provider for supported
features and the empty, unconfigured state for unsupported features. Cancel
or closing the dialog preserves all current selections.
Custom opens `SyncProviderFeatureSelection(provider)`. This provider-agnostic
multiselect reads capabilities and current selections from the loaded provider
and settings. Checked features select that provider; unchecked features clear only
its own assignments. Unchecked features already marked `never` keep that state;
explicitly checking one assigns the provider. Cancelling the multiselect changes
nothing. Trakt invokes onboarding after
successful device authentication, never during token refresh. Confirmed Trakt
logout clears its feature selections while retaining the installed module.

The **Install sync provider** setting below **Clear sync** opens the complete
trusted catalogue, including installed and enabled providers. Missing providers
have an `(install)` suffix; disabled providers have an `(enable)` suffix. Selecting
one runs the same onboarding flow: install/enable as needed, then choose Default,
Cancel, or Custom. The Custom multiselect shows its supported features.
Existing assignments to that provider are
preselected. Unchecking one resets its setting to the empty, unconfigured state;
unchecked features assigned to other providers retain their settings.

Duplicate IDs, incompatible interfaces, and broken entry points produce explicit
errors. Discovery and provider imports are scoped to a Python invocation;
setup refreshes discovery after installation or enabling. Updating already-loaded
provider code still requires a new invocation.

Provider addons are maintained separately from the plugin. Install each provider
in its own `script.module.tmdbhelper.sync.<service>` folder alongside
`plugin.video.themoviedb.helper` in Kodi's addons directory. The plugin contains
the shared interfaces and registry; provider implementations and artwork belong
in the standalone modules.

Install the provider-enabled TMDbHelper build together with matching provider
versions. The dependency version alone cannot distinguish a development checkout
from an older checkout with the same version.

The Kodi provider (`script.module.tmdbhelper.sync.kodi`) reads the active profile's
video library through JSON-RPC. Library membership supplies collection; playcounts,
last-played dates, and resume points supply history/progress. Next episodes are
limited to available local library episodes. Kodi collection is read-only through
this provider: adding/removing actual library content remains a Kodi operation.
Watched/unwatched actions and resume removal write back to library items.
Kodi supplies cumulative playcounts and the latest played date, not a complete
chronological log of individual plays. The provider refreshes snapshots at most
once per minute during normal reads, and actions invalidate/resync immediately.
Native Kodi library playback retains Kodi's own watched/resume persistence;
scrobbling another source writes to the matching library item only when Kodi is
the selected scrobbler. See the standalone provider's README for identity matching,
date limitations, and non-library tracking findings.
