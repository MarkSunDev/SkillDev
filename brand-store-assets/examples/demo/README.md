# Demo: Harbor

A fictional focus/productivity app used to test the full pipeline. The screens in
`screens/` are **generated placeholders**, clearly labeled `DEMO CONTENT · NOT FOR
SUBMISSION`. They are abstract and not real app UI. Replace them with real build
captures before using the output anywhere.

## Regenerate the demo screens

```bash
python3 make_screens.py
```

## Run the full pipeline

From the skill root (`brand-store-assets/`):

```bash
# 1. Logo structural and small-size QA
python3 scripts/check_logo.py examples/demo/logo.svg \
  --out /tmp/harbor/logo-qa --pretty

# 2. Icon set
python3 scripts/render_icon.py examples/demo/logo.svg \
  --out /tmp/harbor/icons --bg "#1E2A2A" --ink "#F3EFE4" --preset store
python3 scripts/check_assets.py --icons /tmp/harbor/icons --pretty

# 3. App Store five-image set
python3 scripts/render_gallery.py examples/demo/gallery.json \
  --store apple --out /tmp/harbor/apple --overview --feature-graphic
python3 scripts/check_assets.py \
  --gallery /tmp/harbor/apple/gallery.json --store apple --pretty

# 4. Google Play five-image set
python3 scripts/render_gallery.py examples/demo/gallery.json \
  --store play --out /tmp/harbor/play --overview --feature-graphic
python3 scripts/check_assets.py \
  --gallery /tmp/harbor/play/gallery.json --store play --pretty
python3 scripts/check_assets.py \
  --feature /tmp/harbor/play/feature-graphic-1024x500.png --pretty

# 5. Optional: AI backdrop + deterministic showcase
python3 scripts/generate_backdrop.py --config /path/to/ai_config.md \
  --style ink --out /tmp/harbor/backdrop.png
python3 scripts/make_showcase.py /tmp/harbor/backdrop.png examples/demo/logo.svg \
  --name "Harbor" --tagline "Make room to think." \
  --accent "#D9A441" --out /tmp/harbor/showcase.png
```

## Expected result

- `logo-qa.png` shows the mark on paper, on dark, in circle/squircle masks, and at
  128/64/32/16 px. The demo mark passes with one optical-center warning (the dot
  intentionally adds weight at the bottom).
- `icons/` contains iOS 1024 RGB, Play 512 RGBA, transparent mark, adaptive
  layers, monochrome layer, and the mask preview.
- `apple/` contains five 1320 × 2868 PNGs, five 1206 × 2622 exports, a
  1024 × 500 feature graphic, an overview, and `gallery.json`.
- `play/` contains five 1440 × 2560 PNGs, five 1080 × 1920 exports, the same
  feature graphic, an overview, and `gallery.json`.
- `check_assets.py` reports `OK` for both galleries, the feature graphic, and the
  icon set (the demo screens are 1320 × 2868 inside a Play device frame, which is
  accepted; the output canvas is 9:16).

## Replace the demo

1. Put the real SVG mark in `logo.svg` (or point `brand.logo` at it).
2. Replace `screens/01.png`–`05.png` with real captures from the submitted build.
3. Update `gallery.json` copy, palette, and `screen` paths.
4. Set `store` to `apple` or `play`, or omit it and pass `--store`.
5. Re-run the commands above. Inspect every output; do not upload blind.
