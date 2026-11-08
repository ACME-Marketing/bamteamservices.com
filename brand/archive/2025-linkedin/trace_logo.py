"""Trace the BAM Team Services raster logo (original.png, 590x228, from LinkedIn) and compose every logo format.

Needs pillow and the potrace CLI (brew install potrace). Run:  python3 brand/trace_logo.py
Then render the PNGs with:  brand/render_social.sh

Each part (emblem, "BAM TEAM", "SERVICES") is traced separately into its own coordinate box, so the same
vectors can be laid out horizontally, stacked, or as a square social avatar.
"""
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter

HERE = Path(__file__).parent
SRC = HERE / "original.png"
OUT_SOCIAL = HERE / "social"
SCALE = 6  # upscale before thresholding for smoother curves

# Brand colours sampled from the original.
BLUE, TEAL = "#4a5f96", "#4fb0b4"            # emblem gradient
CHARCOAL, TEAL_TEXT = "#383838", "#3f8c8d"   # wordmark
NIGHT = "#0f2a33"                            # dark background
LIGHT, TEAL_LIGHT = "#f3f7f7", "#7cc9cb"     # wordmark on dark
BLUE_LIGHT = "#8fa3d6"                       # emblem gradient start on dark

EMBLEM_X = (30, 200)
TEXT_X = 205
BAM_ROWS = (55, 118)
SERVICES_ROWS = (118, 170)


def ink(p):
    lum = 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
    return max(0, min(255, int((238 - lum) * 255 / 140)))


def mask(img, box):
    out = Image.new("L", img.size, 0)
    src, dst = img.load(), out.load()
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            dst[x, y] = ink(src[x, y])
    return out


class Layer:
    """A traced part. `svg` draws it in a box (0,0)-(w,h) in source pixels; (x, y) is its place in the original."""

    def __init__(self, m, pad=2):
        b = m.point(lambda v: 255 if v > 60 else 0).getbbox()
        self.x, self.y = b[0] - pad, b[1] - pad
        self.w, self.h = b[2] - b[0] + 2 * pad, b[3] - b[1] + 2 * pad
        crop = m.crop((self.x, self.y, self.x + self.w, self.y + self.h))
        big = crop.resize((crop.width * SCALE, crop.height * SCALE), Image.LANCZOS)
        big = big.filter(ImageFilter.GaussianBlur(SCALE * 0.35))
        bw = big.point(lambda v: 0 if v > 110 else 255).convert("1")  # potrace traces black
        with tempfile.TemporaryDirectory() as tmp:
            pbm, svg = Path(tmp) / "m.pbm", Path(tmp) / "m.svg"
            bw.save(pbm)
            subprocess.run(["potrace", str(pbm), "-s", "-o", str(svg), "--alphamax", "1.0", "--opttolerance", "0.2",
                            "--turdsize", "20", "--unit", "1"], check=True)
            text = svg.read_text()
        g = re.search(r"<g transform=.*?</g>", text, re.S).group(0)
        g = re.sub(r'\s(fill|stroke)="[^"]*"', "", g)
        self.svg = f'<g transform="scale({1 / SCALE:.6f})">{g}</g>'

    def at(self, x, y, s=1.0, fill="currentColor"):
        return f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})" fill="{fill}">{self.svg}</g>'


