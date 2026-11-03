# Sync providers (interface version 4)

TMDbHelper discovers enabled, installed `script.module.tmdbhelper.sync.*` addons.
Each addon exposes a named Python package inside `resources/lib`. Derive its
name from the addon ID by removing `script.module.` and replacing dots with
underscores. The package's `__init__.py` exports its zero-argument `Provider`
subclass of `SyncProvider` using a named absolute import from its `provider.py`.
The loader imports the package directly from its installed path without changing
`sys.path`. Package names and locations come from the addon ID; the loader has
no built-in service names or provider imports. Relative and wildcard imports
are not permitted.

TMDb is an internal provider in `tmdbhelper.lib.sync.providers.tmdb`, registered
directly by the registry and validated against the same provider interface.
It is always available without addon discovery, installation, or account
authorization. Its ratings contribution can be disabled and reordered separately.
The external-addon catalogue and loader do not install or import this provider.

With stored TMDb login credentials, the same internal provider also declares
`SyncWatchlist` and the `watchlist` action. Without credentials it declares neither;
provider discovery never starts interactive authentication. Select TMDb as the
watchlist source through the existing sync selector. Reads and writes share the
provider's cached `TMDbUser` client, independently of its public ratings client.
Watchlists refresh every ten minutes because TMDb has no last-activities endpoint.
Only complete paginated snapshots replace cached membership; failed requests
preserve it, while successful empty responses clear it. Movie and show snapshots
remain separate; seasons and episodes have no TMDb watchlist entries.

Provider-owned mapping stores source order in `watchlist_rank` and uses local
first-seen UTC dates for `watchlist_listed_at`, since TMDb does not return added-at
timestamps. Retained entries keep their first-seen dates; observed removals clear
them. These dates do not represent the original dates added on TMDb.
Saved `tmdb_v4_watchlist` directories resolve to `sync_watchlist`, and explicit
`sync_tmdb,sync_type=watchlist` calls delegate to the selected sync watchlist action.
Successful watchlist actions use the standard provider invalidator before refreshing lists.

TMDb registers its account browsing routes through `list_routes`. Its root folder
is contributed through `directory_item_class` only when logged in, replacing the
old Users folder. Recommendations, Favourites, Rated, Your Lists, and custom-list
contents use provider-owned containers, properties, and mappers with the existing
list finalisation pipeline. Account reads check stored credentials before using
the user client and do not prompt for login. Routes remain registered when logged
out so saved links safely return empty lists. The `dir_tmdb_v4` and remaining
`tmdb_v4_*` account routes redirect to the matching `tmdb_*` routes.

The provider's `TMDbUserLists` client owns pagination and is shared by watchlist
sync, account browsing, library monitoring, and custom-list action enumeration.
Monitoring is independent of all sync selections. The supplier uses
`__api_tmdb__` with `watchlist/movie`, `watchlist/tv`, the corresponding favourites,
rated and recommendation references, and `list/<id>` for owned custom lists.
Its movie/show records include TMDb IDs and a null IMDb ID for the existing library
builder. It retrieves complete lists before returning any contents; failed pages
return no snapshot. No library writes or setup prompts occur in the supplier.

TMDb registers `tmdbuserlist`, `tmdbrating`, and `tmdbfavorites` as service actions
while logged in, independently of the watchlist selection. They appear directly
in Sync Options with the TMDb service name and share the provider's user client.
The old TMDb User Options submenu and its setting are removed. `sync_tmdb` remains
a compatibility alias: `userlist`, `rating`, and `favorite` select the corresponding
TMDb service action, while no selector opens Sync Options. Playback rating prompts
explicitly select `tmdbrating`. The existing personal TMDb rating cache and request
payloads remain in use; no shared Trakt sync columns or database schema are changed.

OMDb is also internal, in `tmdbhelper.lib.sync.providers.omdb`, and uses the same
validation and registration pipeline. Its provider-owned authorization check
requires the existing `omdb_apikey` setting. With a key configured, OMDb appears
in Ratings Providers and Priority and defaults to enabled unless previously
disabled. Without a key it is not registered; its saved priority and disabled
state are retained. Internal-provider availability is refreshed per registry.
OMDb requires no separate addon installation or module enablement.

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

