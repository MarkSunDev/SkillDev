---
name: brand-store-assets
description: Design app logos and app icons, then render high-conversion App Store / Google Play store images (商店五图 + feature graphic) from real screenshots or deterministic mockups with a generated fictional cast. Use for logo / 品牌标志, app icon, store screenshots, poster sets, feature graphic, Pixel / iPhone 18 frames, dating/social style packs, app mockups, screenshot copy, or validating exported store assets.
---

# Brand & Store Assets

Produce a coherent brand mark and the store artwork that follows from it:

1. **Logo system** — 6 distinct SVG directions, critique, refinement, and a locked mark.
2. **App icon set** — iOS 1024, Google Play 512, Android adaptive layers, favicon/PWA sizes, and mask/small-size QA.
3. **Editorial store set** — 1320 × 2868 / 1440 × 2560 masters, real screens, shared quiet layout.
4. **High-conversion poster set** — big benefit headline, color-blocked panels, Pixel / iPhone 18 device frames, proof badges, callouts, and a custom app screen per panel.
5. **Play feature graphic** — 1024 × 500, one message, no alpha.
6. **Mockups and fictional cast** — deterministic app screens rebuilt from the product's design system, with generated fictional adults when the user asks to change the content.
7. **Screenshot repair** — fill placeholder silhouettes, gray avatars, empty cards, or missing photo regions with fictional content while keeping the UI and text intact.
8. **Review artifacts** — overview contact sheets, `gallery.json`, `icon-manifest.json`, validation reports.

The renderer is deterministic HTML/CSS → PNG through a local Chromium browser. No Playwright, Puppeteer, CairoSVG, or ImageMagick is required.

## Hard rules

- **Three source modes.** For a submitted build, use real screenshots. If the user wants the approved layout kept and only people/content replaced, use **layer compositing**: base screenshot + new subject layers + original UI untouched. Use a **full mockup** only when the user wants a new screen/feature or no usable base exists. Label a mockup internally; never claim it is a real build capture.
- **Preserve the layout when replacing people.** Do not rebuild the whole app UI just to change a face. Overlay the new profile card/avatar/photo at the exact original bounds; keep the header, controls, copy, and nav intact.
- **Overflow cards peek from behind the phone.** Let a card exceed the frame, but keep it behind the device and align its text to the visible side. Do not cover the app's primary control, name, or nav.
- **Repair, don't redesign.** Fill only the placeholder/missing region. Keep the original text, layout, and navigation. Use `scripts/repair_region.py` for silhouettes, gray avatars, empty cards, and missing photos; use a card layer only when the text is inside the region.
- **Never reuse the supplied person.** If the screenshot contains a person and the content must change, generate a new fictional adult from text only. Delete any output with exposed chest, suggestive pose, celebrity likeness, text, or logos.
- **AI is for decoration and fictional cast only.** Generated images may be abstract backdrops or fictional adult portraits for mockups. They are never app UI, never the final logo, and never a real person's likeness.
- **Correct device frame.** Google Play uses a Pixel frame; the App Store uses an iPhone 18 frame when the set is device-specific. Keep the frame fully visible, including its bottom edge.
- **One style pack per set.** For dating/social, pick one of the 30 built-in packs. Random is a starting point, not a mandate: reject a pack that fights the app's own palette/type. Use `next` when the user is unhappy. Do not mix two packs in one carousel.
- **iOS icon:** exactly 1024 × 1024, RGB, no alpha, no baked rounded corners, no transparency. Apple applies the mask.
- **Google Play icon:** exactly 512 × 512, 32-bit PNG with an alpha channel, at most 1 MB. Full-bleed artwork is safer than a floating transparent mark.
- **Store screenshots:** flattened RGB, no alpha. Apple masters 1320 × 2868 and 1206 × 2622. Play masters 1440 × 2560 and 1080 × 1920.
- **Five images, five distinct screens.** Image 01 is the hero and carries the core promise. Do not reuse a screen or output filename. Play accepts 2–8; use `--allow-count` only when the brief genuinely calls for fewer than five.
- **No unverifiable claims.** No star ratings, awards, rankings, "Editor's Choice", "#1", or download call-to-actions.
- **Re-check live specs.** Store requirements change. The numbers here are current as of October 2026; verify in App Store Connect / Play Console before submitting.
- **Never store API keys in this skill.** Read them from an environment variable or the user's local config file.

## Inputs

Collect or derive these before designing:

