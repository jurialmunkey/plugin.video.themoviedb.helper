# Directory icon sources

`build_directory_icons.py` composites the directory replacements from original
[iconmonstr](https://iconmonstr.com/) SVGs, the named layers in `icon.xcf`, and
existing provider footers. The XCF supplies the background, sync gradient and
Trakt wordmark. All replacement glyphs come from iconmonstr; their geometry is
preserved when rasterizing them.

`iconmonstr/` contains the 34 original SVGs used by the 45 exported assets.
`iconmonstr/sources.json` records each source page and file checksum. Icons are by
Alexander Kahlkopf / iconmonstr; see the
[iconmonstr license](https://iconmonstr.com/license/).

Colours, gradients, backgrounds, output dimensions, positioning and footers are
applied deterministically by the compositor. Rebuilding uses the saved source
SVGs and does not require a network connection.

The build tool requires Python 3.8+, Pillow, ImageMagick 7 (`magick` on `PATH`), and
Roboto Black (`Roboto-Black.ttf`, matching the XCF's text layer). These are artwork
development dependencies, not additional Kodi runtime requirements.

From the add-on root:

```sh
python resources/icons/build_directory_icons.py --font /path/to/Roboto-Black.ttf
```

Pass `--output /path/to/preview` to stage the same family subdirectories without
replacing installed icons. The `ICONS` manifest lists every exported asset, its
single iconmonstr source name and footer. Outputs are 512px RGBA PNGs, or 720px for
TMDb to match that existing family. Rebuilding preserves the source SVGs, XCF,
existing provider logos and reference artwork.

Sync icons use the XCF's blue-to-purple gradient and a function label. Trakt icons
use the purple glyph fill and XCF wordmark. TMDb icons retain the existing cyan
palette and TMDb footer. MDbList and TVDb category icons retain their respective
backgrounds and provider footers. Shared calendar period selectors use the
neutral `common/calendar.png` because both library and Trakt routes use them.

Each icon has one iconmonstr glyph in the standard centred position and size.
There are no companion symbols, inset badges or overlays added by the compositor.
Trakt Discover uses the existing `trakt/trakt.png` provider logo directly.

Existing `sync/up-next.png`, `trakt/up-next.png` and `trakt/groupings.png` paths
are preserved with rebuilt artwork. In particular, `UpNextSeason.map_item_art()`
uses the sync asset for both thumbnail and poster. Other older duplicate files
remain available for external consumers; do not remove them solely because an
internal directory no longer selects them.
