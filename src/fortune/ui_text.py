"""Cached bitmap text for the live Agg/Tk UI, with normal vector export.

Matplotlib's glyph-by-glyph text drawing dominated the replay profile. Pillow
renders these plain interface strings once; subsequent draws composite a small
RGBA bitmap. Font and string caches are bounded. Mathematical/report text is
unaffected, and SVG/PDF backends retain Matplotlib's regular text renderer.
"""

from functools import lru_cache

import numpy as np
from matplotlib import colors, font_manager
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.text import Text
from PIL import Image, ImageDraw, ImageFont


@lru_cache(maxsize=16)
def _font(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)


@lru_cache(maxsize=256)
def _bitmap(text, path, size, rgba, spacing):
    font = _font(path, size)
    measure = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    box = measure.multiline_textbbox(
        (0, 0), text, font=font, anchor="ls", spacing=spacing
    )
    left, top, right, bottom = box
    pad = 1
    image = Image.new(
        "RGBA", (max(1, right - left + 2 * pad), max(1, bottom - top + 2 * pad))
    )
    ImageDraw.Draw(image).multiline_text(
        (pad - left, pad - top),
        text,
        font=font,
        fill=rgba,
        anchor="ls",
        spacing=spacing,
    )
    return np.ascontiguousarray(np.asarray(image)[::-1]), bottom + pad


class RasterText(Text):
    def draw(self, renderer):
        text = self.get_text()
        if not self.get_visible() or not text:
            self.stale = False
            return
        if (
            not isinstance(renderer, RendererAgg)
            or self.get_rotation() != 0
            or "$" in text
            or self.get_bbox_patch() is not None
        ):
            return super().draw(renderer)
        size = max(1, round(renderer.points_to_pixels(self.get_fontsize())))
        path = font_manager.findfont(self.get_fontproperties())
        rgba = tuple(
            round(c * 255) for c in colors.to_rgba(self.get_color(), self.get_alpha())
        )
        linespacing = self.get_linespacing()
        # Matplotlib 3.11 can return "auto" for the default spacing.
        linespacing = linespacing if isinstance(linespacing, (int, float)) else 1.2
        spacing = max(0, round(size * (linespacing - 1)))
        pixels, baseline = _bitmap(text, path, size, rgba, spacing)
        x, y = self.get_transform().transform(self.get_position())
        height, width = pixels.shape[:2]
        ha, va = self.get_horizontalalignment(), self.get_verticalalignment()
        if ha == "center":
            x -= width / 2
        elif ha == "right":
            x -= width
        if va == "top":
            y -= height
        elif va in ("center", "center_baseline"):
            y -= height / 2
        elif va == "baseline":
            y -= baseline
        gc = renderer.new_gc()
        try:
            if self.get_clip_on():
                gc.set_clip_rectangle(self.get_clip_box())
            renderer.draw_image(gc, round(x), round(y), pixels)
        finally:
            gc.restore()
        self.stale = False


def ui_text(parent, x, y, text="", **kwargs):
    kwargs.setdefault("clip_on", False)
    kwargs.setdefault(
        "transform",
        parent.transData if hasattr(parent, "transData") else parent.transFigure,
    )
    artist = RasterText(x, y, text, **kwargs)
    parent.add_artist(artist)
    return artist


def replace_widget_text(axes, old):
    """Replace one widget label at initialization, preserving public settings."""
    new = ui_text(
        axes,
        *old.get_position(),
        old.get_text(),
        transform=old.get_transform(),
        fontproperties=old.get_fontproperties(),
        color=old.get_color(),
        horizontalalignment=old.get_horizontalalignment(),
        verticalalignment=old.get_verticalalignment(),
    )
    old.remove()
    return new