| Input | Why it matters |
|---|---|
| App name and one-line promise | Drives the mark and image 01 |
| Category and audience | Sets the visual temperature and copy |
| Three brand traits | e.g. calm, precise, warm — the critique vocabulary |
| Existing logo / palette / typeface | Preserve brand equity; do not redesign for novelty |
| Competitors or references | Distinctiveness check; never copy |
| Store targets | Apple, Play, or both; tablet tiers |
| Source mode | Real screenshots, or an explicit request to change the app content (mockup) |
| Real screenshots | 5 distinct screens from the submitted build, or the design reference for a mockup |
| Art-direction pack | A random/next/specific pack from `assets/style-packs/dating.json` |
| Reference set | High-conversion examples; extract structure, never copy |
| Version and locale | Footer, overview title, copy language |

If a fact cannot be derived, mark it `[待确认]` and keep going. Do not invent a legal entity, rating, URL, or metric.

## Workflow

### Phase 0 — Inspect the project

1. Read the PRD, design tokens, and existing brand files.
2. Inventory the real screens available. If fewer than five distinct screens exist, ask for captures or a build path; do not fabricate them.
3. Confirm the store targets and device tiers.
4. Decide whether the logo already exists. If it does, skip to Phase 2.

### Phase 0.5 — Choose source mode and art direction

**Source mode**

- **Real** — the default for a submitted build. Use the actual build screens.
- **Layer composite** — the preferred mode when the layout is approved and only the people/content should change. Keep the original screenshot as the base; replace only the profile card, avatars, or photo regions; add overflow cards. Read `references/layer-compositing.md` before cutting anything.
- **Mockup** — only when the user wants a new screen/feature or no usable base exists. Rebuild the screens deterministically from the app's design system and generate a new fictional cast. Read `references/mockups-and-cast.md`.

**Art direction**

For dating/social, pick one of the 30 packs in `assets/style-packs/dating.json`:

```bash
python3 scripts/style_packs.py --random
python3 scripts/style_packs.py --next   # use when the user is unhappy
```

Do not mix packs in one set. Read `references/dating-style-packs.md` for the list,
palette roles, and how to apply a pack. Read
`references/high-conversion-store-patterns.md` before planning the panels.

**Layout**

- `editorial` — quiet, typographic, best for a real build with strong screens.
- `poster` — high-conversion: big benefit headline, color-blocked fields, Pixel /
  iPhone 18 frame, badge, sticker, callout, and an optional overflow card that
  peeks out from behind the phone.

When the user says the layout changed too much, switch from full mockup to layer
compositing. Keep the original UI; only replace the people and add the marketing
layers.

### Phase 1 — Logo directions

Generate **six genuinely different SVG variants**, not six parameter tweaks. Use the pattern families in `references/logo-system.md`:

1. monogram / letterform
2. open ring / aperture
3. negative-space cut
4. dot matrix / particle
5. stacked bars / rhythm
6. node network, wave, or folded plane as the wildcard

For each variant, state the idea in one sentence and why it fits the product. Keep every master on `viewBox="0 0 100 100"`, use `currentColor`, and keep critical strokes at 2.5–4 units (7–8 for a deliberately bold icon). Generate the SVGs as files, then run:

```bash
python3 scripts/check_logo.py path/to/mark.svg --out qa/logo --ink "#1F1D1A" --bg "#F7F4ED" --pretty
```

The checker renders 512 px and 32 px versions, measures margins, optical centering, ink coverage, and produces `logo-qa.png`. Fix every error; treat warnings as design feedback. Present the six variants, narrow to 2–3, then refine only the selected direction.

### Phase 2 — Lock the mark and icon system

1. Choose the final mark and one palette: field, ink, accent. Check contrast.
2. Export the complete icon set:

```bash
python3 scripts/render_icon.py path/to/mark.svg \
  --out out/icons \
  --bg "#1E2A2A" --ink "#F3EFE4" \
  --preset store
```

Outputs: `icon-ios-1024.png`, `icon-play-512.png`, `icon-mark-1024.png`, Android adaptive foreground/background/monochrome at 432 px, and `icon-mask-preview.png`.

3. Inspect `icon-mask-preview.png`: the mark must survive the iOS squircle, circle, rounded square, full square, and 16 px. If it does not, simplify or thicken the mark.
4. `--preset all` also exports Android legacy 48–192 px, favicons, Apple touch icon, and PWA icons.

