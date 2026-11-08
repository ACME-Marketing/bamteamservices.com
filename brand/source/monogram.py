"""Geometric redraw of the BAM monogram with the teal hump (BAM digital brand spec v1.0, Nov 2026).

Construction: each letter is a centreline stroked to one weight (S), clipped flat at baseline and cap
height, then corners are rounded by morphological opening/closing (radius RC). Letters are spaced by
true ink-to-ink distance. The hump is a semicircle on the baseline centred in the A, sized so the
white gap to the A's legs is exactly HUMP_GAP. Output: outlined paths only (no strokes, no fonts).

Run:  python3 brand/source/monogram.py  (needs shapely; see brand/README.md)
"""
import json
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

H = 100.0          # cap height
S = 22.0           # stroke weight
RC = 3.6           # corner radius
GAP_BA = 7.5       # B to A, nearest ink
GAP_AM = 7.5       # A to M, nearest ink
HUMP_GAP = 5.5     # white space around the hump
NAVY, TEAL = "#082F50", "#079D9F"
FLAT = dict(cap_style="flat", join_style="mitre", mitre_limit=10)
CLIP = box(-1000, 0, 1000, H)


def stroke(points):
    return LineString(points).buffer(S / 2, **FLAT)


def arc(cx, cy, r, a0, a1, n=48):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def round_corners(g, r=RC):
    g = g.buffer(-r, join_style="round").buffer(r, join_style="round")   # convex corners
    return g.buffer(r, join_style="round").buffer(-r, join_style="round")  # concave corners


# ---- B: stem + two bowls (bottom one wider), two enclosed counters.
def letter_b():
    c = S / 2
    top, mid, bot = c, 46.0, H - c
    rt, rb = (mid - top) / 2, (bot - mid) / 2
    xt, xb = 82.0 - c - rt, 88.0 - c - rb
    upper = [(c, top), (xt, top)] + arc(xt, top + rt, rt, -90, 90) + [(c, mid)]
    lower = [(c, mid), (xb, mid)] + arc(xb, mid + rb, rb, -90, 90) + [(c, bot)]
    g = unary_union([box(0, 0, S, H), stroke(upper), stroke(lower)])
    return round_corners(g.intersection(CLIP))


A_WIDTH = 136.0

# ---- A: two legs, no crossbar. Fully round apex; feet cut flat on the baseline so each toe tapers to a point.
def letter_a(width=None):
    width = width or A_WIDTH
    c = S / 2
    lean = (width / 2 - c) / (H + 20)
    apex = (width / 2, c)                      # round join: outer apex lands exactly on y = 0
    left = (width / 2 - lean * (H + 20 - c + 20), H + 20)
    right = (width / 2 + lean * (H + 20 - c + 20), H + 20)
    g = LineString([left, apex, right]).buffer(S / 2, cap_style="flat", join_style="round", quad_segs=32)
    g = g.intersection(CLIP)
    # Soften the apex a little more, leaving the tapered toes sharp.
    soft = g.buffer(-5, join_style="round").buffer(5, join_style="round")
    g = unary_union([soft.intersection(box(-1000, -1000, 1000, 55)), g.intersection(box(-1000, 55, 1000, 1000))])
    return affinity.translate(g, -g.bounds[0], 0)


# ---- M: vertical stems, diagonals meeting in a V.


def letter_m(width=120.0, v_depth=70.0):
    """Vertical stems: a slanted left stroke (tried, to interlock with the A) makes the M read as N."""
    c = S / 2
    pts = [(c, H + 20), (c, -12), (width / 2, v_depth), (width - c, -12), (width - c, H + 20)]
    g = stroke(pts).intersection(CLIP)
    return round_corners(g)


def place(prev, g, gap):
    """Shift g right until its nearest ink is exactly `gap` from prev."""
    g = affinity.translate(g, prev.bounds[2] + gap - g.bounds[0], 0)
    for _ in range(40):
        d = prev.distance(g)
        if abs(d - gap) < 0.01:
            break
        g = affinity.translate(g, gap - d, 0)
    return g


B = letter_b()
A = place(B, letter_a(), GAP_BA)
M = place(A, letter_m(), GAP_AM)

# Hump: a bell curve (sunrise / mountain) on the baseline, centred in the A.
# Its flanks are clipped to the A's open counter shrunk by HUMP_GAP, so the white gap to the legs is even;
# the junctions are then smoothed so the flanks flow into the rounded peak.
# One smooth curve, never clipped: y = H - h * cos(pi*t/2)**P for t in [-1, 1].
# P > 1 gives a bell (soft shoulders, rounded crown). The curve is scaled up until any point
# would come closer than HUMP_GAP to the A, so the gap is exact and there are no corners on the curve.
HUMP_ASPECT = 0.43     # height / full base width, matching the original's proportions
HUMP_P = 0.85
ax = (A.bounds[0] + A.bounds[2]) / 2


def hump_shape(half_w):
    h = HUMP_ASPECT * 2 * half_w
    n = 240
    pts = [(ax + half_w * (2 * i / n - 1), H - h * math.cos(math.pi / 2 * (2 * i / n - 1)) ** HUMP_P) for i in range(n + 1)]
    return Polygon(pts), h


lo, hi = 5.0, 80.0
for _ in range(60):
    mid_w = (lo + hi) / 2
    shape, _ = hump_shape(mid_w)
    if shape.distance(A) >= HUMP_GAP:
        lo = mid_w
    else:
        hi = mid_w
HUMP, HUMP_H = hump_shape(lo)
r = HUMP_H


def to_path(g):
    polys = [g] if isinstance(g, Polygon) else list(g.geoms)
    out = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            pts = list(ring.coords)
            out.append("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts[:-1]) + " Z")
    return " ".join(out)


W = M.bounds[2]
data = {
    "w": round(W, 2), "h": H, "navy": to_path(unary_union([B, A, M])), "teal": to_path(HUMP),
    "b": to_path(B), "a": to_path(A), "m": to_path(M),
    "hump_h": round(HUMP_H, 2), "colors": {"navy": NAVY, "teal": TEAL},
    "b_counters": len(B.interiors),
}
Path(__file__).with_name("monogram.json").write_text(json.dumps(data))
print(f"width {W:.1f}  hump h {HUMP_H:.1f} base {HUMP.bounds[2]-HUMP.bounds[0]:.1f}  B counters {len(B.interiors)}  gaps B-A {B.distance(A):.2f} A-M {A.distance(M):.2f}")
