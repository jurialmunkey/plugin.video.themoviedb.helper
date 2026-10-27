# Coding conventions

These guidelines apply throughout this repository. Match the existing architecture
when adding or extending functionality.

## Commit messages

- Prefix every commit subject with an appropriate emoji shortcode, matching the
  existing history (for example, `:bug:` for fixes, `:sparkles:` for new features,
  `:zap:` for improvements, `:bookmark:` for version bumps, and `:robot:` for
  agent instructions).
- Follow the shortcode with a space and a concise description of the change.

## Agree on the approach before implementation

- Before implementing changes involving item data, database access, or sync,
  inspect the affected data flow, relevant base classes, and callers. Identify
  which layer and class should own each part of the change.
- Present a concise proposed approach before editing implementation files. Name
  the modules/classes to change, their responsibilities, the extension points
  to use, and an existing implementation that demonstrates the relevant pattern.
  Explain how the proposal follows these conventions; proximity alone does not
  make an existing implementation an appropriate reference.
- Raise architectural questions early, with a recommended
  option and meaningful alternatives where applicable.
- Keep implementation within the agreed responsibilities and
  patterns.
- If new findings require changing the owning layer, shared abstraction, or
  agreed pattern, explain the proposed revision and obtain approval before
  implementing that deviation.

## Shared responsibility map

Paths below are relative to `resources/tmdbhelper/lib/`. Use this map when
proposing ownership of a change; a feature may require coordinated changes in
several layers, each retaining its own responsibility.

| Area | Responsibility |
| --- | --- |
| Directory containers in `items/directories/` | Configure lists and their parameters, select list properties, and use the existing finalisation pipeline. |
| Directory list properties in `items/directories/` | Obtain entries through the appropriate data interfaces, perform list-wide calculations, generate entries, and invoke the item mapper. |
| Directory mappers in `items/directories/` | Translate directory entries into list-item dictionaries, including labels, artwork, parameters, and skin-facing properties. |
| Sync getters in `sync/datasync.py` and provider subclasses | Query synced user data through the sync database interfaces. Keep sync queries separate from item-details cache queries. |
| `items/database/baseitem_factories/` | Retrieve and cache an individual item's detailed data, coordinate related metadata, and obtain its configured item output. |
| `items/database/basemeta_factories/` | Retrieve additional metadata from related tables, such as credits, genres, and artwork, and sync mapped data back to those tables. |
| `items/database/baseview_factories/` | Retrieve lists/views of item-details database data for directories, such as an item's cast or episodes. |
| `items/database/mappings.py` | Map source API data into the records used by the item-details database; also provide shared mapping helpers. |
| `items/database/itemmeta_factories/` | Map database data and related metadata into Kodi-facing details passed to the ListItem constructor. |
| `items/database/basedata.py` | Provide shared item-details database access and cache retrieval infrastructure used by the factory classes. |
| `items/database/listitem.py` | Coordinate list-item detail enrichment and caching through the existing factories. |
| `items/database/tabledef.py` and `items/database/database.py` | Define item-details storage structure, table configuration, database versions, and migrations. |

- Distinguish source API data -> database records, database records -> Kodi item
  details, and directory entries -> list-item dictionaries. These are separate
  mapping responsibilities even when classes share names such as ItemMapper.
- Keep query and persistence behavior in the appropriate database/sync layer.
  Properties classes request data through those interfaces; containers and
  output mappers must not take over database access or sync operations.
- Prefer the owning layer's existing configuration and extension points. Do not
  place feature logic in shared infrastructure merely because it is reachable
  from the caller. Resolve uncertain ownership during approach approval.

## Organization and reuse

- Always use explicitly named absolute imports. Relative imports and wildcard
  (`from ... import *`) imports are not permitted.
- Keep a distinct feature in its own appropriately named modules.
- Update routes in `addon/consts.py` and all imports when moving or renaming
  classes or modules. Remove unused imports and obsolete references.
- Prefer small subclasses for variations such as daily versus monthly stats.
  Override the differing query, date generation, or mapping behavior and inherit
  shared logic.
- Reuse `jurialmunkey.ftools.cached_property` and `jurialmunkey.parser.try_int`
  where applicable.
- Configure attributes before accessing cached properties. Treat cached results
  as belonging to one configured list instance.
- Implement object oriented programming (OOP) practices where practical. Create
  classes with properties. Use abstractions, inheritance, and subclassing.
- Follow EAFP programming principles. Avoid using "guards" to deal with errors
  arising from unexpected or misconfigured data. Never wallpaper over issues or
  mask the error, instead investigate underlying cause.
