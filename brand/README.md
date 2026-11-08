# BAM Team Services brand (v1.0, locked 2026-11-08)

The BAM monogram with the teal hump in the A: a sunrise over a summit. Built from the "Digital Brand Specifications v1.0" concept sheet (`source/concept-sheet.png`) and redrawn as exact vector geometry.

## Colors

| Name | Hex | Use |
|---|---|---|
| Primary Navy | `#082F50` | BAM lettering, company name, headings, dark backgrounds |
| Accent Teal | `#079D9F` | The hump, large accents and fills |
| White | `#FFFFFF` | Backgrounds, reversed lettering |

Solid fills only: no gradients, shadows or effects. On the website, small teal *text* on white uses `#06797B` (the same hue, deepened to pass WCAG AA contrast); `#079D9F` is too light for small text.

## Type

- **BAM monogram:** custom vector paths. Never typeset it.
- **TEAM SERVICES:** Montserrat SemiBold, uppercase, spaced. BAM is not repeated: the monogram already says it.
- **Innovation for Good:** Montserrat Medium, upright, no ™.
- **Website:** Montserrat SemiBold headings, Inter body.

## Files

| Folder | Contents |
|---|---|
| `svg/` | Masters, all text outlined. `bam-primary` (1600×900 canvas), `bam-header` (1200×320), `-dark` versions on navy, `bam-header-tight` (cropped, for web headers), `bam-avatar` (1024), `bam-app-icon` (512), `bam-monogram`, `bam-favicon-a` (16 px favicon: A + hump) |
| `png/` | `bam-primary-1600x900` (transparent) and dark, `bam-header-1200x320` and dark, `bam-avatar-1024`, `bam-app-icon-512/192/180/32`, `bam-favicon-16`, `favicon.ico` (16/32/48) |
| `social/` | `avatar-1024` (LinkedIn, Facebook, X, Google profile), `linkedin-cover` (2256×382), `facebook-cover` (1702×630), `x-header` (1500×500), `og-image` (1200×630, link previews) |
| `source/` | The generators and fonts (Montserrat, SIL OFL) |
| `archive/2025-linkedin/` | The previous emblem logo and its assets. Retired. |

## Rules

- The monogram never changes: same shapes, same hump position and proportion. Only the layout, name, tagline and background change.
- Clear space around the logo: at least half the height of the B.
- Don't stretch, skew, outline, recolor or add effects.
- Leave the tagline off avatars and icons.
- Below 32 px use `bam-favicon-a` (the A and hump); the full monogram is unreadable at 16 px.

## Construction (source/monogram.py)

Cap height 100 units, one stroke weight (22) for every letter, corners rounded at 3.6. The B has a continuous stem and two enclosed openings (lower bowl wider). The A has no crossbar, a round apex and feet cut flat on the baseline so each toe tapers to a point. The M has vertical stems (a slanted left stem was tried and reads as N). B–A and A–M gaps are equal, measured ink to ink. The hump is one smooth curve, `y = h·cos(πt/2)^0.85`, height/base 0.43, scaled until its whole outline sits exactly 5.5 units from the A's legs.

## Regenerating

```sh
python3 -m venv /tmp/bam-brand && /tmp/bam-brand/bin/pip install shapely fonttools
/tmp/bam-brand/bin/python brand/source/monogram.py   # geometry -> source/monogram.json
/tmp/bam-brand/bin/python brand/source/formats.py    # svg/
python3 brand/source/export.py                       # png/, social/ (needs pillow + Playwright's Chromium)
```
