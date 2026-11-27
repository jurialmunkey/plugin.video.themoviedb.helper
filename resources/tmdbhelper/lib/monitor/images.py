import os
import io
import xbmcvfs
import colorsys
import hashlib
import re
from functools import partial
from xbmc import skinHasImage, Monitor
from tmdbhelper.lib.addon.plugin import get_infolabel, get_condvisibility, IMAGECACHE, ADDON
from tmdbhelper.lib.monitor.imagecycle import ImageArtworkCycle
from jurialmunkey.window import WindowPropertySetter
from jurialmunkey.parser import try_int, try_float
from tmdbhelper.lib.files.futils import make_path
from tmdbhelper.lib.addon.thread import SafeThread
from urllib.parse import quote
from tmdbhelper.lib.addon.logger import kodi_log

CROPIMAGE_SOURCE = "Art(artist.clearlogo)|Art(tvshow.clearlogo)|Art(clearlogo)"

ARTWORK_LOOKUP_TABLE = {
    'poster': ['Art(tvshow.poster)', 'Art(poster)', 'Art(thumb)'],
    'fanart': ['Art(fanart)', 'Art(thumb)'],
    'landscape': ['Art(landscape)', 'Art(fanart)', 'Art(thumb)'],
    'thumb': ['Art(thumb)']}

# Extra artwork slots that can be enabled in settings mapped to their x position in e.g. "Art(fanart{x})"
EXTRAFANART_SLOTS = {
    'fanart1': 1,
    'fanart2': 2,
    'fanart3': 3,
    'fanart4': 4,
    'fanart5': 5,
    'fanart6': 6,
    'fanart7': 7,
    'fanart8': 8,
    'fanart9': 9,
}

# PIL causes issues (via numpy) on Linux systems using python versions higher than 3.8.5
# Lazy import PIL to avoid using it unless user requires ImageFunctions
ImageFilter, ImageDraw, Image = None, None, None


def lazyimport_pil(func):
    def wrapper(*args, **kwargs):
        global ImageFilter
        if ImageFilter is None:
            from PIL import ImageFilter
        return func(*args, **kwargs)
    return wrapper


def md5hash(value):
    value = str(value).encode(errors='surrogatepass')  # Use surrogatepass to avoid emoji in filenames raising exceptions for utf-8
    return hashlib.md5(value).hexdigest()


def _imageopen(image):
    global Image
    if Image is None:
        from PIL import Image
    with xbmcvfs.File(image, 'rb') as f:
        image_bytes = f.readBytes()
    return Image.open(io.BytesIO(image_bytes))


def _add_corners(image, destination, radius=40, aa_factor=4):
    global ImageDraw
    if ImageDraw is None:
        from PIL import ImageDraw

    global Image
    if Image is None:
        from PIL import Image

    image = image.copy()

    diameter = radius * 2
    aaresize = diameter * aa_factor

    circle = Image.new('L', (aaresize, aaresize), 0)

    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, aaresize, aaresize), fill=255)

    circle = circle.resize((diameter, diameter), Image.LANCZOS)

    alpha = Image.new('L', image.size, "white")
    w, h = image.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, diameter)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, diameter, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, diameter, diameter)), (w - radius, h - radius))
    image.putalpha(alpha)

    _saveimage_png(image, destination)
    image.close()


def _add_tile(image, destination):
    global Image
    if Image is None:
        from PIL import Image

    w, h = image.size
    image_tile = Image.new('RGB', (w * 2, h * 2))

    # Top Right
    image_flip = image.copy()
    image_tile.paste(image_flip, (w, 0))

    # Bottom Right
    image_flip = image_flip.transpose(Image.FLIP_TOP_BOTTOM)
    image_tile.paste(image_flip, (w, h))

    # Bottom Left
    image_flip = image_flip.transpose(Image.FLIP_LEFT_RIGHT)
    image_flip = image_flip.resize((w * 2, h), Image.BILINEAR)
    image_flip = image_flip.crop((w, 0, w * 2, h))
    image_tile.paste(image_flip, (0, h))

    # Top Left
    image_flip = image_flip.transpose(Image.FLIP_TOP_BOTTOM)
    image_tile.paste(image_flip, (0, 0))

    _saveimage_jpeg(image_tile, destination)

    image_flip.close()
    image_tile.close()


