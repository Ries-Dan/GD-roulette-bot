"""Exile Roulette image rendering.

Builds one animated GIF per pull (ascendancy wheel on the left, skill reel on the
right) plus a still PNG of the final frame. The wheel is drawn once at startup and
rotated per frame; the reel is a pre-drawn strip that is cropped per frame.
"""
import io
import math
import random
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

from data import SEGMENTS, SKILL_POOL

FONT_DIR = Path(__file__).parent / "fonts"
DISPLAY_FONT = str(FONT_DIR / "IMFeENsc28P.ttf")
BODY_FONT = str(FONT_DIR / "AlegreyaSans-Medium.ttf")
BOLD_FONT = str(FONT_DIR / "AlegreyaSans-Bold.ttf")

LANCZOS = Image.Resampling.LANCZOS
BICUBIC = Image.Resampling.BICUBIC

# ── Palette ────────────────────────────────────────────────────────────────────
BG = (18, 16, 16)
PANEL = (28, 24, 22)
LINE = (58, 48, 42)
FG = (232, 223, 210)
MUTED = (163, 151, 138)
GOLD = (201, 163, 90)
GOLD_HI = (233, 201, 131)
REEL_BG = (14, 12, 11)

# ── Layout ─────────────────────────────────────────────────────────────────────
W, H = 760, 380
WHEEL_R = 158                    # wheel radius incl. rim
WHEEL_C = (195, 212)             # wheel centre
REEL_X, REEL_Y = 410, 86         # reel window top-left
REEL_W = 320
CELL_H = 84
REEL_H = CELL_H * 3

FPS = 20
FRAME_MS = 1000 // FPS
WHEEL_SECONDS = 3.2
REEL_SECONDS = 4.2
REEL_CELLS = 36
FINAL_HOLD_MS = 60000            # long hold on the result in case a client loops the GIF

SEG_DEG = 360 / len(SEGMENTS)


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _fit_font(draw: ImageDraw.ImageDraw, text: str, path: str, size: int, max_w: int,
              min_size: int = 10) -> ImageFont.FreeTypeFont:
    font = _font(path, size)
    while draw.textlength(text, font=font) > max_w and size > min_size:
        size -= 1
        font = _font(path, size)
    return font


def _ease_out(p: float, power: float) -> float:
    return 1 - (1 - p) ** power


# ── Static layers (built once) ─────────────────────────────────────────────────
def _build_background() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # Soft ember glow behind the wheel
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    cx, cy = WHEEL_C
    for i in range(30, 0, -1):
        r = WHEEL_R + i * 5
        gd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=int(70 * (1 - i / 30)))
    img.paste(Image.new("RGB", (W, H), (60, 36, 26)), (0, 0), glow)
    # Titles
    title = _font(BOLD_FONT, 15)
    for text, x_mid in (("CLASS & ASCENDANCY", WHEEL_C[0]), ("MAIN SKILL", REEL_X + REEL_W // 2)):
        spaced = " ".join(text)  # letter-spacing for the eyebrow labels
        tw = d.textlength(spaced, font=title)
        d.text((x_mid - tw / 2, 18), spaced, font=title, fill=GOLD)
    # Reel housing
    pad = 14
    d.rounded_rectangle((REEL_X - pad, REEL_Y - pad, REEL_X + REEL_W + pad, REEL_Y + REEL_H + pad),
                        radius=8, fill=PANEL, outline=LINE, width=1)
    d.rectangle((REEL_X - 1, REEL_Y - 1, REEL_X + REEL_W, REEL_Y + REEL_H), outline=(74, 59, 46))
    return img


def _build_wheel() -> Image.Image:
    ss = 2
    r = WHEEL_R * ss
    size = r * 2
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, size - 1, size - 1), fill=GOLD)
    rim = 5 * ss
    inner = r - rim
    box = (rim, rim, size - rim - 1, size - rim - 1)
    for i, seg in enumerate(SEGMENTS):
        a0 = i * SEG_DEG - 90
        color = seg["color"]
        if i % 2:
            color = tuple(int(c * 0.85) for c in color)
        d.pieslice(box, a0, a0 + SEG_DEG, fill=color, outline=(18, 13, 11), width=2)
    # Gold lines where one class ends and the next begins
    idx = 0
    seen = []
    for seg in SEGMENTS:
        if seg["cls"] not in seen:
            seen.append(seg["cls"])
            ang = math.radians(idx * SEG_DEG - 90)
            d.line((r, r, r + math.cos(ang) * inner, r + math.sin(ang) * inner), fill=GOLD, width=3 * ss)
        idx += 1
    # Radial labels, reading from the hub outwards
    max_w = int(inner * 0.6)
    for i, seg in enumerate(SEGMENTS):
        text = seg["asc"]
        font = _fit_font(d, text, BODY_FONT, 14 * ss, max_w, min_size=9 * ss)
        tw = int(d.textlength(text, font=font)) + 4
        th = font.size + 8
        label = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(label).text((2, th / 2), text, font=font, fill=FG, anchor="lm")
        mid = i * SEG_DEG + SEG_DEG / 2 - 90
        rotated = label.rotate(-mid, resample=BICUBIC, expand=True)
        rad_mid = inner - 12 * ss - tw / 2
        ang = math.radians(mid)
        px = r + math.cos(ang) * rad_mid - rotated.width / 2
        py = r + math.sin(ang) * rad_mid - rotated.height / 2
        img.alpha_composite(rotated, (int(px), int(py)))
    return img.resize((WHEEL_R * 2, WHEEL_R * 2), LANCZOS)


