"""Composite directory artwork from original iconmonstr SVGs and XCF layers.

Development tool: requires Pillow, ImageMagick and a Roboto Black font file.
Run with --font /path/to/Roboto-Black.ttf; --output stages a preview elsewhere.
"""

import argparse
import io
import subprocess
from functools import cached_property
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ICON_ROOT = Path(__file__).resolve().parent
SIZE = 512
GLYPH_BOX = (160, 114)


class XcfLayers:
    def __init__(self, path):
        self.path = path

    @cached_property
    def indices(self):
        result = subprocess.run(
            ['magick', 'identify', '-format', '%s|%l\n', str(self.path)],
            check=True, capture_output=True, text=True)
        return {name: int(index) for index, name in (
            line.split('|', 1) for line in result.stdout.splitlines())}

    @cached_property
    def images(self):
        return {}

    def get(self, name):
        try:
            return self.images[name].copy()
        except KeyError:
            result = subprocess.run(
                ['magick', f'{self.path}[{self.indices[name]}]', 'png:-'],
                check=True, capture_output=True)
            image = Image.open(io.BytesIO(result.stdout)).convert('RGBA')
            self.images[name] = image
            return image.copy()


class SvgGlyphs:
    """Rasterize the original iconmonstr SVGs without modifying their geometry."""
    def __init__(self, directory):
        self.directory = directory

    @cached_property
    def masks(self):
        return {}

    def get(self, name):
        try:
            return self.masks[name].copy()
        except KeyError:
            mask = self.get_mask(name)
            self.masks[name] = mask
            return mask.copy()

    def get_mask(self, name):
        result = subprocess.run([
            'magick', '-background', 'none', '-density', '2304',
            str(self.directory / f'iconmonstr-{name}.svg'),
            '-resize', '192x192', 'png:-',
        ], check=True, capture_output=True)
        return Image.open(io.BytesIO(result.stdout)).convert('RGBA').getchannel('A')


