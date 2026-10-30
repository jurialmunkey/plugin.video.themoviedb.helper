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
    script.py               # opens this provider's configuration in TMDbHelper
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

Declare `xbmc.python.script` with library `resources/script.py` before the
`xbmc.python.module` extension, which retains `resources/lib` as its library.
Kodi uses the first extension as the main type. The script main type makes
providers available under Program add-ons and prevents Kodi from classifying
these independently installed providers as orphaned dependency modules.
The module extension remains available to provider discovery and loading.
Keep the existing addon ID and the dependency on TMDbHelper; core must not add
reverse dependencies on providers.

The script entry point calls
`RunScript(plugin.video.themoviedb.helper,configure_sync_provider,addon_id=<addon_id>)`
through `xbmc.executebuiltin`. The core route delegates to
`SyncProviderOnboarding(addon_id).configure()`, reusing the Default, Cancel,
and Custom configuration flow. Running a provider does not change selections
until the user confirms. Providers using this route require TMDbHelper 6.19.3
or later. Artwork is declared in the metadata extension's `assets` element.
Package only the individual provider folder when distributing an addon.

Providers declare:

- `interface_version = 3` explicitly on the Provider class.
- `sync_classes`: sync-type names from `SYNC_FEATURES` to DataType subclasses,
  including class factories derived from DataType. Each declares a non-empty
  `method` string so invalidation can identify its activity timestamps.
- `action_classes`: action names from `ACTION_FEATURES` to action classes.
- `service_sync_classes`: optional account-data sync registrations independent of
  provider selections. `SyncRatings` and `SyncFavorites` inherit ServiceDataType
  and declare a non-empty cache `method`, like other sync classes. They receive
  the same `(syncdata, item_type, provider)` constructor arguments. Their optional
  `invalidate_cache(provider)` class method clears module-owned service caches.
  Registering these exposes `service_sync`, without adding provider selectors.
- `service_action_classes`: optional independent service action names mapped to
  callable action classes. Names start with the provider ID and must be unique
  across providers and core service actions. This exposes `service_actions`.
  Every authorized provider contributes these actions regardless of sync selections.
  The dispatcher assigns `sync_provider` and the caller's `syncdata` before
  accessing any action properties.
- `migrate_settings()`: optional migration hook called under the loader lock after
  validation and addon-ID assignment, before the provider is returned or its API
  client is constructed. The default is a no-op for existing providers.
- `getter_classes`: `movies_to_watch`, `shows_to_watch`, and `shows_in_progress`
  getters for watched/progress list behaviour. All three are required when the
  provider declares the watched capability; every getter must be callable.
- `ratings_classes`: optional media-type names (`movie`, `tvshow`, `season`,
  `episode`) mapped to RatingsSupplier subclasses. Each implements
  `get_ratings()`; registering any supplies the independent `ratings` capability.
- `imdb_top250_classes`: optional `movie` / `tvshow` names mapped to
  IMDbTop250Supplier subclasses implementing `get_items()`. Each media type must
  also have a ratings supplier. Registering any supplies the `imdb_top250`
  capability; empty defaults preserve existing interface-version-3 providers.
- `stats_class`: an optional StatsSupplier subclass implementing `get_items()`.
  Registering it exposes the independently selected `stats` capability. Existing
  providers inherit a `None` default and retain interface-version-3 compatibility.
- `monitor_lists_class`: an optional MonitorListsSupplier subclass implementing
  `get_lists()` and `get_list_items(list_slug)`. This supplies the independent
  `monitor_lists` capability for library monitoring and list retrieval.
- `scrobbler_class`: an optional ScrobbleRequest subclass for the scrobbling feature.
- `directory_item_class`: an optional BaseDirItem subclass contributing a root
  folder. Its `params['info']` must name one of the provider's `list_routes`.
- `list_routes`: optional route names mapped to `module_name` / `import_attr`
  dictionaries, using the same lazy named imports as core routes. Every name
  starts with `<provider_id>_`; duplicate routes are rejected. The imported
  objects are directory container classes with the existing `(handle,
  paramstring, **params)` interface. Registering routes exposes the `lists`
  capability. Empty defaults keep existing interface-version-3 providers valid.
- `is_authorized()` and `get_last_activities()`: provider authentication and activity
  timestamps grouped by plural item type and activity key.

`SyncData` owns one registry per configured context. Sync classes receive
`(syncdata, item_type, provider)` and provider-specific getters receive
`(syncdata, provider)`. Forward that provider into nested factories and snapshots;
do not construct another `Provider()` inside sync implementations or getters.