HUB_R = int(WHEEL_R * 0.3)
HUB_BOX = HUB_R * 2 + 4
HUB_POS = (WHEEL_C[0] - HUB_BOX // 2, WHEEL_C[1] - HUB_BOX // 2)
PTR_POS = (WHEEL_C[0] - 16, WHEEL_C[1] - WHEEL_R - 11)


def _hub(hub_text: str) -> Image.Image:
    """Small RGBA patch for the wheel hub (does not rotate)."""
    patch = Image.new("RGBA", (HUB_BOX, HUB_BOX), (0, 0, 0, 0))
    d = ImageDraw.Draw(patch)
    c = HUB_BOX / 2
    d.ellipse((c - HUB_R, c - HUB_R, c + HUB_R, c + HUB_R), fill=PANEL, outline=GOLD, width=3)
    font = _fit_font(d, hub_text, DISPLAY_FONT, 24, HUB_R * 2 - 12, min_size=12)
    d.text((c, c), hub_text, font=font, fill=GOLD_HI, anchor="mm")
    return patch


def _pointer() -> Image.Image:
    patch = Image.new("RGBA", (33, 33), (0, 0, 0, 0))
    ImageDraw.Draw(patch).polygon([(1, 1), (31, 1), (16, 31)], fill=GOLD_HI, outline=(60, 40, 20))
    return patch


def _reel_overlay() -> Image.Image:
    """RGBA patch the size of the reel window: glass fades and the gold payline."""
    layer = Image.new("RGBA", (REEL_W, REEL_H), (0, 0, 0, 0))
    fade_h = CELL_H
    for y in range(fade_h):
        a = int(235 * (1 - y / fade_h) ** 1.4)
        for yy in (y, REEL_H - 1 - y):
            layer.paste((*REEL_BG, a), (0, yy, REEL_W, yy + 1))
    d = ImageDraw.Draw(layer)
    y0, y1 = CELL_H, CELL_H * 2
    d.line((0, y0, REEL_W, y0), fill=GOLD, width=2)
    d.line((0, y1, REEL_W, y1), fill=GOLD, width=2)
    ym = (y0 + y1) // 2
    d.polygon([(0, ym - 9), (0, ym + 9), (12, ym)], fill=GOLD_HI)
    d.polygon([(REEL_W, ym - 9), (REEL_W, ym + 9), (REEL_W - 12, ym)], fill=GOLD_HI)
    return layer


BACKGROUND = _build_background()
WHEEL = _build_wheel()
HUB_SPIN = _hub("Fate")
POINTER = _pointer()
REEL_OVERLAY = _reel_overlay()
_HUB_CACHE = {}

# Rotating the wheel is the slowest step on the Pi (~80 ms a frame), so every
# rotation is pre-rendered once, in ROT_STEP-degree steps, with the background
# already behind it. Landing jitter keeps the pointer >3° inside a segment, so
# rounding to the nearest step never changes the result.
ROT_STEP = 2
WHEEL_BOX = (WHEEL_C[0] - WHEEL_R, WHEEL_C[1] - WHEEL_R)
_TILES = {}


def _wheel_tile(rot: float) -> Image.Image:
    key = int(round(rot / ROT_STEP)) % (360 // ROT_STEP)
    tile = _TILES.get(key)
    if tile is None:
        tile = BACKGROUND.crop((*WHEEL_BOX, WHEEL_BOX[0] + WHEEL_R * 2, WHEEL_BOX[1] + WHEEL_R * 2))
        wheel = WHEEL.rotate(-key * ROT_STEP, resample=BICUBIC)
        tile.paste(wheel, (0, 0), wheel)
        _TILES[key] = tile
    return tile


def warm_cache():
    """Pre-render every wheel rotation (call once at startup, off the event loop)."""
    for key in range(360 // ROT_STEP):
        _wheel_tile(key * ROT_STEP)
    _palette()


_PALETTE = []


def _palette() -> Image.Image:
    """One GIF palette shared by every pull, built from a representative frame."""
    if not _PALETTE:
        sample = BACKGROUND.copy()
        sample.paste(_wheel_tile(7), WHEEL_BOX)
        sample.paste(HUB_SPIN, HUB_POS, HUB_SPIN)
        sample.paste(POINTER, PTR_POS, POINTER)
        strip = _draw_strip([SKILL_POOL[0], SKILL_POOL[-1], SKILL_POOL[40]])  # includes a gold "via item" line
        sample.paste(strip, (REEL_X, REEL_Y))
        sample.paste(REEL_OVERLAY, (REEL_X, REEL_Y), REEL_OVERLAY)
        _PALETTE.append(sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT))
    return _PALETTE[0]


def _hub_for(cls_name: str) -> Image.Image:
    if cls_name not in _HUB_CACHE:
        _HUB_CACHE[cls_name] = _hub(cls_name)
    return _HUB_CACHE[cls_name]


# ── Reel strip ─────────────────────────────────────────────────────────────────
def _draw_strip(items: List[tuple]) -> Image.Image:
    strip = Image.new("RGB", (REEL_W, CELL_H * len(items)), REEL_BG)
    d = ImageDraw.Draw(strip)
    tag_font = _font(BOLD_FONT, 12)
    for i, (name, cat, item, _desc) in enumerate(items):
        top = i * CELL_H
        font = _fit_font(d, name, DISPLAY_FONT, 30, REEL_W - 56, min_size=16)
        d.text((REEL_W / 2, top + CELL_H / 2 - 6), name, font=font, fill=FG, anchor="mm")
        if item:
            # Item-granted skill: name the item you need instead of the gem category.
            label = f"via {item}"
            item_font = _fit_font(d, label, BOLD_FONT, 15, REEL_W - 56, min_size=11)
            d.text((REEL_W / 2, top + CELL_H / 2 + 22), label, font=item_font, fill=GOLD, anchor="mm")
        else:
            tag = " ".join(cat.upper())
            d.text((REEL_W / 2, top + CELL_H / 2 + 22), tag, font=tag_font, fill=MUTED, anchor="mm")
        d.line((0, top + CELL_H - 1, REEL_W, top + CELL_H - 1), fill=(26, 23, 21))
    return strip


# ── Public API ─────────────────────────────────────────────────────────────────
def pick() -> Tuple[dict, tuple]:
    """Choose an ascendancy segment and a skill at random."""
    return random.choice(SEGMENTS), random.choice(SKILL_POOL)


def render_spin(segment: dict, skill: tuple) -> Tuple[bytes, bytes, float]:
    """Render the pull. Returns (gif_bytes, png_bytes, animation_seconds)."""
    win = SEGMENTS.index(segment)

    # Wheel: rotate clockwise by `rot` degrees; the segment under the top pointer
    # is the one whose original angle contains (-rot mod 360).
    start = random.uniform(0, 360)
    target = (360 - (win + random.uniform(0.2, 0.8)) * SEG_DEG) % 360
    end = start + 5 * 360 + ((target - start) % 360)

    # Reel: winner sits at index REEL_CELLS-2 so one filler cell shows below it.
    items = [random.choice(SKILL_POOL) for _ in range(REEL_CELLS)]
    items[-2] = skill
    strip = _draw_strip(items)
    reel_end = (REEL_CELLS - 3) * CELL_H

    n_frames = int(REEL_SECONDS * FPS) + 1
    palette = _palette()
    gif_frames = []
    frame = None
    for f in range(n_frames):
        t = f / FPS
        wp = min(1.0, t / WHEEL_SECONDS)
        rp = min(1.0, t / REEL_SECONDS)
        rot = start + (end - start) * _ease_out(wp, 4)
        off = int(round(reel_end * _ease_out(rp, 3.5)))

        frame = BACKGROUND.copy()
        frame.paste(_wheel_tile(rot), WHEEL_BOX)
        hub = _hub_for(segment["cls"]) if wp >= 1 else HUB_SPIN
        frame.paste(hub, HUB_POS, hub)
        frame.paste(POINTER, PTR_POS, POINTER)
        frame.paste(strip.crop((0, off, REEL_W, off + REEL_H)), (REEL_X, REEL_Y))
        frame.paste(REEL_OVERLAY, (REEL_X, REEL_Y), REEL_OVERLAY)
        # Convert as we go so only one full-colour frame is held in memory.
        gif_frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))

    gif_buf = io.BytesIO()
    durations = [FRAME_MS] * (len(gif_frames) - 1) + [FINAL_HOLD_MS]
    # No `loop` argument: the GIF plays once and rests on the result.
    gif_frames[0].save(gif_buf, format="GIF", save_all=True, append_images=gif_frames[1:],
                       duration=durations, disposal=1, optimize=False)

    png_buf = io.BytesIO()
    frame.save(png_buf, format="PNG", optimize=True)

    return gif_buf.getvalue(), png_buf.getvalue(), REEL_SECONDS