def _get_wrapped_image(image):
    """ Wrap source in image:// so that opening it caches the source in Kodi's texture cache """
    if image.startswith('image://'):
        return image
    return f'image://{quote(image, safe="")}/'


def _openimage(image):
    """ Open skin images directly and all other images via Kodi's texture cache """
    if not skinHasImage(image):
        return _imageopen(_get_wrapped_image(image))
    if '://' not in image and not os.path.isabs(image):
        image = os.path.join('special://skin/media/', image)
    return _imageopen(xbmcvfs.translatePath(image))


def _get_crop_bbox(img):
    """ Get bounding box of visible area for cropping """
    if 'A' in img.getbands():
        # Visible area is wherever alpha is non-zero
        return img.getchannel('A').getbbox()
    try:
        # Errors with single channel L conversion to RGBa so catch exceptions
        return img.convert('RGBa').getbbox()
    except Exception:
        # If we get a conversion error just try getting bounding box with current channel
        # We'll probably be okay with single channel texture since Kodi now handles these better
        return img.getbbox()


def _saveimage(image, targetfile, image_format='PNG', **kwargs):
    """ Save image object to disk
    Uses flush() and os.fsync() to ensure file is written to disk before continuing
    Used to prevent Kodi from attempting to cache the image before writing is complete
    """
    with xbmcvfs.File(targetfile, 'wb') as f:
        image.save(f, image_format, **kwargs)
        # f.flush()
        # os.fsync(f)


def _saveimage_jpeg(image, targetfile):
    """ Save image object without alpha channel as JPEG for faster encoding and decoding """
    _saveimage(image, targetfile, image_format='JPEG', quality=90)


def _saveimage_png(image, targetfile):
    """ Save image object as PNG with low compression for faster encoding """
    _saveimage(image, targetfile, image_format='PNG', compress_level=1)