```bash
python3 scripts/check_assets.py --icons out/icons --pretty
```

### Phase 3 — Plan the five-image story

Fill a five-row table before rendering:

| # | Story beat | Source screen | Eyebrow | Headline (2 lines) | Supporting copy (2 lines) | Proof prop | Footer | Field |
|---|---|---|---|---|---|---|---|---|
| 01 | Core promise + primary screen | `screen-01.png` | `DISCOVER` | `The city is / still awake.` | `Real profiles nearby. / Swipe or say hi.` | `REAL PROFILES` badge + `SWIPE →` | `Dating, after dark.` | `#F4EBDD` |
| 02 | Second pillar | `screen-02.png` | ... | ... | ... | ... | ... | ... |
| 03 | Third pillar | `screen-03.png` | ... | ... | ... | ... | ... | ... |
| 04 | Signature differentiator | `screen-04.png` | ... | ... | ... | ... | ... | ... |
| 05 | Personalization / trust | `screen-05.png` | ... | ... | ... | ... | ... | ... |

Use one distinct product pillar per image. Read `references/gallery-system.md` for category-specific sequences, copy formulas, and length caps. For a high-conversion set, also read `references/high-conversion-store-patterns.md`:

- one idea per panel; the headline is the hero
- a proof prop that explains the headline (badge, sticker, callout, card)
- the phone is a prop; keep the correct frame visible
- the app screen must prove this panel's claim, not repeat the home screen
- alternate the field colors from the chosen style pack

Keep the headline to two short lines and the body to two concrete lines. If the copy does not fit, shorten it; do not shrink the type below readability.

### Phase 4 — Prepare the app screens

**Real mode**

Capture from the submitted build at the native phone resolution. Check:

- one locale, one appearance (light or dark), one status-bar time
- full battery / signal, no debug banner, no internal IDs
- representative demo data, no real personal data
- the primary control of each screen visible
- distinct screens, not five crops of the same screen
- store status bar and navigation intact

Do not upscale. Do not upload a raw 20:9 capture for Play; place it inside the device frame on a 9:16 canvas.

**Layer-compositing mode**

Use this when the layout is approved and only the people/content should change.

1. Keep the base screenshot; remove only the browser/window chrome.
2. Identify each person region:
   - **Full profile card** — replace the whole card at its exact bounds and recreate
     the original gradient, progress bars, name, location, tags, and radius.
   - **Avatar** — replace only the circular region.
   - **Photo/selfie** — replace only the rounded-rectangle region.
3. Generate new fictional adults with text only: full-body/three-quarter for a
   profile card, head-and-shoulders for an avatar. Inspect and delete failures.
4. Composite the subject layer over the base. Keep the header, action buttons,
   post text, timestamps, and nav untouched.
5. Add one overflow card behind the phone: about 80% visible, 20% behind the
   frame, with its text aligned to the visible side. Do not cover the primary UI.
6. If the imperfection is a placeholder silhouette, gray avatar, or empty card,
   use `scripts/repair_region.py` to fill only that region; keep the name/label
   outside it. Read `references/screenshot-repair.md`.
7. Read `references/layer-compositing.md` for the exact workflow, masks, and QA.

A project-local compositor is usually clearest. The Flicker example uses
`flicker-store/compose_layers.py`; a generic version needs the same inputs: base
screenshot, subject images, region rectangles, and text settings.

**Mockup mode**

1. Extract the app's tokens: background, card, line, ink, coral/peach accent,
   display serif, body sans, header sizes, nav, pills, action buttons.
2. Build five screen types: Discover, Feed, Likes, Chat (a real conversation
   thread), Me. Do not reuse the same screen with a new caption.
3. Generate a fictional cast with text-only prompts:

```bash
python3 scripts/generate_cast.py --config /path/to/ai_config.md \
  --style portrait --size 1024x1536 \
  --prompt "Maya, a fictional 27-year-old woman, fully buttoned black denim jacket over a high-neck cream turtleneck, head-and-shoulders portrait, city street at night, natural skin, professional casting photo" \
  --out cast/maya.png
```

4. Inspect every portrait. Delete any output with exposed chest, a suggestive
   pose, celebrity likeness, text, or logos. Regenerate with a high neckline,
   head-and-shoulders framing, and a stronger negative prompt.
5. Write `mockups.json` with the cast and screen copy, then render both device
   sizes:

