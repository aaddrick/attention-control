#!/usr/bin/env python3
"""Draw the hero card at .github/assets/hero.png.

The card is the style's own argument, drawn as two air traffic control flight
progress strips. The unstyled reply is one undivided box; its text overruns the
strip and fades off the right edge. The Attention Control reply is a field grid,
one datum per box.

Run it after any change to the header text, the example, or the harness list:

    python3 scripts/make_card.py

Needs Pillow and NumPy. Neither is a test dependency, so CI does not run this
and no gate checks the committed PNG against a fresh render. Pillow encodes the
same pixels differently across versions, so a checksum gate would fail on an
unrelated upgrade. Regenerate by hand and commit the result.

Fonts live in assets/fonts/. Both families are OFL; the licenses sit beside
them.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "assets" / "fonts"
DEFAULT_OUT = ROOT / ".github" / "assets" / "hero.png"

S = 2                      # supersample factor, resized down at the end
W, H = 1280 * S, 640 * S   # GitHub's social preview size

# --- palette ---------------------------------------------------------------
BOARD      = (0x23, 0x26, 0x2B)   # the strip bay
BOARD_DARK = (0x16, 0x18, 0x1C)
PAPER_BUFF = (0xE8, 0xDF, 0xC9)   # unstyled strip
PAPER_TEAL = (0xCF, 0xDE, 0xD8)   # controlled strip
INK        = (0x1B, 0x19, 0x16)
INK_MUTE   = (0x8A, 0x85, 0x7A)
RULE       = (0x9C, 0x96, 0x86)
RED        = (0xA8, 0x37, 0x2A)
GREEN      = (0x2E, 0x6B, 0x4F)
AMBER      = (0xC2, 0x82, 0x0C)   # the accent: what to notice


def disp(size, weight="Bold"):
    return ImageFont.truetype(str(FONTS / f"SairaCondensed-{weight}.ttf"), int(size * S))


def mono(size, weight="Regular"):
    return ImageFont.truetype(str(FONTS / f"IBMPlexMono-{weight}.ttf"), int(size * S))


img = Image.new("RGB", (W, H), BOARD)
d = ImageDraw.Draw(img)

# --- strip bay: brushed metal, capped top and bottom -----------------------
for y in range(0, H, 4 * S):
    d.line([(0, y), (W, y)], fill=(BOARD[0] + 3, BOARD[1] + 3, BOARD[2] + 3), width=1)
d.rectangle([0, 0, W, 10 * S], fill=BOARD_DARK)
d.rectangle([0, H - 10 * S, W, H], fill=BOARD_DARK)


def tracked(draw, xy, text, font, fill, track=0):
    """Draw text with letter spacing. Returns the end x."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track * S
    return x


def tracked_len(draw, text, font, track=0):
    return sum(draw.textlength(c, font=font) + track * S for c in text)


# --- header: both tagline lines, verbatim from README.md -------------------
PAD = 64 * S
tracked(d, (PAD, 46 * S), "ATTENTION CONTROL", disp(58), PAPER_BUFF, track=1.5)
d.text((PAD, 110 * S), "Air traffic control discipline for agent output.",
       font=disp(30, "Medium"), fill=(0x9A, 0x9E, 0xA6))
d.text((PAD, 146 * S), "Written for a reader with ADHD.",
       font=disp(27, "Medium"), fill=AMBER)

SX, SW = PAD, W - PAD * 2
MARK_W = 92 * S          # leftmost box: the disposition mark


def strip(y, h, paper, tilt):
    """Paper strip with a soft shadow, slight tilt, faint grain."""
    pad = 26 * S
    lay = Image.new("RGBA", (SW + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rectangle([pad, pad, pad + SW, pad + h], fill=paper + (255,))

    # paper grain, seeded so the render is reproducible
    a = np.array(lay).astype(np.int16)
    noise = np.random.default_rng(7).integers(-5, 6, (lay.size[1], lay.size[0], 1))
    mask = a[:, :, 3] > 0
    a[:, :, :3] = np.clip(a[:, :, :3] + noise * mask[:, :, None], 0, 255)
    lay = Image.fromarray(a.astype(np.uint8))

    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([pad, pad, pad + SW, pad + h], fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(9 * S)).rotate(tilt, resample=Image.BICUBIC)
    lay = lay.rotate(tilt, resample=Image.BICUBIC)

    img.paste(sh, (SX - pad, y - pad + 5 * S), sh)
    img.paste(lay, (SX - pad, y - pad), lay)
    return ImageDraw.Draw(img)


# ===========================================================================
# Strip 1, unstyled: one box, no fields, text running off the edge
# ===========================================================================
Y1, H1 = 196 * S, 132 * S
d = strip(Y1, H1, PAPER_BUFF, 0.35)

d.line([(SX + MARK_W, Y1), (SX + MARK_W, Y1 + H1)], fill=RULE, width=2 * S)
cx, cy, r = SX + MARK_W // 2, Y1 + H1 // 2 - 6 * S, 16 * S
d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=RED, width=5 * S)
d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=RED, width=5 * S)
tracked(d, (SX + 13 * S, Y1 + H1 - 28 * S), "UNSTYLED", disp(13, "SemiBold"), INK_MUTE, track=1)
tracked(d, (SX + MARK_W + 20 * S, Y1 + 12 * S), "MESSAGE", disp(16, "SemiBold"), INK_MUTE, track=2.5)

