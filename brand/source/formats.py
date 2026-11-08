"""Build the four logo formats from the spec as standalone, fully outlined SVGs (out/*.svg).

A  primary      monogram + BAM TEAM SERVICES + Innovation for Good     (master 1600x900 canvas)
B  header       monogram | BAM TEAM / SERVICES                          (master 1200x320 canvas)
C  avatar       white monogram on navy circle, inside the central 72%   (1024x1024)
D  app icon     white monogram on navy rounded square                   (512x512)
Plus light/dark variants of A and B, a transparent monogram, and a 16 px favicon (A + hump).

Run after monogram.py:  python3 brand/source/formats.py  (needs fonttools; see brand/README.md)
"""
import json
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
OUT = HERE.parent / "svg"
OUT.mkdir(exist_ok=True)
FONTS = HERE / "fonts"
m = json.loads((HERE / "monogram.json").read_text())
MW, MH = m["w"], m["h"]
NAVY, TEAL, WHITE = "#082F50", "#079D9F", "#FFFFFF"
TEAL_ON_DARK = "#079D9F"


class Setter:
    def __init__(self, path):
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.cap = self.f["OS/2"].sCapHeight
        self.kern = {}
        # Pair kerning from GPOS is complex; tracked caps don't need it, and the tagline is short.

    def line(self, text, tracking=0.0):
        """Return (path in font units, y down, baseline 0; ink width)."""
        x, parts = 0.0, []
        last_ink = 0.0
        for i, ch in enumerate(text):
            name = self.cmap[ord(ch)]
            g = self.gs[name]
            if ch != " ":
                pen = SVGPathPen(self.gs)
                g.draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
                parts.append(pen.getCommands())
                last_ink = x + g.width
            x += g.width + (tracking * self.upm if i < len(text) - 1 else 0)
        return " ".join(parts), last_ink


semi = Setter(FONTS / "Montserrat-600.ttf")
med = Setter(FONTS / "Montserrat-500.ttf")


def mono(x, y, h, ink=NAVY, teal=TEAL):
    s = h / MH
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})">'
            f'<path d="{m["navy"]}" fill="{ink}" fill-rule="evenodd"/><path d="{m["teal"]}" fill="{teal}"/></g>')


def text(setter, s, x, baseline, cap_px, tracking, fill):
    d, w = setter.line(s, tracking)
    k = cap_px / setter.cap
    return f'<g transform="translate({x:.2f} {baseline:.2f}) scale({k:.5f})"><path d="{d}" fill="{fill}"/></g>', w * k


def fit_tracking(setter, s, cap_px, target_w):
    """Tracking that makes the ink width of s equal target_w at this size."""
    _, w0 = setter.line(s, 0)
    k = cap_px / setter.cap
    gaps = len(s) - 1
    return (target_w / k - w0) / gaps / setter.upm


def svg(w, h, body, bg=None, label="BAM Team Services"):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{label}"><title>{label}</title>{rect}{body}</svg>\n')


def primary(dark=False):
    W, Hh = 1600, 900
    ink = WHITE if dark else NAVY
    mh = 300                       # monogram cap height
    mw = MW * mh / MH
    x0 = (W - mw) / 2
    cap1 = mh * 0.19               # TEAM SERVICES cap height
    cap2 = mh * 0.17               # tagline cap height
    gap1, gap2 = mh * 0.16, mh * 0.15
    total = mh + gap1 + cap1 + gap2 + cap2 * 1.25
    y0 = (Hh - total) / 2
    t1 = fit_tracking(semi, "TEAM SERVICES", cap1, mw)
    l1, _ = text(semi, "TEAM SERVICES", x0, y0 + mh + gap1 + cap1, cap1, t1, ink)
    _, tw = med.line("Innovation for Good", 0.01)
    k2 = cap2 / med.cap
    tx = (W - tw * k2) / 2
    l2, _ = text(med, "Innovation for Good", tx, y0 + mh + gap1 + cap1 + gap2 + cap2, cap2, 0.01, ink)
    return svg(W, Hh, mono(x0, y0, mh, ink, TEAL) + l1 + l2, NAVY if dark else None)


