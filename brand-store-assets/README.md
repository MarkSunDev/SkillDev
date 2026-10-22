# Brand & Store Assets

A Codex/ZCode skill for designing app logos and icons, then rendering App Store
and Google Play five-image store galleries from real app screenshots.

It produces:

- six logo directions and a structural/small-size QA sheet
- iOS 1024, Play 512, Android adaptive 432, favicon/PWA icons, and mask previews
- App Store five-image set at 1320 × 2868 + 1206 × 2622
- Google Play five-image set at 1440 × 2560 + 1080 × 1920
- Play feature graphic at 1024 × 500
- an overview contact sheet and machine-checkable manifests
- optional AI-generated abstract backdrops and deterministic brand showcases

Everything is rendered with HTML/CSS → PNG through a locally installed
Chromium-based browser. No Playwright, Puppeteer, CairoSVG, or ImageMagick.

## Install

### Codex

From the parent directory of this folder:

```bash
cp -R brand-store-assets ~/.codex/skills/brand-store-assets
```

Or clone/symlink the folder into `~/.codex/skills/`.

### ZCode

ZCode loads user skills from `~/.agents/skills/`. From inside this folder:

```bash
cp -R "$(pwd)" ~/.agents/skills/brand-store-assets
```

Or symlink it:

```bash
ln -s "$(pwd)" ~/.agents/skills/brand-store-assets
```

The folder name and the `name:` in `SKILL.md` are both `brand-store-assets`.

## Requirements

- Python 3.9+
- Pillow and NumPy:

```bash
python3 -m pip install -r requirements.txt
```

- One Chromium-based browser: Google Chrome, Chromium, Microsoft Edge, Brave, or
  Vivaldi. The renderer auto-detects common install paths. Override with:

```bash
export BROWSER_BIN="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
```

- Optional, for AI backdrops and fictional cast portraits: `curl` (preferred) or
  Python's `urllib`, plus an image-generation API key.

## Quick start

```bash
# Logo QA
python3 scripts/check_logo.py path/to/mark.svg --out out/logo-qa --pretty

# Icon set
python3 scripts/render_icon.py path/to/mark.svg \
  --out out/icons --bg "#1E2A2A" --ink "#F3EFE4" --preset store

# Art direction: random dating/social pack; use --next if unhappy
python3 scripts/style_packs.py --random

# High-conversion poster set (Pixel for Play, iPhone 18 for App Store)
python3 scripts/render_gallery.py poster-play.json --store play --frame pixel \
  --out out/play --overview --feature-graphic
python3 scripts/render_gallery.py poster-apple.json --store apple --frame iphone \
  --out out/apple --overview

# Repair a placeholder/avatar/photo region in an existing screenshot
python3 scripts/repair_region.py base/likes.png people/isabella.png \
  --rect 18,300,265,245 --radius 30 --centering 0.5,0.22 \
  --fade-bottom 80 --fade-color "#2B1E24" --out screens/likes.png

# Mockups + fictional cast (optional mockup mode)
python3 scripts/generate_cast.py --config /path/to/ai_config.md \
  --style portrait --prompt "fictional adult, high-neck top, head-and-shoulders" \
  --out cast/maya.png
python3 scripts/render_mockups.py mockups.json --out mockups/play \
  --width 1080 --height 2400
python3 scripts/render_mockups.py mockups.json --out mockups/apple \
  --width 1320 --height 2868

# Validate
python3 scripts/check_assets.py --icons out/icons --pretty
python3 scripts/check_assets.py --gallery out/apple/gallery.json --store apple --pretty
python3 scripts/check_assets.py --gallery out/play/gallery.json --store play --pretty
python3 scripts/check_assets.py --feature out/play/feature-graphic-1024x500.png --pretty
```

## Demo

`examples/demo/` contains a fictional "Harbor" app with a logo, a manifest, and
five generated placeholder screens. The placeholders are labeled
`DEMO CONTENT · NOT FOR SUBMISSION`; replace them with real captures.

```bash
cd examples/demo && python3 make_screens.py && cd ../..
python3 scripts/render_gallery.py examples/demo/gallery.json \
  --store apple --out /tmp/harbor/apple --overview --feature-graphic
```