lines = [
    "Great question! Let me take a look. It seems like the token verification logic could",
    "possibly be utilizing a somewhat deprecated API here, and one approach that might be",
    "considered would be going ahead and updating the package at some point when you ge",
]
ty = Y1 + 46 * S
for i, line in enumerate(lines):
    d.text((SX + MARK_W + 20 * S, ty), line, font=mono(19),
           fill=INK_MUTE if i else (0x5E, 0x5A, 0x52))
    ty += 27 * S

# the last line fades at the right edge: information falling off the strip
fade = Image.new("RGBA", (200 * S, 34 * S), (0, 0, 0, 0))
fd = ImageDraw.Draw(fade)
for i in range(200 * S):
    fd.line([(i, 0), (i, 34 * S)], fill=PAPER_BUFF + (int(255 * i / (200 * S)),))
img.paste(fade, (SX + SW - 200 * S, Y1 + 100 * S), fade)
d = ImageDraw.Draw(img)

# ===========================================================================
# Strip 2, Attention Control: a field grid, one datum per box
# ===========================================================================
Y2, H2 = 362 * S, 172 * S
d = strip(Y2, H2, PAPER_TEAL, -0.25)

d.line([(SX + MARK_W, Y2), (SX + MARK_W, Y2 + H2)], fill=RULE, width=2 * S)
cx, cy = SX + MARK_W // 2, Y2 + H2 // 2 - 6 * S
d.line([(cx - 15 * S, cy + 1 * S), (cx - 4 * S, cy + 13 * S)], fill=GREEN, width=5 * S)
d.line([(cx - 4 * S, cy + 13 * S), (cx + 16 * S, cy - 13 * S)], fill=GREEN, width=5 * S)
tracked(d, (SX + 8 * S, Y2 + H2 - 28 * S), "CONTROLLED", disp(13, "SemiBold"),
        (0x5E, 0x6B, 0x66), track=1)

# the same edit the README's "What changes" section cites
rows = [
    [("ACTION", "npm install jsonwebtoken@latest", INK),
     ("EDIT",   "src/auth.ts:47",                  INK)],
    [("STATE",  "step 2 of 3 - schema changed",    AMBER),
     ("NEXT",   "npm test -- auth.spec.ts",        INK)],
]
gx0, gw = SX + MARK_W, SW - MARK_W
COL = 0.58
label_font, value_font = disp(15, "SemiBold"), mono(19, "Medium")
rh = H2 // 2
for r, row in enumerate(rows):
    ry = Y2 + r * rh
    if r:
        d.line([(gx0, ry), (SX + SW, ry)], fill=RULE, width=2 * S)
    x = gx0
    for c, (label, value, colour) in enumerate(row):
        if c:
            d.line([(x, ry), (x, ry + rh)], fill=RULE, width=2 * S)
        tracked(d, (x + 20 * S, ry + 11 * S), label, label_font, (0x5E, 0x6B, 0x66), track=2.5)
        d.text((x + 20 * S, ry + 36 * S), value, font=value_font, fill=colour)
        x += int(gw * (COL if c == 0 else 1 - COL))

# --- footer ----------------------------------------------------------------
# Both lines sit on one baseline. The two faces have different ascents, so a
# shared top edge would leave them visibly off by a few pixels.
BASE = H - 42 * S
url_font = mono(21, "Medium")
d.text((PAD, BASE - url_font.getmetrics()[0]), "github.com/aaddrick/attention-control",
       font=url_font, fill=(0x8E, 0x93, 0x9B))
harnesses = "CLAUDE CODE  ·  CODEX  ·  CURSOR  ·  GEMINI CLI  ·  COPILOT  ·  ZED"
hf = disp(19, "SemiBold")
tracked(d, (W - PAD - tracked_len(d, harnesses, hf, track=2), BASE - hf.getmetrics()[0]),
        harnesses, hf, (0x6E, 0x73, 0x7B), track=2)

out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
out = img.resize((W // S, H // S), Image.LANCZOS)
out.save(out_path, optimize=True)
print(f"wrote {out_path} {out.size[0]}x{out.size[1]}")
