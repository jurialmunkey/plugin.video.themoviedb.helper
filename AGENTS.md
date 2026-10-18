# Coding conventions

These guidelines apply throughout this repository. Match the existing architecture
and the style of nearby classes when adding or extending functionality.

## Organization and reuse

- Keep a distinct feature in its own appropriately named modules.
- Update routes in `addon/consts.py` and all imports when moving or renaming
  classes or modules. Remove unused imports and obsolete references.
- Prefer small subclasses for variations such as daily versus monthly stats.
  Override the differing query, date generation, or mapping behavior and inherit
  shared logic.
- Follow local naming, indentation, import, tuple, and method conventions. Reuse
  `jurialmunkey.ftools.cached_property` and `jurialmunkey.parser.try_int` where
  surrounding code does so.
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

- Check syntax, whitespace, routes, and imports for affected modules. Use
  in-memory compilation when bytecode writes are unavailable.
- For aggregation or date changes, verify meaningful cases: separate movie/TV
  counts, exclusion of parent rows, range boundaries, zero totals, missing
  periods, month ends, year rollover, and leap years.
- Preserve existing behavior unless the requested change calls for altering it.
  State which checks ran and distinguish isolated checks from testing in Kodi.
- Never write tests in files in the codebase.
