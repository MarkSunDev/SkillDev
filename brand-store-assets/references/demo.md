# Demo and test record

Demo app: **Harbor**, a fictional focus/productivity product. The screens are
generated placeholders labeled `DEMO CONTENT · NOT FOR SUBMISSION`; they are not
real app UI. The logo is a real SVG mark and is used to test the icon and gallery
pipelines.

## Reproduce

From the skill root:

```bash
cd examples/demo && python3 make_screens.py && cd ../..

python3 scripts/check_logo.py examples/demo/logo.svg \
  --out /tmp/harbor/logo-qa --pretty

python3 scripts/render_icon.py examples/demo/logo.svg \
  --out /tmp/harbor/icons --bg "#1E2A2A" --ink "#F3EFE4" --preset store
python3 scripts/check_assets.py --icons /tmp/harbor/icons --pretty

python3 scripts/render_gallery.py examples/demo/gallery.json \
  --store apple --out /tmp/harbor/apple --overview --feature-graphic
python3 scripts/check_assets.py \
  --gallery /tmp/harbor/apple/gallery.json --store apple --pretty

python3 scripts/render_gallery.py examples/demo/gallery.json \
  --store play --out /tmp/harbor/play --overview --feature-graphic
python3 scripts/check_assets.py \
  --gallery /tmp/harbor/play/gallery.json --store play --pretty
python3 scripts/check_assets.py \
  --feature /tmp/harbor/play/feature-graphic-1024x500.png --pretty
```

## Result on 2026-10-22

### Logo

- `viewBox="0 0 100 100"`
- 2 drawable elements: an open ring and a dot
- thinnest stroke: 7.0/100
- 512 px margin: 17.6%
- 32 px ink coverage: 12.4% (survives favicon size)
- one warning: optical center off by 2.7% due to the dot at the bottom
- status: PASS

### Icons

| File | Size | Alpha | Result |
|---|---|---|---|
| `icon-ios-1024.png` | 1024 × 1024 | No | PASS |
| `icon-play-512.png` | 512 × 512 | Yes (RGBA) | PASS, ~33 KB |
| `icon-mark-1024.png` | 1024 × 1024 | Yes | PASS |
| `icon-adaptive-foreground-432.png` | 432 × 432 | Yes, safe zone | PASS |
| `icon-adaptive-background-432.png` | 432 × 432 | No | PASS |
| `icon-monochrome-432.png` | 432 × 432 | Yes, safe zone | PASS |
| `icon-mask-preview.png` | 1800 × 1200 | No | QA artifact |

`check_assets.py --icons` → `OK: 0 warning(s)`.

### App Store

- 5 images at 1320 × 2868, RGB, no alpha
- 5 exports at 1206 × 2622
- feature graphic 1024 × 500, RGB, no alpha
- overview 3200 × 1280
- `check_assets.py --store apple` → `OK: 0 warning(s)`

### Google Play

- 5 images at 1440 × 2560, RGB, no alpha
- 5 exports at 1080 × 1920
- feature graphic 1024 × 500, RGB, no alpha
- overview 3200 × 1280
- `check_assets.py --store play` → `OK: 0 warning(s)`

The source demo screens are 1320 × 2868 (iPhone aspect) placed inside a Play
9:16 canvas. The device frame derives its aspect from the source, so the screen is
not stretched; the output canvas is 1440 × 2560. For a real Play submission,
capture Android screens at their native portrait resolution.

### AI backdrop test

- `GET /models` listed `gpt-image-2`, `gpt-image-2.5`,
  `grok-imagine-image-quality`, `grok-imagine-image`, and video models.
- `gpt-image-2` and `gpt-image-2.5` returned `service unavailable`.
- `grok-imagine-image-quality` returned a 960 × 960 JPEG for a 1024 × 1024
  request. The script saved the returned size.
- `make_showcase.py` composited the real SVG mark on the generated backdrop at
  1600 × 1200, with a `Showcase · not a store asset` label.

This is an optional path; the core logo, icon, and gallery workflow has no API
dependency.

## Known limitations

- The demo screens are placeholders and must be replaced before any real use.
- `check_assets.py` validates the master gallery files. If you validate an
  export folder, point `--assets-dir` at it and update the manifest `src`/`size`
  values, or run a separate manifest for the export set.
- The renderer needs a local Chromium browser; it does not download one.
- AI model availability, output size, and commercial terms are provider-specific
  and can change without notice.