The action dispatcher supplies `syncdata`, `sync_provider`, and `sync_feature`
before accessing action properties. Authorization, reads, writes, and invalidation
within the operation therefore reuse the same provider and its cached API client.
Successful synced-state actions use `SyncActionInvalidator` before refreshing
containers. Actions declare `sync_types` for their item type and
`show_sync_types` for parent-show dependencies. The invalidator uses the existing
sync factories to normalize activity identities, deduplicates them, and refreshes
only dependencies assigned to the action's provider. It retains cached columns
until successful responses replace them. Explicit maintenance and provider
changes continue to use the broader feature invalidators.
MDbList watched additions use a concrete invalidator that preserves the history
timestamp for incremental requests; removals invalidate it for a full snapshot.
Trakt rating actions invalidate only the affected media type's ratings snapshot.
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
scrobbling, and stats. Single-provider selectors offer
None, enabled providers declaring that feature, and installation/enabling options
from `catalog.py`. The catalogue records trusted addon IDs, display names, and
supported capabilities so missing or disabled modules are offered only for
features they support. Combined-list setup offers a catalogue provider when it
supports at least one requested feature. Loaded providers determine actual
capabilities; selection rechecks those declarations after installing/enabling
and before assigning a provider to a feature. Keep catalogue capabilities aligned
with the corresponding provider declarations when support changes.
Catalogue entries also declare `provider_id`, allowing unavailable providers'
namespaced list routes to offer installation or enabling.
Each `sync_provider_<feature>` setting stores an empty value for an unconfigured
feature, `never` for an explicitly disabled feature, or the chosen provider ID.
Scrobbling uses a multiselect and stores a JSON array of provider IDs in
`sync_provider_scrobbling`; existing single-provider values remain readable.
The dialog checks all selected, available providers and also offers installation
or enabling of supported providers. Confirming no selections stores `never`.
Cancelling, declining a provider trust warning, or failing provider installation
leaves the saved selection unchanged. Installation rechecks actual capabilities.
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
Trakt registers `traktrating` and `traktfavorites`; the existing `rating` and
`favorites` script selectors remain compatibility aliases. MDbList retains its
`mdblistuser` action. Personal ratings and favorites sync, record mapping, actions, and account rating
snapshots belong to the Trakt module. They use `service_sync_classes` and
`service_action_classes`; they do not depend on which provider is selected for
watched data, watchlists, collection, or scrobbling. Disabled or unauthorized
modules supply no service actions or sync data. Existing columns and activity
identifiers are retained. Unavailable or unauthorized services leave cached
values and activity timestamps intact. Normal sync resumes when the service is
available again; manual invalidation remains available when a reset is needed.
Public ratings are separate: Trakt supplies movies, shows, seasons, and episodes
through `ratings_classes`, just like MDbList. The monitor uses the existing
ratings-provider enablement and priority settings, with no direct Trakt fallback.
Personal rating snapshots retain account/media-type isolation and their maximum
twenty-minute lifetime. Activity changes and successful writes invalidate them;
manual ratings or all-data sync invokes the module's cache invalidation hook.
Empty snapshots are cached; failed or incomplete responses are not.
List removal targets the service owning the displayed list; other services retain
their add-to-list action. The `sync_trakt` script route aliases `sync_options`.

Scrobbling has an independent selection of multiple providers. Each selected,
available, authorized provider receives playback start and stop requests.
`PlayerScrobblers` coordinates independent `PlayerProviderScrobbler` instances,
so a successful completion is not repeated while another provider retries a failed
response. A separate playback instance handles the single TMDb rating prompt.
Shared playback timing, completion thresholds, and TMDb
rating prompts remain in TMDbHelper. Rating prompts run without a selected or
authorized scrobbler. Watched writes belong exclusively to the selected scrobbling
providers; core does not also increment the Kodi library playcount. Provider modules
own payloads, service requests,
authentication, and interpretation of scrobble results. Core coordinates sync-cache
refreshes after successful stop requests. A reported history change also forces
stats refresh when the playback provider is the selected stats source, independently
of the watched source. Stats persistence, scheduling, totals, and skin properties
remain in core; API retrieval and source mapping belong to the selected supplier.
Core playback refresh does not construct a service API client for stats.

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
its own assignments. For scrobbling, checking adds the provider alongside existing
selections, and unchecking removes only that provider. Confirmed logout likewise
removes only that provider from scrobbling selections. Unchecked features already
marked `never` keep that state; explicitly checking one assigns the provider.
Cancelling the multiselect changes
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

Provider selectors and **Install sync provider** save and close the addon settings
dialog before opening their selection dialogs. This ensures selectors read the
saved values and provider changes are persisted directly, avoiding Kodi's deferred
setting writes while the addon settings dialog is open. Settings reopen at the
original provider control afterward, including when selection is cancelled.
Provider setup launched from lists or other scripts does not reopen settings.

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
one of the selected scrobblers. See the standalone provider's README for identity
matching, date limitations, and non-library tracking findings.


## Provider list directories