- Prefer flat structures. Avoid nesting loops. Prefer comprehensions if possible.
- Functions in classes should be simple, and have a single purpose. Avoid "god"
  functions/classes. Break complex code into smaller abstracted parts.
- When using cached properties, prefer `get_x():` type function which returns
  the data into the cached property rather than doing the work directly in the
  property function.

## Changes to shared classes

- Put feature-specific behavior in the appropriate concrete class or subclass.
  Modify a shared base class only when the behavior belongs to all affected
  subclasses; use existing extension points for variations.
- Before proposing a shared-class change, inspect its subclasses, overrides,
  and callers. Explain why the behavior belongs in the shared abstraction and
  how it affects existing consumers as part of approach approval.
- Preserve the shared class's contract. Do not add feature-specific branches to
  shared infrastructure to avoid implementing the appropriate subclass behavior.

## Containers, properties, and mappers

- Keep container classes focused on configuring a list and its parameters. Use
  `list_properties_class`, `configure_list_properties()`, and
  `get_items_finalised()` where the existing base classes provide them.
- Put data retrieval, list-wide calculations, and generation of entries in the
  properties class. Do not generate item dictionaries in the container class.
- Use a mapper class to translate each entry into a list-item dictionary.
  Properties classes should expose `item_mapper_class` and call it through
  `get_mapped_item(item, add_infoproperties=None)`.
- Construct mappers like the classes in `mapper_static.py`: inherit `ItemMapper`,
  accept its `meta` and `add_infoproperties` interface, expose derived values with
  `cached_property`, and override `get_infolabels()`, `get_infoproperties()`, and
  the other relevant mapping methods.
- Extend `super().get_item()` when adding fields such as `label2` or `is_folder`.
  Preserve the base mapper's handling of extra properties and dictionary cleanup.
- Store skin-facing `ListItem.Property(...)` values in `infoproperties`; use the
  existing list-item pipeline to apply them to Kodi items.

## Sync database getters

- Retrieve synced data through the existing sync database and getter interfaces.
  Keep SQL and sync operations out of containers and mappers.
- Add `SyncDataGetter...` subclasses consistent with `sync/datasync.py`. Declare
  `query_clauses` and `clause_keys`, provide a `query_values` property, and override
  `get_keys()` and `get_clause()` only where necessary.
- Reuse the inherited constructor and cached `.items` interface. Getter factory
  methods configure attributes such as `item_type`, `days`, or `months` before
  accessing cached properties. Use `get_item_type_getter()` for typed getters.
- Bind query values with SQL placeholders. Use the existing
  `cache.get_list_values(keys=..., values=..., conditions=...)` interface.
- Sync the underlying column names, not SQL expressions or aliases. For example,
  a getter selecting `COUNT(*)` and a date expression must still sync
  `last_watched_at`.


## Dates

- Use local calendar boundaries when grouping UTC watch timestamps. Use actual
  calendar months rather than assuming every month has 30 days.
- Reuse `addon/tmdate.py` helpers such as `convert_timestamp()`, `format_date_obj()`,
  `get_datetime_today()`, and `get_timedelta()`.
- Respect Kodi's regional long-date format and
  `Skin.String(TMDbHelper.Date.Format)` with the `%d %b %Y` fallback for custom
  date properties.
- Monthly entries use the first day of the month for their date properties.
  `week_number` means seven-day blocks within the month: days 1-7 are week 1,
  days 8-14 are week 2, and days 29-31 are week 5.

## Verification

- Before reporting completion, review the completed implementation diff against
  the approved approach and shared responsibility map. Check that each change
  belongs to its owning layer and follows the agreed extension points.
- Review mapping direction, factory registrations, routes, imports, and cache
  configuration order. Confirm that attributes are configured before cached
  properties are accessed and that output mapping preserves the base pipeline.
- For shared-class changes, review the effect on existing subclasses, overrides,
  and callers, including consumers outside the requested feature.
- Correct architectural violations before reporting completion. If a correction
  requires departing from the approved approach, obtain approval for that
  revision first. Briefly report the architectural review and any unresolved
  limitations alongside the verification results.
- Check syntax, whitespace, routes, and imports for affected modules. Use
  in-memory compilation when bytecode writes are unavailable.
- For aggregation or date changes, verify meaningful cases: separate movie/TV
  counts, exclusion of parent rows, range boundaries, zero totals, missing
  periods, month ends, year rollover, and leap years.
- Preserve existing behavior unless the requested change calls for altering it.
  State which checks ran and distinguish isolated checks from testing in Kodi.
- Never write tests in files in the codebase.
