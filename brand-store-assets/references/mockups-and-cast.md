# Mockups and fictional cast

A real submitted build should use real screenshots. This document is for the case
where the user explicitly asks to **change the app content** for a concept,
pre-launch, or marketing set. In that case, rebuild the screen deterministically
from the app's design system and use a new fictional cast. Never reuse a supplied
person's photo, and never present a mockup as a real build capture.

## Choosing the source

| Situation | Source | Rules |
|---|---|---|
| Real listing for a submitted build | Real screenshots | No redrawing; no fabricated UI; preserve the actual build |
| User asks to change the app content | Deterministic mockup + fictional cast | Rebuild from the app's own tokens; label internally as mockup |
| Pre-launch concept | Mockup | No fake ratings, awards, or user counts |
| The person in a supplied screenshot must not appear | Generate a new fictional adult | Never use the supplied face as a reference |

When in doubt, ask which mode the user wants. Do not silently turn a real listing
into a mockup.

If the user only wants the people replaced and the existing layout is approved,
use **layer compositing** instead of a full mockup: base screenshot + subject
layers + original UI + overflow card. See `layer-compositing.md`. A full mockup is
for a new screen/feature or when there is no usable base.

## App mockup workflow

1. **Extract the design system** from the supplied screens:
   - background, card, line, ink, coral/peach accent, muted text
   - display serif, body sans, eyebrow tracking, header sizes
   - corner radii, pill tags, bottom nav, status bar, action buttons
2. **Build one template** (`assets/templates/app-screen.html`) with the screen
   types you need: discover, feed, likes, chat, me.
3. **Write a spec** (`mockups.json`) with:
   - `cast`: names, ages, locations, tags, portrait paths
   - `feed`, `likes`, `chats`, `thread`, `me`
   - `screen` entries to render
4. **Render at the device resolution**:
   - Pixel-class Play screen: **1080 × 2400** (20:9)
   - iPhone-class App Store screen: **1320 × 2868**
5. **Place the screens inside the correct frame** in the poster template:
   - Google Play: Pixel frame with punch-hole camera and side buttons
   - App Store: iPhone 18 frame with Dynamic Island and titanium edge
6. **Inspect every mockup** before using it. Check text fit, photos, nav state,
   and whether the screen actually proves the store headline.

```bash
python3 scripts/render_mockups.py mockups.json --out mockups/play --width 1080 --height 2400
python3 scripts/render_mockups.py mockups.json --out mockups/apple --width 1320 --height 2868
```

The mockup template uses the app's own palette; the poster wrapper uses the
selected style pack. This keeps the product consistent while the marketing wrapper
changes.

## Fictional cast workflow

Use `scripts/generate_cast.py`. It sends **text only** to the image model. Never
pass a supplied screenshot, a real person's photo, or a reference image of a real
face.

```bash
python3 scripts/generate_cast.py \
  --config /path/to/ai_config.md \
  --style portrait --size 1024x1536 \
  --prompt "Maya, a fictional 27-year-old woman with shoulder-length dark hair, wearing a fully buttoned black denim jacket over a high-neck cream turtleneck, head-and-shoulders portrait, city street at night, warm bokeh, natural skin, professional casting photo" \
  --out generated/cast/maya.png
```

The script prepends a safety prefix and appends a negative prompt:

- fictional adult
- head and shoulders
- modest, fully buttoned clothing with a high neckline
- no exposed chest, no cleavage, no open jacket, no bare shoulders, no midriff
- no tight clothing, no suggestive pose, no bedroom setting
- no swimwear, no lingerie, no nudity, no explicit content
- no children or minors
- no celebrity likeness, no real person
- no text, logos, brand marks, or watermarks

### Inspect every output

Models still fail. A real test on this project produced an open jacket with
exposed chest despite the instruction “fully clothed.” That image was deleted and
regenerated with:

- a high-neck turtleneck under the jacket
- “head and shoulders”
- “hands out of frame”
- “fully buttoned”
- a stronger negative prompt

Delete any image that fails the modesty or likeness check. Do not crop around it,
do not use it in a mockup, and do not keep it in the deliverable folder.

### Cast consistency

Use one cast across the five screens. The same person can appear in Discover,
Likes, Chat, and Me; this makes the app feel like one product rather than five
stock-photo collages. Keep names, ages, locations, and interests consistent.

### Portrait framing

- A head-and-shoulders portrait works in a tall profile card and a circular
  avatar. Use `object-position: center 26%`–`32%` so the face stays visible.
- A square avatar can crop a 2:3 portrait; the face should remain centered.
- Lifestyle images (coffee, record shop, city) should contain no people and no
  readable logos.
- Do not generate text, UI, or logos inside the portrait.

## Mockup content checklist

- [ ] The screen shows the exact feature the poster headline claims.
- [ ] The five screens are different: Discover, Feed, Likes, Chat, Me.
- [ ] The chat screen is a real conversation thread, not a list with empty space.
- [ ] Names, ages, locations, and tags are consistent across screens.
- [ ] Status bar time is consistent (use 9:41).
- [ ] The bottom nav highlights the correct tab.
- [ ] Profile photos are fully clothed, non-explicit, and not the supplied person.
- [ ] No real celebrity likeness, no real user data, no fake ratings.
- [ ] The mockup is labeled `mockup` in the project README or manifest.
- [ ] The store copy does not claim the mockup is a real user or a real build
      capture.

## Ethics and rights

- Generated people are fictional. Do not claim they are real users.
- Do not use a real person's photo or likeness, including the person in the
  supplied screenshots.
- Do not generate minors in a dating context.
- Do not generate sexualized imagery. Keep clothing modest and framing
  head-and-shoulders.
- Do not generate celebrities or public figures.
- Keep a record of model, prompt, and date for each generated asset.
- Check the image provider's commercial-use terms before publishing.