class ImageFunctions(SafeThread, WindowPropertySetter):
    save_path = f'{IMAGECACHE}{{}}/'
    blur_size = try_int(get_infolabel('Skin.String(TMDbHelper.Blur.Size)')) or 480
    crop_size = (800, 310)
    radius = try_int(get_infolabel('Skin.String(TMDbHelper.Blur.Radius)')) or 40
    corner = try_int(get_infolabel('Skin.String(TMDbHelper.Corner.Radius)')) or 20
    blur_scale = max(1, min(4, radius // 10))  # Heavy blurs are processed at reduced size then scaled back up
    blur_work_size = blur_size // blur_scale

    def __init__(self, method=None, artwork=None, is_thread=True, prefix='ListItem'):
        if is_thread:
            SafeThread.__init__(self)
        self.image = artwork
        self.func = None
        self.save_orig = False
        self.save_prop = None
        if method == 'blur':
            self.func = self.blur
            self.save_path = make_path(self.save_path.format('blur'))
            self.save_prop = f'{prefix}.BlurImage'
            self.save_orig = True
        elif method == 'crop':
            self.func = self.crop
            self.save_path = make_path(self.save_path.format('crop'))
            self.save_prop = f'{prefix}.CropImage'
            self.save_orig = True
        elif method == 'desaturate':
            self.func = self.desaturate
            self.save_path = make_path(self.save_path.format('desaturate'))
            self.save_prop = f'{prefix}.DesaturateImage'
            self.save_orig = True
        elif method == 'colors':
            self.func = self.colors
            self.save_path = make_path(self.save_path.format('colors'))
            self.save_prop = f'{prefix}.Colors'

    def run(self):
        if not self.save_prop or not self.func:
            return
        output = self.func(self.image) if self.image else None
        self.set_properties(output)

    def set_properties(self, output):
        if not output:
            self.get_property(self.save_prop, clear_property=True)
            self.get_property(f'{self.save_prop}.Original', clear_property=True) if self.save_orig else None
            return
        self.get_property(self.save_prop, output)
        self.get_property(f'{self.save_prop}.Original', self.image) if self.save_orig else None

    def clamp(self, x):
        return max(0, min(x, 255))

    @lazyimport_pil
    def crop(self, source):
        if not source:
            return ''
        filename = f'cropped-{md5hash(source)}.png'
        destination = os.path.join(self.save_path, filename)
        try:
            if not xbmcvfs.exists(destination):  # Used to do os.utime(destination, None) on existing here
                img = _openimage(source)
                img = img.crop(_get_crop_bbox(img))
                img.thumbnail(self.crop_size)
                _saveimage_png(img, destination)
                img.close()

            return destination

        except Exception as exc:
            kodi_log(f'Crop Error:\n{source}\n{destination}\n{exc}', 2)
            return ''

    @lazyimport_pil
    def blur(self, source):
        filename = f'{md5hash(source)}-{self.radius}-{self.blur_size}.jpg'
        destination = os.path.join(self.save_path, filename)
        diffuse_destination = os.path.join(self.save_path, f'{filename}-diffuse-{self.corner}.jpg') if self.corner else None
        tile_destination = os.path.join(self.save_path, f'{filename}-tiled.jpg')
        try:
            if not xbmcvfs.exists(destination) or (diffuse_destination and not xbmcvfs.exists(diffuse_destination)):  # os.utime(destination, None)
                img = _openimage(source)
                img.draft(None, (self.blur_work_size, self.blur_work_size))  # JPEG sources decode directly at reduced scale
                img.thumbnail((self.blur_work_size, self.blur_work_size))
                img = img.convert('RGB')
                img = img.filter(ImageFilter.GaussianBlur(self.radius / self.blur_scale))
                img = img.resize((img.width * self.blur_scale, img.height * self.blur_scale), Image.BILINEAR)
                _saveimage_jpeg(img, destination)

                if diffuse_destination:
                    _add_corners(img, diffuse_destination, radius=self.corner)

                if tile_destination:
                    _add_tile(img, tile_destination)

                img.close()

            return destination

        except Exception:
            return ''

    @lazyimport_pil
    def desaturate(self, source):
        filename = f'{md5hash(source)}.png'
        destination = os.path.join(self.save_path, filename)
        try:
            if not xbmcvfs.exists(destination):  # os.utime(destination, None)
                img = _openimage(source)
                img = img.convert('LA')
                _saveimage_png(img, destination)
                img.close()

            return destination

        except Exception:
            return ''

    def get_maincolor(self, img):
        """Returns main color of image as list of rgb values 0:255"""
        rgb_list = [None, None, None]
        for channel in range(3):
            pixels = img.getdata(band=channel)
            values = [pixel for pixel in pixels]
            rgb_list[channel] = self.clamp(sum(values) / len(values))
        return rgb_list

    def get_compcolor(self, r, g, b, shift=0.33):
        """
        Changes hue of color by shift value (percentage float)
        Takes RGB as 0:255 values and returns RGB as 0:255 values
        """
        hls_tuple = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        rgb_tuple = colorsys.hls_to_rgb(abs(hls_tuple[0] - shift), hls_tuple[1], hls_tuple[2])
        return self.rgb_to_int(*rgb_tuple)

    def get_color_lumsat(self, r, g, b):
        hls_tuple = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        hue = hls_tuple[0]
        lum = try_float(get_infolabel('Skin.String(TMDbHelper.Colors.Luminance)')) or hls_tuple[1]
        sat = try_float(get_infolabel('Skin.String(TMDbHelper.Colors.Saturation)')) or hls_tuple[2]
        return self.rgb_to_int(*colorsys.hls_to_rgb(hue, lum, sat))

    def rgb_to_int(self, r, g, b):
        return [try_int(self.clamp(i * 255)) for i in [r, g, b]]

    def rgb_to_hex(self, r, g, b):
        return f'FF{r:02x}{g:02x}{b:02x}'

    def hex_to_rgb(self, colorhex):
        r = try_int(colorhex[2:4], 16)
        g = try_int(colorhex[4:6], 16)
        b = try_int(colorhex[6:8], 16)
        return [r, g, b]

    def set_prop_colorgradient(self, propname, start_hex, end_hex, checkprop):
        if not start_hex or not end_hex:
            return

        steps = 20

        rgb_a = self.hex_to_rgb(start_hex)
        rgb_z = self.hex_to_rgb(end_hex)

        inc_r = (rgb_z[0] - rgb_a[0]) // steps
        inc_g = (rgb_z[1] - rgb_a[1]) // steps
        inc_b = (rgb_z[2] - rgb_a[2]) // steps

        val_r = rgb_a[0]
        val_g = rgb_a[1]
        val_b = rgb_a[2]

        for i in range(steps):
            if self.get_property(checkprop) != start_hex:
                return
            hex_value = self.rgb_to_hex(val_r, val_g, val_b)
            self.get_property(propname, set_property=hex_value)
            val_r = val_r + inc_r
            val_g = val_g + inc_g
            val_b = val_b + inc_b
            Monitor().waitForAbort(0.05)

        self.get_property(propname, set_property=end_hex)
        return end_hex

    def colors(self, source):
        colors = self.get_colors(source)
        if not colors:
            return ''
        self.set_colors_properties(*colors)
        return colors[0]

    @lazyimport_pil
    def get_colors(self, source):
        """ Returns main and complementary colors of image as hex values """
        filename = f'{md5hash(source)}.png'
        destination = self.save_path + filename

        try:
            if xbmcvfs.exists(destination):  # os.utime(destination, None)
                img = _imageopen(xbmcvfs.translatePath(destination))
            else:
                img = _openimage(source)
                img.thumbnail((128, 128))
                img = img.convert('RGB')
                _saveimage_png(img, destination)

            maincolor_rgb = self.get_maincolor(img)
            maincolor_hex = self.rgb_to_hex(*self.get_color_lumsat(*maincolor_rgb))
            compcolor_rgb = self.get_compcolor(*maincolor_rgb)
            compcolor_hex = self.rgb_to_hex(*self.get_color_lumsat(*compcolor_rgb))

            img.close()
            return (maincolor_hex, compcolor_hex)

        except Exception as exc:
            kodi_log(exc, 1)
            return

    def set_colors_properties(self, maincolor_hex, compcolor_hex):
        self.set_color_property(f'{self.save_prop}.Main', maincolor_hex)
        self.set_color_property(f'{self.save_prop}.Comp', compcolor_hex)

    def set_color_property(self, propname, color_hex):
        """ Set color immediately if unset otherwise fade from current color in background """
        current_hex = self.get_property(propname)
        if not current_hex:
            self.get_property(propname, set_property=color_hex)
            return
        checkprop = f'{propname}Check'
        self.get_property(checkprop, set_property=current_hex)
        SafeThread(target=self.set_prop_colorgradient, args=[propname, current_hex, color_hex, checkprop]).start()


class ImageArtworkGetter():
    def __init__(self, parent, source, prebuilt_artwork=None):
        self._parent = parent
        self._source = source
        self.prebuilt_artwork = prebuilt_artwork

    @property
    def infolabels(self):
        try:
            return self._infolabels
        except AttributeError:
            self._infolabels = self.get_infolabels()
            return self._infolabels

    def get_infolabels(self):
        if not self._source:
            return ARTWORK_LOOKUP_TABLE.get('thumb')
        return ARTWORK_LOOKUP_TABLE.get(self._source, self._source.split("|"))

    @property
    def built_artwork(self):
        try:
            return self._built_artwork
        except AttributeError:
            self._built_artwork = self.get_built_artwork()
            return self._built_artwork

    def get_built_artwork(self):
        return self.prebuilt_artwork or self._parent.get_builtartwork()

    @property
    def artwork(self):
        try:
            return self._artwork
        except AttributeError:
            self._artwork = self.get_artwork()
            return self._artwork

    def get_artwork(self):
        return next((j for j in (self.get_artwork_item(i) for i in self.infolabels) if j), None)

    @property
    def artwork_fallback(self):
        try:
            return self._artwork_fallback
        except AttributeError:
            self._artwork_fallback = self.get_artwork_fallback()
            return self._artwork_fallback

    def get_artwork_fallback(self):
        return next((j for j in (self.get_artwork_item(i, prebuilt=True) for i in self.infolabels) if j), None)

    def get_artwork_item(self, item, prebuilt=False):
        # Check if we're getting a cycled x position item e.g. "Art(fanart{x})"
        if '{x}' not in item:
            return self.get_artwork_slot(item, prebuilt=prebuilt)
        return self._parent.get_cycled_artwork(
            (item, prebuilt),
            self._parent.get_extrafanart_slots,
            partial(self.get_artwork_slot, item, prebuilt=prebuilt),
        )

    def get_artwork_slot(self, item, x='', prebuilt=False):
        if not prebuilt:
            return self._parent.get_infolabel(item.format(x=x))
        if not item.startswith('art('):
            return
        return self.built_artwork.get(item.format(x=x)[4:-1])


class ImageManipulations(WindowPropertySetter):
    def get_infolabel(self, info):
        return get_infolabel(f'ListItem.{info}')

    def get_condvisibility(self, info):
        return get_condvisibility(f'ListItem.{info}')

    def get_builtartwork(self):
        return

    def get_extrafanart_slots(self):
        """ Base slot is always included followed by the extra slots enabled in settings """
        return (
            '',
            *(EXTRAFANART_SLOTS[i] for i in ADDON.getSettings().getStringList('service_extrafanart_slots')),
        )

    def get_cycled_artwork(self, key, get_slots, resolve):
        """ Without a kept cycle each request draws the first available image of a fresh shuffle """
        return ImageArtworkCycle(get_slots).get_next(resolve)

    def get_artwork(self, source='', build_fallback=False, built_artwork=None):
        source = source or ''
        source = source.lower()

        for _source in source.split("||"):
            img_get = ImageArtworkGetter(self, _source, prebuilt_artwork=built_artwork)
            if img_get.artwork:
                return img_get.artwork
            if not build_fallback or not img_get.built_artwork:
                continue
            if img_get.artwork_fallback:
                return img_get.artwork_fallback

    def get_blur_fallback(self):
        fallback = self.get_property('Blur.Fallback')
        variable = re.fullmatch(r'\$SKINVAR\[([^\[\],]+)\]', fallback or '')
        return get_infolabel(f'$VAR[{variable[1]}]') if variable else fallback

    def get_image_manipulation_requests(self, built_artwork=None, allow_list=('crop', 'blur', 'desaturate', 'colors', )):
        """ Source image for each manipulation that is allowed and enabled by the skin """
        return {
            i['method']: i['images']()
            for i in self.get_image_manipulation_configs(built_artwork)
            if i['method'] in allow_list and i['active']()
        }

    def get_image_manipulation_configs(self, built_artwork=None):
        return (
            {'method': 'crop',
                'active': lambda: get_condvisibility("Skin.HasSetting(TMDbHelper.EnableCrop)"),
                'images': lambda: self.get_artwork(
                    source=CROPIMAGE_SOURCE,
                    build_fallback=True,
                    built_artwork=built_artwork)},
            {'method': 'blur',
                'active': lambda: get_condvisibility("Skin.HasSetting(TMDbHelper.EnableBlur)"),
                'images': lambda: self.get_artwork(
                    source=self.get_property('Blur.SourceImage'),
                    build_fallback=True,
                    built_artwork=built_artwork)
                or self.get_blur_fallback()},
            {'method': 'desaturate',
                'active': lambda: get_condvisibility("Skin.HasSetting(TMDbHelper.EnableDesaturate)"),
                'images': lambda: self.get_artwork(
                    source=self.get_property('Desaturate.SourceImage'),
                    build_fallback=True,
                    built_artwork=built_artwork)
                or self.get_property('Desaturate.Fallback')},
            {'method': 'colors',
                'active': lambda: get_condvisibility("Skin.HasSetting(TMDbHelper.EnableColors)"),
                'images': lambda: self.get_artwork(
                    source=self.get_property('Colors.SourceImage'),
                    build_fallback=True,
                    built_artwork=built_artwork)
                or self.get_property('Colors.Fallback')},)