class IconComposer:
    def __init__(self, font, output):
        self.font = font
        self.output = output
        self.xcf = XcfLayers(ICON_ROOT / 'icon.xcf')
        self.glyphs = SvgGlyphs(ICON_ROOT / 'iconmonstr')

    def get_canvas(self, family):
        if family == 'themoviedb':
            canvas = Image.open(ICON_ROOT / family / 'recommended.png').convert('RGBA')
            ImageDraw.Draw(canvas).rectangle((0, 0, 719, 470), fill=(13, 37, 63, 255))
            return canvas
        colors = {'tvdb': (27, 38, 38, 255)}
        if family in colors:
            return Image.new('RGBA', (SIZE, SIZE), colors[family])
        return self.xcf.get('Layer')

    def get_fill(self, family, size):
        if family in ('sync', 'common'):
            return self.xcf.get('Layer #2').crop((160, 114, 352, 306)).resize(size)
        if family == 'themoviedb':
            fill = Image.new('RGBA', size)
            draw = ImageDraw.Draw(fill)
            for x in range(size[0]):
                t = x / (size[0] - 1)
                color = tuple(round(a + (b - a) * t) for a, b in zip((106, 194, 197), (11, 181, 224)))
                draw.line((x, 0, x, size[1]), fill=(*color, 255))
            return fill
        color = {'trakt': (159, 66, 198), 'tvdb': (108, 213, 145)}[family]
        return Image.new('RGBA', size, (*color, 255))

    def add_footer(self, canvas, family, label):
        if family == 'trakt':
            canvas.alpha_composite(self.xcf.get('trakt-text-logo-dark.svg'), (172, 336))
        elif family == 'tvdb':
            source = Image.open(ICON_ROOT / family / 'tvdb.png').convert('RGBA')
            logo = source.crop((108, 170, 405, 340))
            logo.thumbnail((150, 80), Image.Resampling.LANCZOS)
            canvas.alpha_composite(logo, ((512 - logo.width) // 2, 332))
        elif family != 'themoviedb':
            font = ImageFont.truetype(self.font, 70)
            draw = ImageDraw.Draw(canvas)
            width = draw.textlength(label, font=font)
            if width > 400:
                font = ImageFont.truetype(self.font, int(70 * 400 / width))
            draw.text((256, 369), label, font=font, fill='white', anchor='mm')

    def build(self, family, filename, symbol, label=''):
        canvas = self.get_canvas(family)
        mask = self.glyphs.get(symbol)
        box = tuple(value * 5 // 4 for value in mask.size) if family == 'themoviedb' else mask.size
        position = ((canvas.width - box[0]) // 2, 206 if family == 'themoviedb' else GLYPH_BOX[1])
        mask = mask.resize(box, Image.Resampling.LANCZOS)
        fill = self.get_fill(family, box)
        fill.putalpha(ImageChops.multiply(fill.getchannel('A'), mask))
        canvas.alpha_composite(fill, position)
        self.add_footer(canvas, family, label)
        path = self.output / family / f'{filename}.png'
        path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(path, optimize=True)
        return path


# family, filename, single glyph source, footer text
ICONS = (
    ('sync', 'recentlywatched', 'time-8', 'history'),
    ('sync', 'mostwatched', 'award-5', 'most watched'),
    ('sync', 'up-next', 'arrow-right-alt-filled', 'up next'),
    ('sync', 'currentlywatching', 'media-control-1', 'watching'),
    ('sync', 'dropped', 'forbidden-1', 'dropped'),
    ('sync', 'recommended', 'thumb-1', 'recommended'),
    ('sync', 'recommended-mostwatched', 'trophy-5', 'recommended'),
    ('sync', 'calendar', 'calendar-2', 'airing next'),
    ('sync', 'watchlist-released', 'check-mark-4', 'watchlist'),
    ('sync', 'watchlist-anticipated', 'time-9', 'watchlist'),
    ('sync', 'towatch', 'bookmark-4', 'to watch'),
    ('common', 'calendar', 'calendar-4', 'calendar'),
    ('themoviedb', 'trending-day', 'chart-5', ''),
    ('themoviedb', 'trending-week', 'chart-20', ''),
    ('themoviedb', 'revenue', 'coin-10', ''),
    ('themoviedb', 'mostvoted', 'thumb-9', ''),
    ('themoviedb', 'studios', 'video-camera-1', ''),
    ('themoviedb', 'networks', 'radio-tower-1', ''),
    ('themoviedb', 'collection', 'layer-multiple-filled', ''),
    ('themoviedb', 'providers', 'television-1', ''),
    ('themoviedb', 'favorites', 'heart-filled', ''),
    ('themoviedb', 'rated', 'star-3', ''),
    ('themoviedb', 'watchlist', 'eye-3', ''),
    ('themoviedb', 'lists', 'text-bullet-list-lined', ''),
    ('themoviedb', 'user', 'user-19', ''),
    ('themoviedb', 'nodes', 'sitemap-1', ''),
    ('themoviedb', 'play', 'media-control-1', ''),
    ('themoviedb', 'groupings', 'layer-21', ''),
    ('themoviedb', 'calendar', 'calendar-4', ''),
    ('themoviedb', 'airingnext', 'calendar-2', ''),
    ('trakt', 'favorites', 'heart-filled', ''),
    ('trakt', 'viewers', 'user-29', ''),
    ('trakt', 'related', 'link-1', ''),
    ('trakt', 'comments', 'speech-bubble-2', ''),
    ('trakt', 'searchlists', 'magnifier-text-lined', ''),
    ('trakt', 'up-next', 'arrow-right-alt-filled', ''),
    ('trakt', 'groupings', 'layer-21', ''),
    ('tvdb', 'awards', 'award-5', ''),
    ('tvdb', 'genres', 'layer-21', ''),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', required=True, help='Path to Roboto-Black.ttf')
    parser.add_argument('--output', type=Path, default=ICON_ROOT)
    args = parser.parse_args()
    composer = IconComposer(args.font, args.output)
    for icon in ICONS:
        print(composer.build(*icon))


if __name__ == '__main__':
    main()