Directories are additive: all enabled providers may expose their own root folder,
independently of history, watchlist, collection, and scrobbling selections. There
is no single `sync_provider_lists` setting. Folder visibility and authorization
belong to the provider's directory item and API layer.

Providers own their menu items, list containers, properties, mappers, sort
options, icons, and type-variant artwork selection. Reuse BaseDirItem and its
item builder for menus, and ListDefault/ListStandard with
`list_properties_class`, `configure_list_properties()`, and
`get_items_finalised()` for lists. Properties retrieve entries through the API
or appropriate database interfaces; mappers turn those entries into item
dictionaries. Configure attributes before accessing cached properties.

The MDbList module registers `mdblist_directory` and all existing `mdblist_*`
list routes. Core resolves provider routes through the registry without
per-list forwarding entries. If no route is found, a `<provider_id>_` prefix
matching a trusted catalogue provider with the lists capability offers
installation/enabling through Kodi. The dialog names the requested route and
provider; successful setup retries that route without changing sync selections.
An installed provider must declare the requested route or an invalid-route
error is raised. Concurrent requests recheck provider availability and prompt
generation under a mutex.
Declining returns no directory items. The sorting script resolves the module's
sorting container. Library monitoring uses its own supplier interface below,
without constructing directory containers. The MDbList API client and
rating-response mappings belong entirely to the module. Core does not construct
or expose an MDbList API client.

Trakt registers a single `trakt_directory` root. Grouped browsing, genres,
calendar period menus, Random, and Discover live under that root. Core Movie,
TV, Random, and details menus no longer inject Trakt entries. Existing `trakt_*`
browsing URLs remain registered by the module. The nine legacy `random_*`
Trakt URLs redirect to their `trakt_random_*` counterparts; obsolete `dir_*`
Trakt URLs have no reroutes. Directory routing and sorting use the registry.
Shared Trakt API transport and calendar support remain in core for the local
library calendar. Its concrete local subclass does not import the optional
provider; the Trakt module subclasses the same calendar support.

## Ratings suppliers

In Sync settings, the Ratings group contains Providers and Priority. Providers
uses a multiselect to enable/disable installed suppliers. Priority uses select
dialogs to choose a provider and move it up/down. Save applies the order;
Cancel leaves it unchanged. Each control preserves the other's configuration.
Enabled Kodi modules with the ratings capability appear independently of
sync-provider selections.
New suppliers default to enabled and follow saved entries in alphabetical order;
unavailable providers' saved order and disabled state are retained.

The hidden `ratings_provider_configuration` setting stores a JSON object with
`order` and `disabled` lists of provider IDs. It is separate from the
single-provider sync selectors and does not invalidate any caches. Existing
cached results remain until their normal
expiry or manual deletion.

Subclasses of `tmdbhelper.lib.sync.providers.ratings.RatingsSupplier` receive
`provider`, `tmdb_type`, `tmdb_id`, `imdb_id`, `season`, and `episode` before the
cached `.ratings` property is accessed. They return a dictionary using existing
ratings-table fields and their existing raw formats (for example, integer
ratings on a 0-100 scale). The supplier owns authorization, API calls, and source
mapping; it must return `{}` for an unavailable API. It must not read or write
the item-details database. No new table fields or migrations are required.

RatingsDict and its season/episode subclasses instantiate only enabled suppliers
registered for their media type. Retrieval runs in parallel, while merging uses
the configured order, with the first provider winning overlapping non-missing
fields. `None` and empty strings are missing; zero ratings and vote counts are
valid. Lower providers fill missing fields.

Provider results occupy the former MDbList position in `rating_attribs`: after
OMDb and before direct Trakt/TMDb sources. Existing built-in precedence and IMDb
Top 250 output format remain unchanged. MDbList's module supplies all four media
types using its module-owned API client's rating methods; no MDbList-specific
branch remains in the ratings dictionaries.

## Account stats

The Stats source uses `sync_provider_stats` and the same selector, None option,
and Default/Custom onboarding flow as watchlist and collection. Selection is
independent of watched, scrobbling, and ratings sources. There is no automatic
first-capable fallback. Existing installations must select a source or configure
one through provider onboarding; no Trakt source is silently assigned.

`tmdbhelper.lib.sync.providers.stats.StatsSupplier` receives `provider` before its
cached `.items` property is accessed. `get_items()` returns dictionaries containing
`name`, `type`, and integer `stat`. `name` is the metric (for example `minutes`),
while `type` is the category (for example `movies` or `shows`). Providers use these
common names for comparable metrics and may supply additional categories. Suppliers
own requests and mapping, and do not access the query database. The Stats helper
checks the selected provider's authorization before constructing its supplier.
`None` means unavailable or failed: retain the previous snapshot without extending
its expiry. An empty list is a successful empty snapshot. Zero values are valid.
Malformed source data and programming errors must not be hidden.

