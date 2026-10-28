# Directory icon sources

`build_directory_icons.py` composites the directory replacements from original
[iconmonstr](https://iconmonstr.com/) SVGs, the named layers in `icon.xcf`, and
existing provider footers. The XCF supplies the background, sync gradient and
Trakt wordmark. All replacement glyphs come from iconmonstr; their geometry is
preserved when rasterizing them.

`iconmonstr/` contains the original SVGs used by the exported assets.
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
palette and TMDb footer. TVDb category icons retain their background and
provider footer. MDbList artwork, including type variants, is shipped in
`script.module.tmdbhelper.sync.mdblist/resources/icons/mdblist/` and is no longer
part of these core build manifests. Shared calendar period selectors use the
neutral `common/calendar.png` because both library and Trakt routes use them.

The normal icons retain their single centred glyph. Trakt Discover uses the
existing `trakt/trakt.png` provider logo directly.

## Type variants in mixed menus

`build_directory_variants.py` builds the separately named `-movie`, `-tv`,
`-person`, `-season`, `-episode` and `-both` PNGs registered in
`resources/tmdbhelper/lib/items/directories/base/artwork.py`:

```sh
python resources/icons/build_directory_variants.py
python resources/icons/build_directory_variants.py --output /path/to/preview
```

This tool subclasses the existing compositor and reuses the saved normal PNGs
as source artwork, including their backgrounds, provider branding and labels.
Existing type glyphs come from `themoviedb/movies.png`, `tv.png`, `cast.png`,
`groupings.png` (seasons) and `episodes.png`. Combined entries use one screen-with-play
symbol composed from the existing `television-1` and `media-control-1` SVG masks.
All main glyphs fit the same square icon box with preserved proportions and a
fixed horizontal and vertical centre. Gradients and solid fills follow each
provider's palette.

The category glyph sits inside a background-coloured circular badge with a
coloured rim and the approved downward soft shadow. The inset is approximately
12.5% smaller than the initial mockup, with additional radial padding for square
glyphs. The badge position is a fixed layout anchor, independent of the main
glyph's visible bounds. Glyph masks
are recovered from the saved artwork while retaining its antialiasing; rendering
at three times the final dimensions smooths the circle and rim. Saved text and
provider branding are extracted and centred at a fixed text anchor. Compositing
always follows background, text, main icon, then badge (including its shadow);
no footer is pasted over the completed badge. `CompositeLayout` defines one
proportional grid; `TMDbCompositeLayout` scales it to 720px. Coordinates are
rounded only for rasterization:

| Output | Icon box / centre | Text centre | Badge centre / diameter |
| --- | --- | --- | --- |
| 512px | 192px / (256, 210) | (256, 369) | (352, 275) / 100px |
| 720px | 270px / (360, 295) | (360, 519) | (495, 387) / 141px |

This build requires Pillow and
ImageMagick 7, but no font file, network access or new icon downloads.

The manifest is shared with the menu artwork selector so every selectable
variant has an exported file. `BaseDirList` requests these variants only when a
menu displays multiple content types. Group headers, groups containing a single
type, and Movies/TV/People directories retain their normal icons. Artwork
selection does not change item labels, route parameters, sorting or sync queries.
Single-type TVDb menus retain their normal artwork.

Existing `sync/up-next.png`, `trakt/up-next.png` and `trakt/groupings.png` paths
are preserved with rebuilt artwork. In particular, `UpNextSeason.map_item_art()`
uses the sync asset for both thumbnail and poster. Other older duplicate files
remain available for external consumers; do not remove them solely because an
internal directory no longer selects them.
