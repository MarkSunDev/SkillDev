# Dating / social style packs

The skill ships **20 art-direction packs** for dating and social store images:
`assets/style-packs/dating.json`. They are prompts plus palettes, not finished
layouts. The poster template turns a pack into a visual system; the app mockup
keeps the product's own UI palette.

## Picker

```bash
# list all packs
python3 scripts/style_packs.py --list

# random pick (default when no action is given)
python3 scripts/style_packs.py --random

# next pack after the last one; use when the user is unhappy
python3 scripts/style_packs.py --next

# specific pack
python3 scripts/style_packs.py --get paper-hearts
```

The picker writes `.style-pack-state.json` in the current directory by default.
Pass `--state /path/to/state.json` to keep the rotation with a project. The JSON
output contains the palette, display language, props, background prompt, cast
prompt, and things to avoid.

**Random is a starting point, not a mandate.** Reject a pack that fights the app's
own palette and type. A dark, nocturnal app with coral accents should not get a
cream paper wrapper just because the random pick landed on Paper Hearts. Harmony
beats novelty: choose the pack whose field/ink/accent can coexist with the product,
or use the app's own palette as the primary direction. The Flicker delivery uses
**After Hours Amber** for this reason; the cream/red Paper Hearts attempt was
rejected.

## The 20 packs

| # | ID | Mood |
|---|---|---|
| 01 | `after-hours-amber` | Late-night city editorial: deep ink, amber streetlight, quiet intimacy |
| 02 | `peach-noir` | Film-noir shadows warmed by peach and coral |
| 03 | `soft-focus` | Warm paper and dusty rose; gentle, human, low-contrast |
| 04 | `city-pop` | 80s city-pop sunset: teal, coral, cream, chrome |
| 05 | `chrome-hearts` | Y2K chrome, black glass, one hot-pink accent |
| 06 | `lavender-haze` | Lavender dusk, lilac glow, soft and open |
| 07 | `matcha-milk` | Sage, oat and cream; calm, grounded, slow dating |
| 08 | `red-room` | Deep red room, warm skin tones, one hard light |
| 09 | `blue-hour` | Midnight blue and ice light; after-dusk stillness |
| 10 | `golden-hour` | Terracotta and gold; a long sunset, unhurried |
| 11 | `monochrome-edit` | Black, white and one coral accent; gallery-clean |
| 12 | `paper-hearts` | Cream paper, red ink, printed matter; a love letter |
| 13 | `neon-arcade` | Dark arcade, hot pink and cyan neon |
| 14 | `brutalist-match` | Concrete gray, acid yellow, black type |
| 15 | `glasshouse` | Frosted glass, mint and cream; clean and modern |
| 16 | `midnight-bloom` | Black night, magenta bloom, floral glow |
| 17 | `sunset-strip` | Coral sunset, yellow light, palm shadows |
| 18 | `quiet-luxury` | Taupe, cream and burgundy; old-money restraint |
| 19 | `electric-violet` | Violet nightlife, acid-lime accent |
| 20 | `analog-romance` | Muted red, cream, film grain; a photo album |

## How a pack is applied

### Palette

Each pack has five roles:

- `field` — the main poster background
- `ink` — headline/body text on the field
- `accent` — italic headline line, badge, rule
- `accent2` — secondary glow, callout, or detail
- `paper` — the light alternate field

Use a rhythm rather than one field five times:

1. `field`
2. `accent` (or a deep accent)
3. `paper`
4. `accent2` or a warm neutral
5. `field`

Keep ink/field contrast ≥4.5:1; 7:1 is safer for thumbnails. If the accent is
dark, use a light badge text (`badge_ink`); if the field is light, the poster
template automatically uses the field color for sticker/callout text.

### Display and props

Pack fields:

- `display` — headline treatment and type contrast
- `props` — badge, sticker, callout, doodle language
- `avoid` — clichés to skip

The poster template supports:

```json
"badge": "REAL PROFILES",
"badge_ink": "#FBF4E8",
"sticker": "SWIPE →",
"callout": "Tap the star to stand out.",
"callout_side": "left"
```

For a bold neon set, also set the second headline line to sans and the poster mood
to neon:

```json
"typography": { "headline": "\"Public Sans\", sans-serif", "line2": "sans", "headline_weight": 850 },
"image": { "mood": "neon" }
```

`mood: "neon"` adds a subtle grid and a neon glow around the device frame. It works
best on the dark/neon packs (`neon-arcade`, `electric-violet`, `chrome-hearts`,
`midnight-bloom`).

Use one proof prop per panel. A badge that says `REAL PROFILES` is a qualitative
claim, not a fake metric. Do not invent `4.9 ★`, `500K users`, `#1`, or awards.

### Background prompt

The `background_prompt` is for an optional AI-generated decorative backdrop. It
explicitly excludes text, people, logos, and devices. Use it only behind a logo
showcase or as a texture; never inside the phone or as the app screenshot.

```bash
python3 scripts/generate_backdrop.py --config /path/to/ai_config.md \
  --prompt "<pack background_prompt>" --out out/backdrop.png
```

### Cast prompt

The `cast_prompt` adds lighting/wardrobe/setting to a fictional portrait. Combine
it with `generate_cast.py`, which enforces adult, fully clothed, head-and-shoulders,
no celebrity likeness, no text/logos. Inspect every output; delete failures.

### App UI

The app mockup keeps the product's own palette and type. The style pack changes
the **wrapper**, not the product. This prevents the store set from looking like a
different app on every panel.

## Harmony check

Before applying a pack, ask:

- Does the field color support the app's screenshots, or fight them?
- Does the accent belong in the app's world?
- Does the display type match the app's own voice (serif vs heavy sans)?
- Will the phone and app UI still feel like the same product?

If any answer is no, use the next pack or the app's own palette. A store set is
marketing for this product, not a style demo.

## Switching when the user is unhappy

1. Run `--next` (or `--random` again).
2. Rebuild the poster manifest with the new palette and props.
3. Keep the same app mockups and cast, unless the user also wants a new cast.
4. Re-render the five panels and the feature graphic.
5. Do not mix two packs in one set.

The current Flicker test used **Paper Hearts** (`paper-hearts`): cream paper, red
ink, serif headline, red italic accent. The phone content stayed Flicker's dark
coral UI. The next pack in the rotation is `neon-arcade`; if the user wants a
different direction, run `--next` from the Flicker folder.

## Safety and claims

- Style packs are aesthetic directions, not permission to use a real person,
  celebrity, or another brand's trade dress.
- Do not generate sexualized imagery; keep the cast modest and head-and-shoulders.
- Do not invent ratings, awards, download counts, or user counts.
- Generated people are fictional; do not present them as real users.
- Check the image provider's commercial-use terms before publishing.