- `interface_version = 4` explicitly on the Provider class. See
  [Interface versions](#interface-versions) for the supported range and policy.
- `sync_classes`: sync-type names from `SYNC_FEATURES` to DataType subclasses,
  including class factories derived from DataType. Each declares a non-empty
  `method` string so invalidation can identify its activity timestamps.
- `action_classes`: action names from `ACTION_FEATURES` to action classes that
  inherit `tmdbhelper.lib.script.sync.item.ItemSync`.
- `service_sync_classes`: optional account-data sync registrations independent of
  provider selections. `SyncRatings` and `SyncFavorites` inherit ServiceDataType
  and declare a non-empty cache `method`, like other sync classes. They receive
  the same `(syncdata, item_type, provider)` constructor arguments. Their optional
  `invalidate_cache(provider)` class method clears module-owned service caches.
  Registering these exposes `service_sync`, without adding provider selectors.
- `service_action_classes`: optional independent service action names mapped to
  action classes that inherit `tmdbhelper.lib.script.sync.item.ItemSync`.
  Names start with the provider ID and must be unique
  across providers and core service actions. This exposes `service_actions`.
  Every authorized provider contributes these actions regardless of sync selections.
  The dispatcher assigns `sync_provider` and the caller's `syncdata` before
  accessing any action properties.
- `migrate_settings()`: optional migration hook called under the loader lock after
  validation and addon-ID assignment, before the provider is returned or its API
  client is constructed. The default is a no-op for existing providers.
- `getter_classes`: `movies_to_watch`, `shows_to_watch`, and `shows_in_progress`
  getters for watched/progress list behaviour. All three are required when the
  provider declares the watched capability. Each getter inherits
  `tmdbhelper.lib.sync.datasync.SyncDataGetter` and implements `get_items()` and
  `get_sync_succeeded()`; inheriting `SyncDataGetterAll` or one of its subclasses
  provides both. See [Synced data getters](#synced-data-getters).
- `ratings_classes`: optional media-type names (`movie`, `tvshow`, `season`,
  `episode`) mapped to RatingsSupplier subclasses. Each implements
  `get_ratings()`; registering any supplies the independent `ratings` capability.
- `imdb_top250_classes`: optional `movie` / `tvshow` names mapped to
  IMDbTop250Supplier subclasses implementing `get_items()`. Each media type must
  also have a ratings supplier. Registering any supplies the `imdb_top250`
  capability; the empty default keeps providers without it valid.
- `stats_class`: an optional StatsSupplier subclass implementing `get_items()`.
  Registering it exposes the independently selected `stats` capability. Providers
  without it inherit a `None` default.
- `monitor_lists_class`: an optional MonitorListsSupplier subclass implementing
  `get_lists()` and `get_list_items(list_slug)`. This supplies the independent
  `monitor_lists` capability for library monitoring and list retrieval.
- `list_actions_class`: an optional ListActions subclass implementing
  `like_list(list_slug, user_slug='me', delete=False)`, `rename_list(list_slug)`,
  and `delete_list(list_slug)`. It receives the provider in its constructor and
  supplies the independent `list_actions` capability. The `None` default keeps
  providers without list actions valid. See [List actions](#list-actions).
- `identifier_resolver_class`: an optional IdentifierResolver subclass implementing
  `get_ids(tmdb_type, tmdb_id, season=None, episode=None)`. It receives the provider
  and supplies the `identifiers` capability. The `None` default preserves existing
  providers. This optional interface requires core 6.20.4; interface version 4
  remains valid. See [External identifiers](#external-identifiers).
- `scrobbler_class`: an optional ScrobbleRequest subclass for the scrobbling feature.
  Core calls `scrobble(method)`, which returns a `ScrobbleResult`. Scrobblers using
  the inherited `scrobble()` implement `get_scrobbler_item()` and
  `send_request(method, payload)`; scrobblers that override `scrobble()` do not.
- `directory_item_class`: an optional BaseDirItem subclass contributing a root
  folder. Its `params['info']` must name one of the provider's `list_routes`.
- `list_routes`: optional route names mapped to `module_name` / `import_attr`
  dictionaries, using the same lazy named imports as core routes. Every name
  starts with `<provider_id>_`; duplicate routes are rejected. The imported
  objects are directory container classes with the existing `(handle,
  paramstring, **params)` interface. Registering routes exposes the `lists`
  capability. The empty default keeps providers without lists valid.
- `is_authorized()` and `get_last_activities()`: provider authentication and activity
  timestamps grouped by plural item type and activity key.

`SyncData` owns one registry per configured context. Sync classes receive
`(syncdata, item_type, provider)` and provider-specific getters receive
`(syncdata, provider)`. Forward that provider into nested factories and snapshots;
do not construct another `Provider()` inside sync implementations or getters.

`DataType.sync()` returns true when its data is current or a refresh succeeds;
failed or throttled refreshes do not report success. `SyncData.sync()` refreshes
every requested sync type and returns whether all prerequisites are current.
Unsupported fields of an authorized provider are intentionally empty; a missing
or unauthorized provider cannot supply fresh prerequisites.
`SyncDataGetter.sync_succeeded` caches this outcome for one configured getter.
Ordinary `.items` reads retain access to cached data after a failed refresh.
Provider `shows_in_progress` wrappers expose their parent getter's outcome and
check any required filter requests, such as Trakt's optional calendar lookup.
Derived next-episode calculations require successful prerequisites and complete
per-show responses before replacing cached results. They return `None` on
failure and an empty collection only for a successful empty result.

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
Trakt registers `traktrating`, `traktfavorites`, `traktcomments`, and
`traktuserlist`; the existing `rating`, `favorites`, `comments`, and `userlist`
script selectors remain compatibility aliases.
The comment dialog action belongs to the Trakt module and uses its provider API.
The module also owns list creation and item membership actions, including list
selection, removal detection, and the existing monitored-list library prompt.
These actions use the supplied provider API and registry. Core discovers all
service actions through provider registrations without constructing a Trakt API.
The Trakt-specific action base belongs to the module; older module versions
importing the removed core action base must be updated before they can load.
MDbList retains its `mdblistuser` action.
Personal ratings and favorites sync, record mapping, actions, and account rating
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

There are no built-in fallback sync providers, old setting aliases, or automatic
sync selections. Opening an unconfigured provider sync list offers setup, including
from widgets. A list with a saved provider selection does not offer replacement
setup when that provider is unavailable; its data is unavailable until the provider
returns or the user changes the selection in settings. Combined lists can still use
their other available selected providers. Provider-specific lists also skip
installation prompts after the registry reports a provider load failure.
Installation and enabling use Kodi's built-in
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
provider and offers `SyncProviderDefaultSelection(provider)` when it supports
selectable sync features. Providers without these features, such as TVDb and
Gemini, skip configuration and leave existing sync selections unchanged.
The dialog offers
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
Cancel, or Custom when sync features are supported. The Custom multiselect shows
its supported features.
Existing assignments to that provider are
preselected. Unchecking one resets its setting to the empty, unconfigured state;
unchecked features assigned to other providers retain their settings.

Provider selectors and **Install sync provider** save and close the addon settings
dialog before opening their selection dialogs. This ensures selectors read the
saved values and provider changes are persisted directly, avoiding Kodi's deferred
setting writes while the addon settings dialog is open. Settings reopen at the
original provider control afterward, including when selection is cancelled.
Provider setup launched from lists or other scripts does not reopen settings.

Duplicate IDs produce explicit errors. A provider addon that fails to import or
validate, such as one with an unsupported interface version or one partway
through an update, is logged and treated as temporarily unavailable rather than
raising into lists. An OK dialog names the module and asks the user to update it,
while confirming that settings and synced data have been kept. The dialog appears
once per failed provider per Kodi session, including across separate registries
and simultaneous lookups. A successful load resets that provider's notification
so a later failure can be reported again. This does not change the addon's enabled
flag or clear its feature selections. Technical error details remain in the log.
Selected-provider lookups return no provider, full listings
skip it, and its synced data is kept rather than cleared as for a removed
provider. Each registry tries a failed addon once, so the next invocation loads
it again. Selected-provider lookups load only the provider's own addon when its
addon ID is `script.module.tmdbhelper.sync.<provider_id>`; other providers are
found by loading every discovered provider. Listing all providers loads the rest
and applies the duplicate checks. Each provider is loaded once per registry.
Discovery and provider imports are scoped to a Python invocation;
setup refreshes discovery after installation or enabling. Updating already-loaded
provider code still requires a new invocation.

External provider addons are maintained separately from the plugin. Install each
external provider
in its own `script.module.tmdbhelper.sync.<service>` folder alongside
`plugin.video.themoviedb.helper` in Kodi's addons directory. The plugin contains
the shared interfaces, registry, and internal TMDb/OMDb providers; external provider
implementations and artwork belong in the standalone modules.

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


## Synced data getters

`SyncDataGetter` is the interface that core reads from every synced data getter,
including those providers supply through `getter_classes`. Getters receive
`(syncdata, provider)`. Callers set `additional_keys` before reading the cached
`items` and `sync_succeeded` properties, which call `get_items()` and
`get_sync_succeeded()`. Both methods raise `NotImplementedError` on the base class,
and the loader rejects provider getters that do not override them.
`SyncDataGetterAll` implements both through the sync database; wrappers that
filter another getter, such as `shows_in_progress`, inherit `SyncDataGetter` and
derive both values from their parent getter.

## Interface versions

`SyncProviderLoader` accepts providers whose `interface_version` lies between its
`minimum_interface_version` and its current `interface_version`, inclusive.
Each class that a provider supplies inherits a core base class that defines its
interface, and the loader checks the inheritance and required overrides at load.
Core reads only the attributes and methods that these base classes declare.

When core starts relying on something new from provider-supplied classes:

- Prefer adding it to the base class with a default that preserves the previous
  behaviour. Existing providers keep working, so no version change is needed.
- When no such default exists, add it to the base class as a method raising
  `NotImplementedError`, add a loader check, and increase both the current and
  minimum interface versions. Older providers are then rejected at load and are
  unavailable until they update.
- When a provider relies on new core behaviour, increase the minimum
  `plugin.video.themoviedb.helper` version imported by its `addon.xml`. Kodi
  enforces that direction, so the provider cannot run on an older core.
- Record each interface version below.

| Version | Changes |
| --- | --- |
| 4 | Getters inherit `SyncDataGetter` and implement `get_items()` and `get_sync_succeeded()`. Actions and service actions inherit `ItemSync`. Scrobblers inherit `ScrobbleRequest`; those using its `scrobble()` implement `get_scrobbler_item()` and `send_request()`. The loader accepts a version range. |
| 3 | Previous interface: getters, actions and scrobblers only had to be callable. |

## List actions

`tmdbhelper.lib.sync.providers.list_actions.ListActions` defines operations on
lists rather than movie, show, or episode items. Registered classes inherit this
base and implement all three methods; the loader validates both inheritance and
method overrides. `get_provider_list_actions(provider_id, registry=None)` resolves
an enabled, authorized provider and constructs its actions with that same
provider context. Missing, unavailable, unauthorized, or unsupported providers
supply no list actions. This does not depend on sync provider selections.

The Trakt module registers `TraktListActions` and owns list like/unlike, rename,
and delete requests, prompts, feedback, and container refresh behavior. Core keeps
the legacy `like_list`, `rename_list`, and `delete_list` script commands as thin
delegates to this interface. The `like_list` command retains `user_slug` and the
`delete` flag for unliking. Directory mappers continue to emit the existing script
commands and perform no writes themselves. List creation and item membership
actions are separate from this interface.

List actions require core 6.20.3 or later. They are an optional addition to
interface version 4; existing providers inherit the empty default.

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

Sortable entries retain their `is_sortable` property and declare their sorting
route in `infoproperties['sortby_info']`, such as `mdblist_sortby` or
`trakt_sortby`. Provider mappers and menu item builders supply this route; core
handles Skin Shortcuts detection and redirects to it with the original `info`
in `parent_info`. Entries without `sortby_info` use the shared `sync_sortby`
route, which resolves provider sort methods through the registry. Ordinary
browsing keeps the original route. Existing `is_sortable` values are preserved
so these entries also work with older core versions.

Core resolves provider list routes through the registry without
per-list forwarding entries. If no route is found, a `<provider_id>_` prefix
matching a trusted catalogue provider with the lists capability offers
installation/enabling through Kodi. The dialog names the requested route and
provider; successful setup retries that route without changing sync selections.
An installed provider must declare the requested route or an invalid-route
error is raised. Concurrent requests recheck provider availability and prompt
generation under a mutex.
Declining returns no directory items. Sorting scripts resolve provider-owned
sorting containers. Library monitoring uses its own supplier interface below,
without constructing directory containers. Service-specific API clients and
response mappings belong to their provider modules. MDbList setup, list URLs,
script commands, localization, and implementation details are documented in the
[module README](https://github.com/jurialmunkey/script.module.tmdbhelper.sync.mdblist/blob/main/README.md).

Trakt registers a single `trakt_directory` root. Grouped browsing, genres,
calendar period menus, Random, and Discover live under that root. Core Movie,
TV, Random, and details menus no longer inject Trakt entries. Existing `trakt_*`
browsing URLs remain registered by the module. The nine legacy `random_*`
Trakt URLs redirect to their `trakt_random_*` counterparts; obsolete `dir_*`
Trakt URLs have no reroutes. Directory routing and sorting use the registry.
The Trakt module owns its standard directory bases, pagination-header handling,
filters, list cache configuration, calendar requests, and calendar mappers.
Containers configure their properties and retain core's list finalisation
pipeline. Properties select their mapper through `item_mapper_class`; output
still uses the shared mapper pipeline for extra properties and dictionary cleanup.
Class names, route registrations, cache keys, and calendar date behavior are
preserved. The shared `mapper_standard` classes and factory remain in core
because MDbList also uses them. Core's `lists_calendar` retains episode stacking
used by both Trakt and the local library calendar, with no provider import.
The Trakt module owns its API/authentication package in
`tmdbhelper_sync_trakt.api`, including client ID configuration and its pagination
limit. Its provider factory, discover dialog, and directory authorization helper
use the module-owned classes. The client continues to inherit core's generic
`NoCacheRequestAPI`.

Trakt containers configure their client through the module's `TraktList` mixin.
Its `TraktContainerAPIs` resolves a provider lazily through the registry and
reuses that provider's API. Nested list enumeration, directory authorization,
and Discover receive the same provider context before cached properties are
accessed. Shared core lists and the shared Discover base have no Trakt client.
Core no longer performs a Trakt-specific startup authorization request; the
module validates and refreshes credentials when its API is needed.

Core account entry points launch the module's account actions. The core Trakt
API package, API-key configuration, pagination constant, and obsolete token
permissions are removed. Service requests, credentials, and account behavior
belong entirely to the module. Shared request and token-handler infrastructure
remains in core.

### Trakt preferences

The Trakt module owns `cache_own_lists`, `genre_icon_location`, and `use_calendar`
in its settings. Core's API settings page opens them through **Trakt settings**
and the existing `open_sync_provider_settings` route. The provider's
`migrate_settings()` hook copies the legacy core preferences once, before API
clients or settings-dependent getters are used. It preserves non-default module
preferences already saved by the user, including false boolean values, verifies
each write, and marks migration complete only after all writes succeed. A failed
or partial migration can be retried without overwriting saved module values.

Core keeps `trakt_cacheownlists`, `trakt_genre_icon_location`, and
`nextepisodes_usecalendar` as hidden compatibility definitions so Kodi retains
their values until the module can migrate them. Migration leaves those source
values intact. Only the module's preferences control its behavior afterward.

The page multiplier (`pagemulti_trakt`, labelled **Other page multiplier**),
calendar flattening, next-episode sorting, recommendation seed, and watched
indicators remain core preferences because they serve shared functionality.
Legacy Trakt names do not make those settings provider-owned. The shared
`seasons_upnext` preference no longer depends on the legacy Trakt token.

### Trakt credentials

The module owns the hidden `token` setting and its sign-in/sign-out controls.
Account dialogs use module-local translations, while built-in Kodi labels
continue to use the shared localization helper. Running the module without
arguments retains the provider configuration flow; `action=authenticate` and
`action=revoke` run its account actions and reuse core's invalidation interfaces.

`TraktSettings.migrate_credentials()` has its own `credentials_migrated` marker,
independent of preference migration. It copies the legacy core `trakt_token`
once, preserving both non-empty module credentials and an explicitly configured
empty token. Each setting write is verified before migration is marked complete.
Failed writes can be retried; the legacy source is retained unchanged. Completion
clears the old session authorization properties so they cannot override a
preconfigured module account. Logout clears the module token without resetting
the migration marker, so later loads do not import the legacy token again.

Migration uses the same named mutex as token refresh. It runs through the loader
hook and, for direct client construction, before authorization or refresh locks
are acquired. `TraktTokenHandler` subclasses the generic `TokenHandler` and
overrides only its settings access hooks. Core's shared token handler is unchanged.
Core retains the hidden legacy credential setting as a migration source; its
visible account controls are removed.

Credential migration requires TMDbHelper 6.20.5 and Trakt module 1.2.4 or later
to be updated together. TMDbHelper 6.20.6 and Trakt module 1.2.5 complete the
diagnostics migration and core cleanup. The module's minimum core dependency
remains 6.20.5, which provides all required interfaces. The provider interface
remains version 4; no new shared provider contract is introduced.

### Trakt diagnostics and artwork

The module's Diagnostics settings expose request logging and authorization
status. Its `diagnostics.py` owns request execution, response mapping, dialogs,
and report files. Small diagnostic subclasses share report handling and vary
the request or output mapping. `TraktDiagnosticFiles` inherits core's generic
`FileUtils` with the module's profile as its output directory. A successful empty
response is logged; failed or invalid responses do not produce a report.
Authorization diagnostics report authorization, refresh-token presence and
expiry without including access or refresh token values.

The existing core `log_request=trakt`, `test_func=trakt_response`,
`test_func=trakt_auth`, and `test_func=get_response_sync` commands remain forwarding
entry points. Arguments are JSON-encoded and URL-quoted before being passed to
the module script, so commas, Unicode and URL query strings remain intact.
Unavailable modules cause no request, setup prompt or fallback to a core client.
Core's TMDb logging and unrelated diagnostics retain their existing pipeline.

Trakt artwork, including type variants, is shipped only in the module. Core's
duplicate PNGs and its Trakt-only normal/type export definitions are removed;
shared icon generation and the remaining core icon families retain their
existing behavior. Shared directory mappers, calendar stacking, stats caching,
library tagging and persisted compatibility names remain core responsibilities.

## Ratings suppliers

In Sync settings, the Ratings group contains Providers and Priority. Providers
uses a multiselect to enable/disable installed suppliers. Priority uses select
dialogs to choose a provider and move it up/down. Save applies the order;
Cancel leaves it unchanged. Each control preserves the other's configuration.
Enabled Kodi modules with the ratings capability and available internal providers
appear independently of sync-provider selections. TMDb and OMDb supply movie and
TV-show ratings; season and episode suppliers are unchanged. OMDb uses the existing
API client and source mapper, preserving its ratings and awards fields. Its
supplier requires an IMDb ID and a configured API key before requesting data.
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

Provider results precede IMDb Top 250 in `rating_attribs`. TMDb and OMDb retrieval
belong to their internal suppliers, with no direct fallback in the ratings
dictionaries. Configured provider priority determines overlapping fields across
all suppliers, including OMDb ratings and awards. Lower-priority providers fill
missing fields.
The IMDb Top 250 output format remains unchanged. Service-specific rating
retrieval belongs to provider suppliers rather than the ratings dictionaries.

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
`user_slug` is `__api_<provider_id>__`. Providers own their list labels and retain
their saved identifiers for compatibility with `monitor_userlist` and
`monitor_userslug`.

`get_list_items(list_slug)` returns the normalized records expected by
LibraryBuilderUserList: each has `type` (`movie` or `show`) and a matching
`movie`/`show` dictionary containing `title` and `ids` (`tmdb` and `imdb`).
The module owns API requests and normalization.
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

Providers own their credentials and settings migrations. Core's API settings
page opens a module's settings through `open_sync_provider_settings`, using the
existing install/enable flow when needed. This does not select a sync provider.
The loader invokes the provider's `migrate_settings()` hook before API clients
are constructed. Credential migration must verify destination persistence before
clearing a legacy source. Module-specific settings and migration details belong
in the module's documentation.

## Browsing-only providers

`script.module.tmdbhelper.sync.tvdb` and
`script.module.tmdbhelper.sync.gemini` use interface version 4 with only the
`lists` capability. They own their API clients, settings, artwork, root entries,
directory properties and output mappers. Their script entry points use
`open_sync_provider_settings` to open API settings without assigning sync
features. Core has no reverse dependencies on these optional modules.

TVDb supplies awards and genres through `tvdb_directory`, `tvdb_awards`,
`tvdb_award_categories`, `tvdb_award_category`, `tvdb_genres` and `tvdb_genre`.
Gemini supplies `gemini_recommendations`. Core redirects legacy `dir_tvdb*`
and `gemini` routes to those names, preserving existing widget parameters and
the normal missing-provider install/enable flow.

Before creating API clients, Gemini migrates the legacy core API key and TVDb
migrates the legacy bearer token into module-owned storage. Migration verifies
the destination before clearing the legacy value and preserves existing module
credentials. TVDb retains its bundled key and supports an optional personal key.
Legacy credential values remain available to these migrations in Kodi's saved
settings without definitions in core's settings schema. Provider-only translations
belong to the module catalogs; shared labels and core settings buttons remain in
core.
The local awards database and its metadata consumers remain in core; browsing
does not change item-details database ownership or the finalisation pipeline.

## Provider module manager

Run `RunScript(plugin.video.themoviedb.helper,manage_provider_modules)` to manage
installed provider modules, including disabled third-party modules, and install
missing modules from the trusted catalogue. Selecting an entry installs, enables,
or disables it; the dialog refreshes after each action. The internal TMDb provider
is not an external module and is not listed.

Installing or enabling a module offers to make it the default sync provider.
Accepting replaces watched, watchlist, collection, and stats selections, clearing
unsupported selections. Ratings and scrobbling have separate prompts when
supported. Ratings priority and other scrobbling providers are preserved.
Providers offering only browsing do not receive these feature prompts.

Disabling requires OK/Cancel confirmation showing the module's active sync,
ratings, and scrobbling assignments. After Kodi confirms the module is disabled,
those assignments are removed through the existing settings interfaces. Cancelling
leaves the module and its configuration unchanged. Ratings cache contents retain
their normal expiry behaviour, as with the ratings-provider selector.

## External identifiers

Core obtains TMDb, IMDb, and TVDb IDs through
`FindQueriesDatabase.get_external_ids()`. It reads the item-details `unique_id`
metadata first and caches TMDb external-ID responses in `ItemQueries.db`.
Ratings use the parent show's IMDb ID for seasons and episodes. These readers
never request full item details from the detail service.

Episode-parent lookup reads cached episode relationships, then previously cached
TMDb external-ID responses, then TMDb's find endpoint using an IMDb or TVDb ID.
A bare TMDb episode ID with no cached relationship or external ID cannot be
reversed; monitor callers retain their title/external-ID fallback.

`tmdbhelper.lib.sync.providers.identifiers.IdentifierResolver` defines optional
provider enrichment. `IdentifierResolvers` gathers IDs from enabled, loadable
providers declaring `identifier_resolver_class`; the first nonempty value for a
key wins. The resolver returns a dictionary of unique-ID keys and values, using
`tvshow.` prefixes for parent-show IDs when enriching TV items. Public lookups
need not require an authorized account. Providers retain ownership of requests,
source mappings, and identifier caches. Network failures return no enrichment.

Player configuration checks enabled templates for `{trakt}`, `{slug}`,
`{eptrakt}`, or `{epslug}` before requesting provider enrichment. Existing item
IDs and TMDb IDs take precedence; missing/disabled providers leave generic IDs
available. Templates requiring provider-specific IDs need that provider.

The Trakt module owns `TraktIdentifiers.db`, including per-record expiry and
successful-query timestamps. A failed request leaves both unchanged; a successful
empty response records its query expiry. On first use it copies unexpired legacy
`trakt_id` rows from `ItemQueries.db`, preserving the source and recording a
one-time migration marker. Episode and show slugs are stored separately. Core no
longer owns the Trakt lookup or its cache. Updated provider callers use their own
identifier client. A temporary `get_trakt_id()` compatibility method delegates to
Trakt's resolver through its optional `get_id()` hook. When an enabled older
module lacks that resolver, the method shows the existing update warning once
per session and returns no result. It does not construct a Trakt API or cache.
Other provider features and the interface version remain unchanged.
