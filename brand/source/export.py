"""Export PNGs, favicon.ico and social images from the SVG masters (brand/svg).

Run after formats.py:  python3 brand/source/export.py
Needs pillow and a Chromium headless shell (Playwright's cache is used automatically; set CHROME to override).
"""
import glob
import os
import subprocess
from pathlib import Path

from PIL import Image

SRC = Path(__file__).resolve().parent
BRAND = SRC.parent
SVG, PNG, SOCIAL = BRAND / "svg", BRAND / "png", BRAND / "social"
TMP = BRAND / ".render"
CHROME = os.environ.get("CHROME") or sorted(glob.glob(os.path.expanduser(
    "~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell")))[-1]
NAVY, TEAL, WHITE = "#082F50", "#079D9F", "#FFFFFF"
FONT = (SRC / "fonts/Montserrat-600.ttf").as_uri()
FONT_MED = (SRC / "fonts/Montserrat-500.ttf").as_uri()


def shoot(html, w, h, out, dpr=1, transparent=False):
    """Render html at w x h CSS px (x dpr) to out. Headless Chrome keeps a minimum window, so crop."""
    TMP.mkdir(exist_ok=True)
    page = TMP / (out.stem + ".html")
    page.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>"
                    f"@font-face{{font-family:M;src:url('{FONT}');font-weight:600}}"
                    f"@font-face{{font-family:M;src:url('{FONT_MED}');font-weight:500}}"
                    f"*{{margin:0;box-sizing:border-box}}html,body{{background:transparent}}"
                    f"body{{width:{w}px;height:{h}px;overflow:hidden;position:relative;font-family:M,sans-serif}}"
                    f"</style></head><body>{html}</body></html>")
    shot = TMP / (out.stem + ".shot.png")
    args = [CHROME, "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
            f"--force-device-scale-factor={dpr}", f"--window-size={max(w, 800)},{max(h, 800)}",
            "--virtual-time-budget=3000", f"--screenshot={shot}"]
    if transparent:
        args.append("--default-background-color=00000000")
    subprocess.run(args + [page.as_uri()], capture_output=True, timeout=60)
    im = Image.open(shot).crop((0, 0, w * dpr, h * dpr))
    im = im if transparent else im.convert("RGB")
    out.parent.mkdir(exist_ok=True)
    im.save(out, optimize=True)
    print(f"{out.relative_to(BRAND)}  {im.size[0]}x{im.size[1]}")


def svg_img(name, style="width:100%;height:100%"):
    return f"<img src='{(SVG / name).as_uri()}' style='display:block;{style}'>"


# ---- Logo PNGs (spec section 4)
shoot(svg_img("bam-primary.svg"), 1600, 900, PNG / "bam-primary-1600x900.png", transparent=True)
shoot(svg_img("bam-primary-dark.svg"), 1600, 900, PNG / "bam-primary-dark-1600x900.png")
shoot(svg_img("bam-header.svg"), 1200, 320, PNG / "bam-header-1200x320.png", transparent=True)
shoot(svg_img("bam-header-dark.svg"), 1200, 320, PNG / "bam-header-dark-1200x320.png")
shoot(svg_img("bam-avatar.svg"), 1024, 1024, PNG / "bam-avatar-1024.png", transparent=True)
shoot(svg_img("bam-app-icon.svg"), 512, 512, PNG / "_icon512.png", transparent=True)
big = Image.open(PNG / "_icon512.png")
for s in (512, 192, 180, 32):
    big.resize((s, s), Image.LANCZOS).save(PNG / f"bam-app-icon-{s}.png", optimize=True)
    print(f"png/bam-app-icon-{s}.png  {s}x{s}")
(PNG / "_icon512.png").unlink()
shoot(svg_img("bam-favicon-a.svg"), 256, 256, PNG / "_fav256.png", transparent=True)
fav = Image.open(PNG / "_fav256.png")
fav.resize((16, 16), Image.LANCZOS).save(PNG / "bam-favicon-16.png", optimize=True)
# favicon.ico: 16 px uses the A + hump, 32 and 48 use the full monogram.
ico_32 = big.resize((32, 32), Image.LANCZOS)
fav.resize((16, 16), Image.LANCZOS).save(PNG / "favicon.ico", format="ICO",
                                          append_images=[ico_32, big.resize((48, 48), Image.LANCZOS)],
                                          sizes=[(16, 16), (32, 32), (48, 48)])
(PNG / "_fav256.png").unlink()
print("png/favicon.ico  16, 32, 48")

# ---- Social (brand/social)
BG = f"background:{NAVY};"
shoot(svg_img("bam-avatar.svg"), 1024, 1024, SOCIAL / "avatar-1024.png")

# LinkedIn / X: the profile picture covers the lower-left, so the line sits to the right.
cover = lambda size, sub: (
    f"<div style='{BG}position:absolute;inset:0;display:flex;align-items:center;justify-content:flex-end;padding-right:7%'>"
    f"<div style='text-align:right;color:{WHITE}'><div style='font-weight:600;font-size:{size}px;letter-spacing:-0.01em'>Innovation for Good</div>"
    f"<div style='margin-top:{sub * 0.9}px;font-weight:600;font-size:{sub}px;letter-spacing:0.22em;color:{TEAL}'>BAMTEAMSERVICES.COM</div></div></div>")
shoot(cover(40, 12), 1128, 191, SOCIAL / "linkedin-cover.png", dpr=2)
shoot(cover(72, 18), 1500, 500, SOCIAL / "x-header.png")

# Facebook / link preview: the primary logo, centred (mobile crops the sides of Facebook covers).
centred = lambda logo_w: (f"<div style='{BG}position:absolute;inset:0;display:grid;place-items:center'>"
                          f"{svg_img('bam-primary-dark.svg', f'width:{logo_w}px;height:auto')}</div>")
shoot(centred(560), 851, 315, SOCIAL / "facebook-cover.png", dpr=2)
shoot(centred(820), 1200, 630, SOCIAL / "og-image.png")

for f in TMP.iterdir():
    f.unlink()
TMP.rmdir()