```bash
python3 scripts/render_mockups.py mockups.json --out mockups/play \
  --width 1080 --height 2400
python3 scripts/render_mockups.py mockups.json --out mockups/apple \
  --width 1320 --height 2868
```

Do not use the supplied person's photo as an input or a reference. Do not present
a mockup as a real build capture.

### Phase 5 — Render the galleries

Create a manifest (`gallery.json`) next to the logo and screenshots. Minimal shape:

```json
{
  "app": "Harbor",
  "version": "1.0",
  "store": "apple",
  "brand": { "name": "Harbor", "logo": "logo.svg" },
  "feature_graphic": {
    "headline": ["A calmer way", "to get things done."],
    "support": "Plan, focus, and close the day.",
    "bg": "#1E2A2A",
    "ink": "#F3EFE4",
    "accent": "#D9A441",
    "mood": "glow"
  },
  "images": [
    {
      "slug": "01-focus",
      "feature": "LESS NOISE",
      "title": ["Less noise.", "More focus."],
      "body": ["One calm workspace for the day.", "No feeds, no clutter."],
      "footer": "Harbor. Make room to think.",
      "bg": "#1E2A2A",
      "ink": "#F3EFE4",
      "accent": "#D9A441",
      "screen": "screens/01.png"
    }
  ]
}
```

`screen` is the real app capture, or a deterministic mockup screen. `src` is the rendered output and is written by the renderer. Keep `artwork` for provenance if useful.

For a high-conversion poster set, set `layout` and add the proof props:

```json
{
  "layout": "poster",
  "frame": "pixel",
  "images": [
    {
      "slug": "01-discover",
      "feature": "DISCOVER",
      "title": ["The city is", "still awake."],
      "body": ["Real profiles from people nearby.", "Swipe, superlike, or start a chat."],
      "footer": "FLICKER / DATING, AFTER DARK",
      "bg": "#F4EBDD",
      "ink": "#2A1A1A",
      "accent": "#C23B3B",
      "accent2": "#E2A08A",
      "badge": "REAL PROFILES",
      "badge_ink": "#FBF4E8",
      "sticker": "SWIPE →",
      "callout": "Tap the star to stand out.",
      "callout_side": "right",
      "overflow": {
        "photo": "people/hannah.png",
        "name": "Hannah, 26",
        "sub": "HEAVY METAL · TATTOOS",
        "side": "left",
        "rotate": -7,
        "photo_position": "50% 16%"
      },
      "tilt": -1.8,
      "frame": "pixel",
      "screen": "screens/discover.png"
    }
  ]
}
```

Render both stores:

```bash
# high-conversion poster set
python3 scripts/render_gallery.py poster-play.json --store play --frame pixel \
  --out out/play --overview --feature-graphic

python3 scripts/render_gallery.py poster-apple.json --store apple --frame iphone \
  --out out/apple --overview

# quieter editorial set for a real build
python3 scripts/render_gallery.py gallery.json --store play --out out/editorial-play \
  --overview --feature-graphic
```

- `layout: "poster"` selects `assets/templates/poster.html`: big headline, color field, device frame, badge, sticker, callout, and an optional `overflow` card that peeks out from behind the phone.
- `overflow` takes `photo`, `name`, `sub`, `side` (`left`/`right`), `rotate`, and `photo_position`. The card sits behind the device; its text is aligned to the visible side.
- A detail composition may intentionally reuse a screen. Set `"allow_reuse": true` on that image and use `--allow-count` when the set has fewer than five images.
- For a bold neon direction, set `"mood": "neon"` on the images and `typography.line2` to `"sans"`; the poster adds a grid and a neon device glow. The default line 2 is serif italic.
- `frame: "pixel"` draws a Pixel-style punch-hole frame; `frame: "iphone"` draws an iPhone 18-style Dynamic Island frame. Keep the frame fully visible.
- Start the phone above the footer and leave a visible gap; the poster template computes the height from the canvas and frame.
- `--allow-count` permits 2–8 screenshots instead of the house convention of 5.
- Apple defaults to 1320 × 2868 and exports 1206 × 2622.
- Play defaults to 1440 × 2560 and exports 1080 × 1920.
- `--feature-graphic` renders the Play 1024 × 500 asset from `feature_graphic` copy. The App Store has no feature graphic.
- `--overview` renders the 3200 × 1280 review sheet (never upload it).
- `--jpeg` switches exports to JPEG; `--only 01,02` renders a subset.

### Phase 6 — Validate and inspect