See `examples/demo/README.md` for the complete command sequence.

## Structure

```text
brand-store-assets/
  SKILL.md
  README.md
  agents/openai.yaml
  references/
    logo-system.md
    gallery-system.md
    high-conversion-store-patterns.md
    layer-compositing.md
    screenshot-repair.md
    mockups-and-cast.md
    dating-style-packs.md
    store-specs.md
    research-and-ai.md
    demo.md
  scripts/
    _render.py              # browser detection, HTML injection, screenshots
    check_logo.py           # SVG structure + 512/32 px QA
    render_icon.py          # iOS/Play/adaptive/favicon exports + mask sheet
    render_gallery.py       # five images, exports, feature graphic, overview
    make_overview.py        # rebuild an overview from a rendered gallery
    check_assets.py         # icons, gallery, feature graphic validators
    generate_backdrop.py    # optional AI abstract backdrop
    generate_cast.py        # fictional adult cast for mockups (text-only)
    render_mockups.py       # deterministic app-screen mockups
    repair_region.py        # fill placeholder/photo regions without touching UI
    style_packs.py          # random/next picker for 30 dating style packs
    make_showcase.py        # deterministic logo + backdrop composite
  assets/
    templates/              # gallery, poster, app-screen, feature, overview, icon, showcase
    style-packs/dating.json # 30 art-direction packs
    fonts/                  # Instrument Serif + Public Sans (OFL)
  examples/demo/            # fictional demo, placeholder screens
```

## Design decisions

- **HTML/CSS + local browser** gives exact pixel dimensions, real font metrics,
  and CSS `color-mix`/gradients without a heavy rendering dependency. The browser
  is already installed on most design machines.
- **The device is sized from the source aspect and the available height.** A full
  portrait phone plus a footer cannot both be 70% wide on a 9:16 Play canvas; the
  template fits the device above the footer instead of clipping it.
- **The screenshot stays a real raster.** The phone frame and all typography are
  CSS; the app UI is an untouched image layer inside the frame.
- **Five images** are an editorial convention. Both stores accept more; five is
  enough to tell a complete story without repeating a screen.
- **AI is decorative only.** Generated images never become store screenshots or
  the logo. The real SVG mark is composited deterministically over any backdrop.
- **Validators are conservative.** They check documented dimensions, alpha,
  Play's 2:1 rule, icon safe zones, copy length, and contrast. They do not claim a
  store will accept an asset.
- **Poster mode is for conversion, editorial mode is for restraint.** The poster
  template uses big type, color blocks, a Pixel/iPhone frame, badges, stickers,
  and callouts. The phone frame must remain fully visible.
- **Layer compositing preserves the approved layout.** If only the people/content
  change, keep the original screenshot, replace the profile card/avatars/photo
  regions, and add the marketing layers. Do not rebuild the whole UI. See
  `references/layer-compositing.md`.
- **Overflow cards peek from behind the phone.** A card may exceed the frame, but
  keep it behind the device (about 80% visible, 20% hidden) and align its text to
  the visible side. A card over the app's name or primary control is a bug.
- **Mockups are explicit, not silent.** If the user wants a new screen/feature or
  there is no usable base, rebuild the UI deterministically and generate a new
  fictional cast. Never reuse the supplied person's photo, and never present a
  mockup as a real build capture.
- **Style packs are one-per-set.** Pick one of the 30 dating/social packs at
  random; use `--next` when the user wants a different direction. Do not mix two
  packs in one carousel.

## Licenses

- Bundled fonts: Instrument Serif and Public Sans, SIL Open Font License. See
  `assets/fonts/OFL-*.txt`.
- Logo methodology adapted from
  [`op7418/logo-generator-skill`](https://github.com/op7418/logo-generator-skill)
  (MIT).
- Icon research: [iconLibrary](https://iconlibrary.top/), [Lucide](https://lucide.dev/packages)
  (ISC). [Mobbin](https://mobbin.com/) is a paid reference library; its screens
  are not redistributed here.
- The renderer uses the locally installed browser; no browser binaries are
  redistributed.