def header(dark=False, tight=False):
    """Monogram, then TEAM over SERVICES. The two lines span the monogram's height so it reads as one name."""
    W, Hh = 1200, 320
    ink = WHITE if dark else NAVY
    mh = 150
    mw = MW * mh / MH
    gap_line = mh * 0.24                 # space between the two lines
    cap = (mh - gap_line) / 2            # each line's cap height, so TEAM tops align and SERVICES sits on the baseline
    k = cap / semi.cap
    t_services = 0.10
    _, w_services = semi.line("SERVICES", t_services)
    t_team = t_services   # same spacing on both lines, left aligned
    tw = w_services * k
    gap = mh * 0.20
    total = mw + gap + tw
    x0 = (W - total) / 2
    y0 = (Hh - mh) / 2
    tx = x0 + mw + gap
    a, _ = text(semi, "TEAM", tx, y0 + cap, cap, t_team, ink)
    b, _ = text(semi, "SERVICES", tx, y0 + mh, cap, t_services, ink)
    body = mono(x0, y0, mh, ink, TEAL) + a + b
    if tight:  # cropped to the ink, transparent: for placing in a website header
        return svg(round(total, 2), mh, f'<g transform="translate({-x0:.2f} {-y0:.2f})">{body}</g>')
    return svg(W, Hh, body, NAVY if dark else None)


def avatar(size=1024):
    # Lettering inside the central 72% so circular crops never touch it.
    mw = size * 0.66
    mh = MH * mw / MW
    x0, y0 = (size - mw) / 2, (size - mh) / 2 + mh * 0.02
    body = f'<circle cx="{size / 2}" cy="{size / 2}" r="{size / 2}" fill="{NAVY}"/>' + mono(x0, y0, mh, WHITE, TEAL)
    return svg(size, size, body)


def app_icon(size=512, radius=0.22):
    mw = size * 0.74
    mh = MH * mw / MW
    x0, y0 = (size - mw) / 2, (size - mh) / 2
    body = f'<rect width="{size}" height="{size}" rx="{size * radius:.1f}" fill="{NAVY}"/>' + mono(x0, y0, mh, WHITE, TEAL)
    return svg(size, size, body)


def monogram_only(ink=NAVY):
    pad = 4
    return svg(MW + 2 * pad, MH + 2 * pad, mono(pad, pad, MH, ink, TEAL))


files = {
    "bam-primary.svg": primary(), "bam-primary-dark.svg": primary(dark=True),
    "bam-header.svg": header(), "bam-header-dark.svg": header(dark=True),
    "bam-header-tight.svg": header(tight=True), "bam-header-tight-white.svg": header(dark=True, tight=True),
    "bam-avatar.svg": avatar(), "bam-app-icon.svg": app_icon(),
    "bam-monogram.svg": monogram_only(), "bam-monogram-white.svg": monogram_only(WHITE),
}
for name, s in files.items():
    (OUT / name).write_text(s)
print("\n".join(f"{n}: {len(s) // 1024} KB" for n, s in files.items()))


def favicon_a(size=64, radius=0.22):
    """16-32 px favicon: the A and its hump only (the full monogram is unreadable at 16 px)."""
    import re as _re
    nums = [float(v) for v in _re.findall(r"-?\d+\.?\d*", m["a"])]
    xs, ys = nums[0::2], nums[1::2]
    ax0, ax1 = min(xs), max(xs)
    aw = ax1 - ax0
    art = size * 0.70
    k = art / max(aw, MH)
    x0 = (size - aw * k) / 2 - ax0 * k
    y0 = (size - MH * k) / 2
    body = (f'<rect width="{size}" height="{size}" rx="{size * radius:.1f}" fill="{NAVY}"/>'
            f'<g transform="translate({x0:.2f} {y0:.2f}) scale({k:.5f})"><path d="{m["a"]}" fill="{WHITE}"/>'
            f'<path d="{m["teal"]}" fill="{TEAL}"/></g>')
    return svg(size, size, body)


(OUT / "bam-favicon-a.svg").write_text(favicon_a())
print("bam-favicon-a.svg written")