```bash
python3 scripts/check_assets.py --gallery out/apple/gallery.json --store apple --pretty
python3 scripts/check_assets.py --gallery out/play/gallery.json --store play --pretty
python3 scripts/check_assets.py --feature out/play/feature-graphic-1024x500.png --pretty
```

The validator checks count, order, copy length, duplicate screens, alpha, dimensions, Play's 320–3840 px and 2:1 rules, icon alpha/size, Android adaptive safe zone, feature graphic 1024 × 500, and contrast. Fix every error before delivering.

Then inspect the actual images:

- headline and body are not clipped
- image 01 communicates the product without the other four
- the five screens are visibly different and prove their own headline
- the device frame is the correct one (Pixel for Play, iPhone 18 for Apple), fully visible, including the bottom edge
- the phone is not stretched or cropped; the app UI is readable
- badges, stickers, and callouts are readable and explain the claim
- text is readable at thumbnail size and at 50%
- the background rhythm has contrast and does not repeat five times
- the feature graphic stands alone as a brand poster
- the icon survives the mask sheet and 16 px
- every generated person is a fictional adult, fully clothed, non-explicit, and not the supplied person
- no text, logos, or celebrity likeness inside a generated image

### Phase 7 — Deliver

```
out/
  icons/
    icon-ios-1024.png
    icon-play-512.png
    icon-adaptive-foreground-432.png
    icon-adaptive-background-432.png
    icon-monochrome-432.png
    icon-mark-1024.png
    icon-mask-preview.png
    icon-manifest.json
  mockups/
    play/discover-1080x2400.png ... me-1080x2400.png
    apple/discover-1320x2868.png ... me-1320x2868.png
  cast/
    *.png                       # fictional adults, inspected
  apple/
    01-....png ... 05-....png
    exports/*-1206x2622.png
    overview.png
    gallery.json
  play/
    01-....png ... 05-....png
    exports/*-1080x1920.png
    feature-graphic-1024x500.png
    overview.png
    gallery.json
  poster-play.json
  poster-apple.json
```

Report the paths, the validation result, and any `[待确认]` facts. State whether the set is real screenshots or a mockup, and which style pack was used. Do not claim a store will accept an asset; say it matches the current documented specs and was machine-checked.

## Optional: AI backdrops, fictional cast, and brand showcases

AI-generated images are optional. Use `scripts/generate_backdrop.py` for an abstract field, `scripts/generate_cast.py` for fictional adult portraits in a mockup, and `scripts/make_showcase.py` to composite the real SVG mark and typography deterministically over a backdrop. This keeps the logo sharp and editable while getting a high-end presentation background.

```bash
python3 scripts/generate_backdrop.py --config /path/to/ai_config.md \
  --style ink --out out/backdrop.png --count 1

python3 scripts/make_showcase.py out/backdrop.png logo.svg \
  --name "Harbor" --tagline "Make room to think." --out out/showcase.png
```

Never use these images inside the device as app UI. Never use a generated person as a real user, a real testimonial, or a substitute for the supplied person's identity. See `references/mockups-and-cast.md` for cast safety and `references/research-and-ai.md` for model fallback, licensing, and key handling.

## Reference map

| File | Use it for |
|---|---|
| `references/logo-system.md` | Logo principles, 8 pattern families, variant matrix, icon constraints, critique rubric |
| `references/gallery-system.md` | Five-image layout, copy system, narrative sequences, device treatment, feature graphic |
| `references/high-conversion-store-patterns.md` | Ten patterns from high-performing store sets; poster recipe and QA |
| `references/layer-compositing.md` | Preserve the original layout, replace only people, avatar/card masks, overflow cards |
| `references/screenshot-repair.md` | Fill placeholder silhouettes, avatars, empty cards, and missing photo regions |
| `references/mockups-and-cast.md` | Full mockup mode, fictional cast generation, safety checks, app-screen workflow |
| `references/dating-style-packs.md` | The 30 dating/social art-direction packs and the random/next picker |
| `references/store-specs.md` | Current App Store / Play sizes, alpha rules, validator rules, common failures |
| `references/research-and-ai.md` | iconLibrary / Lucide / Mobbin / logo-generator-skill usage, licensing, AI backdrop workflow |
| `references/demo.md` | A working example and the exact commands used to test this skill |

## Troubleshooting

**`No Chromium-based browser found`** — install Google Chrome, Chromium, or Microsoft Edge; or set `BROWSER_BIN=/path/to/browser`. The scripts do not download a browser.

