"""Build type-specific directory artwork without replacing the normal icons.

Run from the add-on root with Python, Pillow and ImageMagick 7.
Use --output to stage the family subdirectories outside resources/icons.
"""

import argparse
import math
import sys
from functools import cached_property
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ICON_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ICON_ROOT.parent))

from build_directory_icons import IconComposer
from tmdbhelper.lib.items.directories.base.artwork import DIRECTORY_ICON_VARIANTS, get_directory_icon_variant


SCALE = 3


class CompositeLayout:
    canvas_size = 512

    def get_scaled(self, value):
        return round(value * self.canvas_size / 512)

    @property
    def icon_size(self):
        return self.get_scaled(192)

    @property
    def icon_center(self):
        return tuple(self.get_scaled(value) for value in (256, 210))

    @property
    def text_center(self):
        return tuple(self.get_scaled(value) for value in (256, 369))

    @property
    def badge_center(self):
        return tuple(self.get_scaled(value) for value in (352, 275))

    @property
    def badge_diameter(self):
        return self.get_scaled(100)

    @property
    def rim_width(self):
        return self.get_scaled(8)

    @property
    def shadow_offset(self):
        return self.get_scaled(6)

    @property
    def shadow_blur(self):
        return 6.4 * self.canvas_size / 512


class TMDbCompositeLayout(CompositeLayout):
    canvas_size = 720


class SourceArtwork:
    """Keep the saved artwork's geometry, colours, backgrounds and footers."""

    def __init__(self, path):
        self.path = path

    @cached_property
    def image(self):
        return Image.open(self.path).convert('RGBA')

    @cached_property
    def background(self):
        return self.image.getpixel((0, 0))

    @cached_property
    def glyph_area(self):
        bottom = 471 if self.image.width == 720 else 324
        return self.image.crop((0, 0, self.image.width, bottom))

    @cached_property
    def bounds(self):
        background = Image.new('RGB', self.glyph_area.size, self.background[:3])
        return ImageChops.difference(self.glyph_area.convert('RGB'), background).getbbox()

    @cached_property
    def glyph(self):
        return self.glyph_area.crop(self.bounds)

    @cached_property
    def text(self):
        return self.get_text()

    def get_text(self):
        area = self.image.crop((0, self.glyph_area.height, self.image.width, self.image.height))
        background = Image.new('RGB', area.size, self.background[:3])
        bounds = ImageChops.difference(area.convert('RGB'), background).getbbox()
        return area.crop(bounds)

    @cached_property
    def mask(self):
        return self.get_mask()

    def get_mask(self):
        # Nearby interior colours recover the saved glyph's antialiasing without
        # confusing its gradient with alpha. Uniform background pixels stay clear.
        pixels = self.glyph.convert('RGB')
        expanded = pixels.filter(ImageFilter.MaxFilter(7))
        mask = Image.new('L', pixels.size)
        mask.putdata([
            self.get_alpha(pixel, fill)
            for pixel, fill in zip(pixels.getdata(), expanded.getdata())
        ])
        return mask

    def get_alpha(self, pixel, fill):
        actual = tuple(value - bg for value, bg in zip(pixel, self.background))
        if not any(actual):
            return 0
        expected = tuple(value - bg for value, bg in zip(fill, self.background))
        denominator = sum(value * value for value in expected)
        alpha = sum(a * b for a, b in zip(actual, expected)) / denominator
        return 255 if alpha >= 0.97 else max(0, round(alpha * 255))