def grad(id_, a, b, x1, x2):
    return (f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" x1="{x1:.2f}" y1="0" x2="{x2:.2f}" y2="0">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')


def doc(w, h, body, defs="", label="BAM Team Services"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" role="img" aria-label="{label}">'
            f'<title>{label}</title><defs>{defs}</defs>{body}</svg>\n')


img = Image.open(SRC).convert("RGB")
W, H = img.size
emb = Layer(mask(img, (EMBLEM_X[0], 0, EMBLEM_X[1], H)))
bam = Layer(mask(img, (TEXT_X, BAM_ROWS[0], W, BAM_ROWS[1])))
svc = Layer(mask(img, (TEXT_X, SERVICES_ROWS[0], W, SERVICES_ROWS[1])))


def colours(dark):
    return (BLUE_LIGHT if dark else BLUE, TEAL_LIGHT if dark else TEAL,
            LIGHT if dark else CHARCOAL, TEAL_LIGHT if dark else TEAL_TEXT)


# ---- Horizontal logo: the original arrangement.
def horizontal(dark=False, one=None, pad=6):
    g0, g1, c_bam, c_svc = colours(dark)
    x0 = min(emb.x, bam.x, svc.x) - pad
    y0 = min(emb.y, bam.y, svc.y) - pad
    w = max(emb.x + emb.w, bam.x + bam.w, svc.x + svc.w) + pad - x0
    h = max(emb.y + emb.h, bam.y + bam.h, svc.y + svc.h) + pad - y0
    ef = one or "url(#g)"
    body = (emb.at(emb.x - x0, emb.y - y0, fill=ef) + bam.at(bam.x - x0, bam.y - y0, fill=one or c_bam)
            + svc.at(svc.x - x0, svc.y - y0, fill=one or c_svc))
    return doc(w, h, body, grad("g", g0, g1, emb.x - x0, emb.x - x0 + emb.w))


# ---- Wordmark block (BAM TEAM over SERVICES), as in the original.
WM_X = min(bam.x, svc.x)
WM_W = max(bam.x + bam.w, svc.x + svc.w) - WM_X
WM_H = svc.y + svc.h - bam.y


def wordmark(x, y, s, c_bam, c_svc):
    return (bam.at(x + (bam.x - WM_X) * s, y, s, c_bam)
            + svc.at(x + (svc.x - WM_X) * s, y + (svc.y - bam.y) * s, s, c_svc))


# ---- Stacked logo: emblem centred above the wordmark.
def stacked(dark=False, pad=16):
    g0, g1, c_bam, c_svc = colours(dark)
    gap = emb.h * 0.16
    w = max(emb.w, WM_W) + 2 * pad
    h = emb.h + gap + WM_H + 2 * pad
    ex = (w - emb.w) / 2
    body = (emb.at(ex, pad, fill="url(#g)")
            + wordmark((w - WM_W) / 2, pad + emb.h + gap, 1, c_bam, c_svc))
    return doc(w, h, body, grad("g", g0, g1, ex, ex + emb.w))


# ---- Square avatar: emblem only, sized to survive a circle crop (LinkedIn, Facebook, X, Google).
def avatar(size=1000, dark=False, rounded=False, fill_ratio=0.62):
    g0, g1, _, _ = colours(dark)
    s = size * fill_ratio / emb.h
    ew, eh = emb.w * s, emb.h * s
    ex = (size - ew) / 2
    ey = (size - eh) / 2 + eh * 0.03  # the thin spike at the bottom carries little weight: nudge down
    bg = NIGHT if dark else "#ffffff"
    rx = f' rx="{size * 0.2:.1f}"' if rounded else ""
    body = f'<rect width="{size}" height="{size}"{rx} fill="{bg}"/>' + emb.at(ex, ey, s, "url(#g)")
    return doc(size, size, body, grad("g", g0, g1, ex, ex + ew))


HERE.joinpath("logo.svg").write_text(horizontal())
HERE.joinpath("logo-on-dark.svg").write_text(horizontal(dark=True))
HERE.joinpath("logo-one-color.svg").write_text(horizontal(one=CHARCOAL))
HERE.joinpath("logo-stacked.svg").write_text(stacked())
HERE.joinpath("logo-stacked-on-dark.svg").write_text(stacked(dark=True))
HERE.joinpath("icon.svg").write_text(avatar(512, rounded=True, fill_ratio=0.74))
HERE.joinpath("emblem.svg").write_text(doc(emb.w, emb.h, emb.at(0, 0, fill="url(#g)"), grad("g", BLUE, TEAL, 0, emb.w)))
HERE.joinpath("emblem-on-dark.svg").write_text(
    doc(emb.w, emb.h, emb.at(0, 0, fill="url(#g)"), grad("g", BLUE_LIGHT, TEAL_LIGHT, 0, emb.w)))

OUT_SOCIAL.mkdir(exist_ok=True)
OUT_SOCIAL.joinpath("avatar.svg").write_text(avatar())
OUT_SOCIAL.joinpath("avatar-dark.svg").write_text(avatar(dark=True))
print("emblem", emb.w, emb.h, "wordmark", WM_W, WM_H)