**Text is clipped** — the template auto-shrinks to a floor, then leaves the copy overflowing. Shorten the headline/body. Run the validator; it reports long lines before rendering.

**The screenshot looks cropped** — the device frame uses the source aspect, so a very wide capture will make a wide frame. Re-capture at the phone's native portrait aspect, or compose the raw capture on a 9:16 canvas.

**The user says the app content did not change** — if the layout is approved, use layer compositing, not a full rebuild: keep the original screen, replace only the person/photo regions, and add an overflow card. See `references/layer-compositing.md`.

**The user says the layout changed too much** — you are in mockup mode when you should be in layer-compositing mode. Restore the original screenshot; replace only the full profile card, avatars, and photo regions; keep every other pixel of UI. Do not redesign the header, controls, copy, or nav.

**The overflow card covers the phone name or controls** — move it behind the device frame: about 80% visible, 20% behind. Align the card's text to the visible side and wrap the sub line inside the visible width. Do not use a front card that covers the primary UI.

**The card name/sub is cut off** — the visible portion is too narrow. Put the meta inside the visible area (`right: 20% + 16px` on a left card; `left: 20% + 16px` on a right card), reduce the name to 19u, and allow the sub to wrap.

**A screenshot has a placeholder silhouette or gray avatar** — use `scripts/repair_region.py` with the exact rect/circle, a new fictional adult, a radius, and a bottom fade. Fill only the image area; keep the name/label outside. See `references/screenshot-repair.md`.

**The repaired region has a seam or a cut face** — adjust `--radius`, `--centering`, and `--fade-bottom` / `--fade-color`. Use the sampled card color for the fade. If the face is cut, move centering toward the top (e.g. `0.5,0.18`).

**A generated portrait is inappropriate** — delete it immediately. Regenerate with a high neckline, fully buttoned clothing, head-and-shoulders framing, hands out of frame, and the negative prompt in `generate_cast.py`. Inspect every output; do not crop around a failure.

**The phone frame is square or clipped** — use `layout: "poster"` and `frame: "pixel"` / `"iphone"`. The frame needs its outer border radius, a visible gap above the footer, and a small tilt (≤2°). Check the bottom corners in the rendered image.

**A badge, sticker, or callout is invisible** — the text color must contrast with its own background. Set `badge_ink` explicitly; the poster template uses the field color for sticker/callout text. Do not put a dark accent badge on a dark field.

**The app mockup has a big empty area** — use a real conversation thread instead of a chat list, add a photo message, and add a photo grid to the Me screen. A feed can show five posts; a likes grid can show six cards. Do not fill space with fake metrics.

**The store set feels like five unrelated posters** — pick one style pack and keep the same type scale, frame, badge language, and field rhythm. Do not mix two packs.

**Play icon rejected** — confirm 512 × 512, PNG, alpha channel present, ≤ 1 MB. Do not flatten to RGB.

**iOS icon rejected** — confirm 1024 × 1024, RGB, no alpha, no rounded corners, no transparency.

**Feature graphic rejected** — confirm exactly 1024 × 500, no alpha, ≤ 15 MB. It is required and is not a sixth screenshot.

**AI model returns `service unavailable`** — run `--list-models`, choose an available image model, or let the script fall back. On the tested endpoint in October 2026, the `gpt-image-*` models returned `service unavailable` while `grok-imagine-image-quality` worked. Availability changes; never hardcode a key.

## Credits and licenses

- Logo methodology adapted from `op7418/logo-generator-skill` (MIT): six-variant workflow, simplicity/negative-space principles, showcase backgrounds. This skill replaces its AI showcase dependency with deterministic composition and adds store-safe icon/gallery specifications.
- Icon library research: iconLibrary (directory), Lucide (ISC). Mobbin is used as a paid reference library only; never copy its screens.
- The high-conversion patterns were distilled from reference store sets supplied by the user in October 2026. The sets are analyzed for structure; no reference imagery is redistributed in this skill.
- The 30 dating/social style packs, poster template, app-screen mockup template, and fictional-cast workflow are original to this skill.
- Generated cast images are fictional adults created from text prompts. They are never the supplied person, a real user, or a celebrity likeness. Inspect every output before use.
- Bundled fonts: Instrument Serif and Public Sans, SIL Open Font License. License files are in `assets/fonts/`.
- The renderer uses the locally installed browser; no browser binaries are redistributed.