Core retains `trakt_stats`, `get_trakt_stats()`, the `get_trakt_stats` script route,
and `TraktStats.*` skin properties as legacy names for generic selected-source
stats. Complete successful snapshots replace the previous rows and expire after
twenty minutes; empty snapshots are cached too. Core calculates combined totals
and minute conversions. Source changes clear the stats rows, expiry, and previously
published skin properties through the dedicated stats invalidator. Missing or
disabled sources supply no stats, without falling back to direct Trakt requests.
Startup requests stats independently of Trakt authorization. Manual stats
invalidation optionally refreshes the selected source. The Trakt module supplies
`users/me/stats` and owns its recursive source-to-record mapping.

## IMDb Top 250

Subclasses of `tmdbhelper.lib.sync.providers.imdb_top250.IMDbTop250Supplier`
receive `provider` and `tmdb_type` (`movie` or `tv`) before the cached `.items`
property is accessed. `get_items()` returns normalized dictionaries with `rank`,
`tmdb_type`, `tmdb_id`, `title`, `year`, and `slug`, ordered by rank. The supplier
owns API requests, authorization where required, and source mapping. It returns
an empty list when no data is available; malformed data and programming errors
must not be hidden. Suppliers do not access the query database.

The `IMDbTop250` helper uses the existing ratings priority and enabled-provider
settings for the requested media type. It skips providers without the matching
Top 250 supplier and requests each remaining supplier sequentially until one
returns a non-empty list. Results from different providers are not merged.
There is no separate Top 250 selector or automatic provider installation.

`FindQueriesDatabaseIMDbTop250` converts those records into the existing query
table's columns and owns cache reads and writes. Schema, expiry, output-key
selection, and ratings consumers are unchanged. Provider priority changes take
effect on the next cache refresh, as with ratings. Without an available supplier,
an uncached lookup returns no result and does not write an empty cache entry.

The Trakt module registers movie and TV suppliers using the existing public
Justin IMDb lists. These requests do not require account authorization.

## Monitored lists

An optional `monitor_lists_class` derives from
`tmdbhelper.lib.sync.providers.monitor_lists.MonitorListsSupplier` and receives
its provider before any cached properties are accessed. The registry exposes
one cached `monitor_list_suppliers` tuple per context. These suppliers are
independent of watched, watchlist, scrobbling, and ratings selections.

`get_lists()` supplies the cached `.lists` result: entries with `label` and
`params` containing string `list_slug` and `user_slug` values. The default
`user_slug` is `__api_<provider_id>__`. MDbList therefore keeps the existing
`__api_mdblist__` identifier and numeric list IDs stored in `monitor_userlist`
and `monitor_userslug`. No migration or new setting is required. MDbList list
labels remain `MDbList: <name>` and use a module-owned ItemMapper.

`get_list_items(list_slug)` returns the normalized records expected by
LibraryBuilderUserList: each has `type` (`movie` or `show`) and a matching
`movie`/`show` dictionary containing `title` and `ids` (`tmdb` and `imdb`).
The module owns API requests and normalization. MDbList retains its existing
separate movies/shows response handling and incomplete-record filtering.
Unauthorized suppliers return no available lists or contents. Suppliers must
not open settings, prompt for installation, or perform library/database writes.

MonitorUserLists obtains all lists from suppliers. LibraryBuilderUserList
retrieves every list through the same registry/supplier interface. Trakt owns
watchlist, owned-list, liked-list enumeration, and paginated content retrieval.
Its reserved user identifier is `__api_trakt__`; its list identifier encodes the
original user and list slugs as a JSON pair. An optional supplier method,
`get_legacy_list_slug(user_slug, list_slug)`, translates old references; the base
returns None. Trakt translates the historical unreserved user/list slug pairs,
so existing saved selections and direct library-addition paths keep working. An unavailable
provider returns no items; it never falls back to a Trakt request or setup
prompt. Reading or updating lists does not rewrite saved monitoring selections.
Core retains limits, confirmation, progress, library creation, and tagging.
The tagging subclass and manual list-addition script inherit the same request
dispatch. No database table definitions or cache invalidation are changed.

## Provider credentials and migration

MDbList stores its API key in its own addon settings as `apikey`. The core API
settings page opens the module's settings through `open_sync_provider_settings`,
using the existing install/enable flow when needed. This does not select a sync
provider. All MDBList requests require the module to be installed and enabled.

The module's `migrate_settings()` hook checks core's hidden legacy
`mdblist_apikey` setting whenever the provider is loaded, including discovery and
installation. It copies the key only if the module has no key, reads back the
destination to verify persistence, and then clears the core value. An existing
module key takes precedence. An empty legacy value makes subsequent loads a
no-op; failed writes preserve the source for retry. The hidden declaration is
retained solely so Kodi can still retrieve values from older installations.