class TypeArtwork:
    paths = {
        'movie': 'movies',
        'tv': 'tv',
        'person': 'cast',
        'season': 'groupings',
        'episode': 'episodes',
    }

    def __init__(self, glyphs):
        self.glyphs = glyphs

    @cached_property
    def sources(self):
        return {
            item_type: SourceArtwork(ICON_ROOT / 'themoviedb' / f'{name}.png')
            for item_type, name in self.paths.items()
        }

    def get(self, item_type):
        return self.sources[item_type]

    @cached_property
    def combined_mask(self):
        return self.get_combined_mask()

    def get_combined_mask(self):
        screen = self.glyphs.get('television-1')
        screen = screen.crop(screen.getbbox())
        play = self.glyphs.get('media-control-1')
        play = play.crop(play.getbbox()).resize((48, 58), Image.Resampling.LANCZOS)
        inset = Image.new('L', screen.size)
        position = (screen.width // 2 - play.width // 2, 64 - play.height // 2)
        inset.paste(play, position)
        return ImageChops.lighter(screen, inset)

    def get_mask(self, item_type):
        return self.combined_mask if item_type == 'both' else self.get(item_type).mask


class DirectoryVariantComposer(IconComposer):
    """Concrete compositor for the approved centred type and rimmed badge style."""

    def __init__(self, output):
        super().__init__('', output)
        self.types = TypeArtwork(self.glyphs)

    @cached_property
    def sources(self):
        return {}

    def get_source(self, path):
        try:
            return self.sources[path]
        except KeyError:
            source = SourceArtwork(path)
            self.sources[path] = source
            return source

    def get_layout(self, family):
        return TMDbCompositeLayout() if family == 'themoviedb' else CompositeLayout()

    def get_fill(self, family, size):
        if family == 'themoviedb':
            return self.get_gradient(self.types.get('movie'), size)
        return super().get_fill(family, size)

    def get_gradient(self, source, size):
        # Recover the original palette from solid portions of the saved artwork.
        top = source.glyph.getpixel((source.glyph.width - 2, 2))
        bottom = source.glyph.getpixel((2, source.glyph.height - 3))
        fill = Image.new('RGBA', size)
        draw = ImageDraw.Draw(fill)
        for y in range(size[1]):
            t = y / (size[1] - 1)
            color = tuple(round(a + (b - a) * t) for a, b in zip(top[:3], bottom[:3]))
            draw.line((0, y, size[0], y), fill=(*color, 255))
        return fill

    def get_type_glyph(self, family, item_type, icon_size):
        mask = self.types.get_mask(item_type)
        scale = icon_size * SCALE / max(mask.size)
        size = tuple(round(value * scale) for value in mask.size)
        mask = mask.resize(size, Image.Resampling.LANCZOS)
        fill = self.get_fill(family, size)
        fill.putalpha(mask)
        return fill

    def add_centered(self, canvas, image, center):
        position = tuple(value * SCALE - dimension // 2 for value, dimension in zip(center, image.size))
        canvas.alpha_composite(image, position)

    def add_text(self, canvas, source, family):
        text = source.text.resize(tuple(value * SCALE for value in source.text.size), Image.Resampling.LANCZOS)
        self.add_centered(canvas, text, self.get_layout(family).text_center)

    def add_main(self, canvas, family, item_type):
        layout = self.get_layout(family)
        glyph = self.get_type_glyph(family, item_type, layout.icon_size)
        self.add_centered(canvas, glyph, layout.icon_center)

    def add_badge_shadow(self, canvas, family, bounds):
        layout = self.get_layout(family)
        left, top, right, bottom = bounds
        mask = Image.new('L', canvas.size)
        shadow_bounds = (left, top + layout.shadow_offset, right, bottom + layout.shadow_offset)
        ImageDraw.Draw(mask).ellipse(tuple(value * SCALE for value in shadow_bounds), fill=110)
        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(layout.shadow_blur * SCALE)))
        canvas.alpha_composite(shadow)

    def get_badge_face(self, source, family, diameter):
        size = (diameter * SCALE, diameter * SCALE)
        bounds = (0, 0, size[0] - 1, size[1] - 1)
        circle = Image.new('L', size)
        ImageDraw.Draw(circle).ellipse(bounds, fill=255)
        face = Image.new('RGBA', size, source.background)
        face.putalpha(circle)
        mask = Image.new('L', size)
        ImageDraw.Draw(mask).ellipse(bounds, outline=255, width=self.get_layout(family).rim_width)
        rim = self.get_fill(family, size)
        rim.putalpha(mask)
        face.alpha_composite(rim)
        return face

    def get_badge_glyph(self, source, family, diameter):
        mask = source.mask
        # Preserve the approved inset size; square/wide glyphs also need enough
        # radial padding so their corners do not crowd the circular rim.
        scale = min(diameter * (84 / 124) / max(mask.size), diameter * 0.85 / math.hypot(*mask.size))
        size = tuple(round(value * scale * SCALE) for value in mask.size)
        mask = mask.resize(size, Image.Resampling.LANCZOS)
        fill = self.get_fill(family, size)
        fill.putalpha(mask)
        return fill

    def add_badge(self, canvas, source, family, center):
        diameter = self.get_layout(family).badge_diameter
        left, top = (value - diameter // 2 for value in center)
        self.add_badge_shadow(canvas, family, (left, top, left + diameter, top + diameter))
        canvas.alpha_composite(self.get_badge_face(source, family, diameter), (left * SCALE, top * SCALE))
        glyph = self.get_badge_glyph(source, family, diameter)
        position = (center[0] * SCALE - glyph.width // 2, center[1] * SCALE - glyph.height // 2)
        canvas.alpha_composite(glyph, position)

    def build_variant(self, icon, item_type):
        source = self.get_source(ICON_ROOT.parent.parent / icon)
        family = source.path.parent.name
        layout = self.get_layout(family)
        canvas = Image.new('RGBA', (layout.canvas_size * SCALE,) * 2, source.background)
        self.add_text(canvas, source, family)
        self.add_main(canvas, family, item_type)
        self.add_badge(canvas, source, family, layout.badge_center)
        canvas = canvas.resize(source.image.size, Image.Resampling.LANCZOS)
        variant = get_directory_icon_variant(icon, item_type)
        path = self.output / Path(variant).relative_to('resources/icons')
        path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(path, optimize=True)
        return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ICON_ROOT)
    args = parser.parse_args()
    composer = DirectoryVariantComposer(args.output)
    variants = (
        (icon, item_type)
        for icon, item_types in DIRECTORY_ICON_VARIANTS.items()
        for item_type in item_types
    )
    for icon, item_type in variants:
        print(composer.build_variant(icon, item_type))


if __name__ == '__main__':
    main()
