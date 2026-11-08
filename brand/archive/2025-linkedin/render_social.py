"""Render social-media PNGs (avatars, covers, link preview) from the traced SVGs.

Run after trace_logo.py, from the project root:  python3 brand/render_social.py
Needs Google Chrome and the site's node_modules (for the fonts). Writes brand/social/*.png.

Sizes follow each platform's current recommendation:
  avatar*.png           1000x1000  LinkedIn company logo, Facebook/X/Google profile (circle-safe)
  linkedin-cover.png    2256x382   LinkedIn company page cover (1128x191 @2x)
  facebook-cover.png    1702x630   Facebook page cover (851x315 @2x)
  x-header.png          1500x500   X / Twitter header
  og-image.png          1200x630   Link previews (site og:image, Slack, iMessage, LinkedIn posts)
"""
import subprocess
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
ROOT = HERE.parent
OUT = HERE / "social"
import glob, os
# Playwright's headless shell: fast, and exits cleanly (full Chrome hangs on teardown in headless mode).
CHROME = os.environ.get("CHROME") or sorted(glob.glob(os.path.expanduser(
    "~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell")))[-1]
FONTS = ROOT / "node_modules/@fontsource-variable"

CSS = f"""
@font-face {{ font-family: 'BrandSerif'; src: url('{FONTS}/source-serif-4/files/source-serif-4-latin-wght-normal.woff2'); font-weight: 200 900; }}
@font-face {{ font-family: 'BrandSans'; src: url('{FONTS}/inter/files/inter-latin-wght-normal.woff2'); font-weight: 100 900; }}
* {{ margin: 0; box-sizing: border-box; }}
html, body {{ width: 100%; height: 100%; overflow: hidden; }}
body {{ background: #0f2a33; color: #f3f7f7; font-family: 'BrandSans'; position: relative;
  background-image: radial-gradient(60% 120% at 85% 0%, rgba(74,95,150,.45), transparent 60%),
                    radial-gradient(50% 100% at 100% 100%, rgba(79,176,180,.25), transparent 60%); }}
.mark {{ position: absolute; opacity: .07; }}
h1 {{ font-family: 'BrandSerif'; font-weight: 500; letter-spacing: -0.015em; line-height: 1.05; }}
.sub {{ font-weight: 600; letter-spacing: .16em; text-transform: uppercase; color: #7cc9cb; }}
"""

EMBLEM = (HERE / "emblem-on-dark.svg").as_uri()
LOGO_DARK = (HERE / "logo-on-dark.svg").as_uri()


def page(body):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"


# Covers: LinkedIn/X put the profile picture over the bottom-left, so content sits to the right.
right_text = lambda size, sub, mark_h, mark_right: page(f"""
  <img class="mark" src="{EMBLEM}" style="height:{mark_h}px; right:{mark_right}px; top:50%; transform:translateY(-50%)">
  <div style="position:absolute; right:7%; top:50%; transform:translateY(-50%); text-align:right">
    <h1 style="font-size:{size}px">Innovation for good.</h1>
    <p class="sub" style="font-size:{sub}px; margin-top:{sub * 1.1}px">Est. 2018 &nbsp;·&nbsp; bamteamservices.com</p>
  </div>""")

centered = lambda logo_h, size, sub: page(f"""
  <img class="mark" src="{EMBLEM}" style="height:140%; right:-6%; top:-20%">
  <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center">
    <img src="{LOGO_DARK}" style="height:{logo_h}px">
    <h1 style="font-size:{size}px; margin-top:{size * 0.75}px">Innovation for good.</h1>
    <p class="sub" style="font-size:{sub}px; margin-top:{sub * 1.0}px">Est. 2018 &nbsp;·&nbsp; bamteamservices.com</p>
  </div>""")

svg_page = lambda name: page(f"<img src='{(OUT / name).as_uri()}' style='width:100%;height:100%;display:block'>")

JOBS = [
    # name, css width, css height, device scale, html
    ("avatar.png", 1000, 1000, 1, svg_page("avatar.svg")),
    ("avatar-dark.png", 1000, 1000, 1, svg_page("avatar-dark.svg")),
    ("linkedin-cover.png", 1128, 191, 2, right_text(46, 12, 300, -40)),
    ("facebook-cover.png", 851, 315, 2, centered(84, 36, 11)),
    ("x-header.png", 1500, 500, 1, right_text(84, 20, 760, -120)),
    ("og-image.png", 1200, 630, 1, centered(170, 60, 18)),
]

OUT.mkdir(exist_ok=True)
tmp = HERE / ".render"
tmp.mkdir(exist_ok=True)
for name, w, h, dpr, html in JOBS:
    # Headless Chrome keeps a minimum window size, so pin the body to w x h and crop the screenshot.
    html = html.replace("<body>", f"<body style='width:{w}px;height:{h}px'>", 1).replace(
        "html, body { width: 100%; height: 100%;", "html, body {", 1)
    src, shot = tmp / f"{name}.html", tmp / name
    src.write_text(html)
    r = subprocess.run([CHROME, "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                        f"--force-device-scale-factor={dpr}", f"--window-size={max(w, 800)},{max(h, 800)}",
                        "--virtual-time-budget=3000", f"--screenshot={shot}", src.as_uri()], capture_output=True, text=True, timeout=60)
    if not shot.exists():  # Chrome often exits non-zero on teardown after writing the file
        raise SystemExit(f"{name}: chrome failed ({r.returncode})\n{r.stderr[-800:]}")
    Image.open(shot).convert("RGB").crop((0, 0, w * dpr, h * dpr)).save(OUT / name, optimize=True)
    print(name, Image.open(OUT / name).size)
for f in tmp.iterdir():
    f.unlink()
tmp.rmdir()
