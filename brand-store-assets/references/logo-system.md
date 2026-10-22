# Logo and app-icon system

A logo is not a poster and an app icon is not a logo shrunk down. The icon is the
smallest, most constrained expression of the brand: one idea, one silhouette, no
text, no fine detail. Design the mark so it survives a 16 px favicon, a circular
Android mask, and a 1024 px store icon without redrawing.

## 1. Inputs that actually change the design

Before drawing, write one line for each:

- **Name** — what is the shortest recognizable form? Initials only if they are distinctive.
- **Promise** — what changes for the user? e.g. "less noise, more focus".
- **Category** — what visual language is already exhausted? Avoid the category cliché.
- **Three traits** — e.g. calm, precise, warm. These are the critique vocabulary.
- **Audience** — consumer, pro, developer, regulated industry. Sets the temperature.
- **References and competitors** — collect 8–12; note what to borrow structurally, never visually.
- **Existing brand equity** — keep the mark, palette, or type if the product already has recognition.

If the user cannot answer, choose a defensible direction and label the assumptions
`[待确认]`. Do not invent a brand story.

## 2. Eight non-negotiable principles

1. **One or two core elements.** A mark with 15 hexagons has no focal point. Aim for 2–6 shapes total.
2. **At least 40–50% negative space.** Empty space is part of the mark, not wasted canvas.
3. **Precise proportions.** On a `0 0 100 100` grid, primary line marks use 2.5–4 units; app icons that must survive 16 px use 6–8 units or solid shapes. Dots are 2–8 units radius. Keep at least 8–12 units between elements.
4. **Intentional asymmetry.** Perfect symmetry is static. Offset a dot, vary a bar length, or shift the optical center by 1–3 units.
5. **Restraint.** No gradients, shadows, bevels, or multiple colors unless the brand genuinely needs them. A one-color mark is the master; color is an application.
6. **One focal point.** The eye should land on one thing immediately.
7. **Structural stability.** Two thin lines feel fragile. Use dense repetition, solid mass, or a thicker stroke.
8. **Rounded negative-space cuts.** Cutouts should have rounded corners or circular ends. Sharp accidental cuts look unfinished.

### Optical corrections

- Center by **visual weight**, not by the bounding box. A triangle sits lower; a circle overshoots a square by ~1–2%.
- Align horizontal/vertical edges to the pixel grid at 16, 32, and 64 px.
- A ring at 16 px is usually a smudge. Either thicken it or replace it with a solid shape.
- Test the mark in one color first. If it needs color to be recognizable, the silhouette is weak.

## 3. Pattern families

Use these as starting points, not templates. Each family should produce a mark
that is meaningfully connected to the product.

### 3.1 Monogram / letterform

**Use when** the name has a distinctive initial or the brand is a personal/professional tool.

**Construction** — extract the structural DNA of the letter (stem, bowl, diagonal, crossbar) and rebuild it with geometric primitives. Never render a font and call it a logo. Keep the counter-space open.

```svg
<svg viewBox="0 0 100 100">
  <g fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round">
    <path d="M 30 24 V 76"/>
    <path d="M 70 24 V 76"/>
    <path d="M 30 52 Q 50 34 70 52"/>
  </g>
</svg>
```

**Pitfall** — a monogram that only works because the full name is next to it. It must read as a symbol on its own.

### 3.2 Open ring / aperture

**Use when** the product is about focus, continuity, protection, a cycle, or a harbor/container.

**Construction** — one 270–300° arc, round caps, plus one dot or a flat edge to break the loading-spinner symmetry. Keep the opening at 50–70°.

```svg
<svg viewBox="0 0 100 100">
  <path d="M 35 76 A 30 30 0 1 1 65 76" fill="none"
        stroke="currentColor" stroke-width="7" stroke-linecap="round"/>
  <circle cx="50" cy="86" r="4.5" fill="currentColor"/>
</svg>
```

**Pitfall** — a generic spinner. Give the gap a purpose: a bead, a notch, a flat base.

### 3.3 Negative-space cut

**Use when** the idea is subtraction, insight, privacy, or "less".

**Construction** — start with a solid, simple field (circle, rounded square, arch) and cut one rounded shape out of it. The cut must be at least 8–12 units wide so it survives small sizes. Use an SVG mask so the cut is transparent on any background.

```svg
<svg viewBox="0 0 100 100">
  <defs>
    <mask id="cut">
      <rect width="100" height="100" fill="white"/>
      <circle cx="58" cy="42" r="13" fill="black"/>
    </mask>
  </defs>
  <circle cx="50" cy="50" r="32" fill="currentColor" mask="url(#cut)"/>
</svg>
```

**Pitfall** — a thin slice that disappears at 32 px, or a cutout that only works on one background color. Use transparency, not a background-colored shape.

### 3.4 Dot matrix / particle

**Use when** the product is data, community, modularity, or emergence.

**Construction** — use a 3×3, 4×4, or concentric layout. Remove dots to form a letter or a recognizable silhouette. Keep dot radius 3–5 units on the 100 grid and gaps at least 8 units.

```svg
<svg viewBox="0 0 100 100">
  <g fill="currentColor">
    <circle cx="30" cy="30" r="4"/><circle cx="50" cy="30" r="4"/><circle cx="70" cy="30" r="4"/>
    <circle cx="30" cy="50" r="4"/><circle cx="70" cy="50" r="4"/>
    <circle cx="30" cy="70" r="4"/><circle cx="50" cy="70" r="4"/><circle cx="70" cy="70" r="4"/>
  </g>
</svg>
```

**Pitfall** — a full grid with no focal point. Remove at least 30% of the dots.

### 3.5 Stacked bars / rhythm

**Use when** the product is about progress, sound, planning, or structure.

**Construction** — 3–5 rounded bars on a shared baseline. Vary length and spacing rhythmically, not randomly. Keep bar thickness 6–10 units and corner radius 2–4 units.

```svg
<svg viewBox="0 0 100 100">
  <g fill="currentColor">
    <rect x="24" y="58" width="10" height="18" rx="4"/>
    <rect x="38" y="42" width="10" height="34" rx="4"/>
    <rect x="52" y="26" width="10" height="50" rx="4"/>
    <rect x="66" y="48" width="10" height="28" rx="4"/>
  </g>
</svg>
```

**Pitfall** — a generic equalizer. Break the rhythm or frame it with a circle/square.

### 3.6 Node network

**Use when** the product is connection, AI orchestration, collaboration, or infrastructure.

**Construction** — 3–5 nodes, 2–4 curved edges, one dominant node. Node radii 4–7 units; edges 2–3 units. Use opacity for secondary edges, not extra colors.

```svg
<svg viewBox="0 0 100 100">
  <g fill="none" stroke="currentColor" stroke-width="2.5">
    <path d="M 30 70 Q 50 70 50 50"/>
    <path d="M 50 50 Q 50 30 70 30"/>
  </g>
  <circle cx="30" cy="70" r="5" fill="currentColor"/>
  <circle cx="50" cy="50" r="7" fill="currentColor"/>
  <circle cx="70" cy="30" r="4.5" fill="currentColor"/>
</svg>
```

**Pitfall** — five equal nodes with six edges: a hairball at 32 px.

### 3.7 Wave / signal

**Use when** the product is audio, communication, calm, or flow.

**Construction** — one dominant wave, one supporting wave at 40–60% opacity, and a single accent dot. Keep amplitude within 20 units.

```svg
<svg viewBox="0 0 100 100">
  <g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
    <path d="M 18 50 Q 34 28 50 50 T 82 50"/>
    <path d="M 18 62 Q 34 44 50 62 T 82 62" opacity=".45"/>
  </g>
  <circle cx="18" cy="50" r="3.5" fill="currentColor"/>
</svg>
```

**Pitfall** — a decorative sine wave with no product meaning. Pair it with a hard geometric edge or a single strong dot.

### 3.8 Fold / plane

**Use when** the product is about transformation, layers, space, or craft.

**Construction** — two or three flat planes with one fold. Use flat tones from one hue; avoid complex gradients. Keep the fold angle consistent.

```svg
<svg viewBox="0 0 100 100">
  <path d="M 50 18 L 80 46 L 50 82 L 20 46 Z" fill="currentColor" opacity=".92"/>
  <path d="M 50 18 L 50 82 L 20 46 Z" fill="currentColor" opacity=".55"/>
</svg>
```

**Pitfall** — too many planes and highlights; it becomes an illustration, not a mark.

## 4. Six-variant matrix

Generate six genuinely different directions:

| Variant | Family | What changes |
|---|---|---|
| 1 | Monogram, solid | Bold weight, 2–3 shapes |
| 2 | Monogram, line | Thin/open counter-space, 3–4 units |
| 3 | Open ring / aperture | Circular rhythm, one break |
| 4 | Negative-space cut | Subtraction, one field |
| 5 | Dot matrix or stacked bars | Repetition, rhythm |
| 6 | Wildcard: node, wave, or fold | Structural metaphor |

Vary density (sparse vs dense), symmetry (centered vs offset), weight (solid vs
line), and complexity (2–3 vs 8–12 elements). If two variants share the same
silhouette, replace one.

For each variant write:

- the one-sentence idea
- the product trait it encodes
- the construction rule that makes it distinctive
- the failure mode at 16 px

## 5. Critique rubric

Score each surviving variant 1–5:

| Criterion | Question |
|---|---|
| Distinctiveness | Is it recognizable without the wordmark? |
| Simplicity | Can you describe it in one sentence? |
| Scalability | Does it work at 16, 32, 64, 128 px? |
| Meaning | Does the form connect to the product, not just the category? |
| Color independence | Does it work in one color? |
| Mask safety | Does it survive a circle, squircle, and rounded square? |
| Originality | Is it distinguishable from the reference set? |

Eliminate any variant with a 1 or 2. Refine the top two rather than generating ten
more directions.

## 6. Color

Use a three-role palette:

- **Field** — the large background: paper, ink, deep green, wine, saturated flat.
- **Ink** — the mark and text: off-black or off-white, not pure `#000`/`#FFF`.
- **Accent** — one warm or cool note, used sparingly (rule, second headline line, dot).

Rules:

- 60/30/10: field dominates, ink carries the mark, accent is a detail.
- Aim for ink/field contrast ≥ 7:1; never below 4.5:1 for body text.
- Accent on field must be ≥ 3:1 for large type; ≥ 4.5:1 for small text.
- A one-color mark is the master. Test it on paper, dark, and a saturated field.
- Avoid relying on a gradient to make the mark legible.

Palette archetypes:

| Feel | Field | Ink | Accent |
|---|---|---|---|
| Editorial / calm | `#F7F4ED` | `#1E2A2A` | `#B5653A` |
| Deep / premium | `#1E2A2A` | `#F3EFE4` | `#D9A441` |
| Cool / technical | `#E8EDF2` | `#182027` | `#2F6F6B` |
| Saturated / confident | `#243B53` | `#F7F4ED` | `#F2C14E` |
| Soft / wellness | `#E7EFE6` | `#24352E` | `#7C9A72` |

## 7. Typography and wordmark

- The app icon is **symbol only**. No text, no letterspaced wordmark, no tagline.
- Keep a separate lockup (`mark + wordmark`) for the store gallery header, website, and documents.
- Use a licensed typeface for the wordmark. Do not trace a font and call it custom lettering.
- Pair one high-contrast display serif (headline) with one humanist sans (body). Use the app's existing type if it has one.
- The wordmark can be title case or uppercase; keep tracking consistent across the five gallery images.

## 8. App icon constraints

### iOS / App Store

- **1024 × 1024**, PNG, **no alpha**, no transparency.
- Do not bake in rounded corners; Apple applies the mask.
- Keep critical content inside the central ~824 × 824 safe area (80.5%).
- Mark occupies roughly 56–68% of the canvas; too small looks timid, too large gets clipped.
- No text, no screenshots, no UI, no drop shadows, no photographic detail.

### Google Play

- **512 × 512**, 32-bit PNG **with alpha**, ≤ 1 MB.
- Do not bake in rounded corners; Play applies a mask.
- Full-bleed field is safer than a floating transparent mark.
- The same 56–68% mark ratio works; check it on light and dark store backgrounds.

### Android adaptive icon

- Canvas 108 × 108 dp; visible area 72 × 72 dp; safe zone 66 × 66 dp (61.1%).
- Export foreground and background at **432 × 432 px** (4×).
- Foreground: transparent, mark inside the central 264 × 264 px safe zone.
- Background: opaque field, no alpha.
- Monochrome layer: transparent, one-color mark, used for themed icons.

### Mask and small-size tests

Test the same icon through:

- iOS squircle
- circle
- rounded square
- full square
- 128 / 64 / 32 / 16 px
- light and dark fields

If the mark disappears at 32 px, thicken the stroke, remove detail, or switch to a
solid silhouette. Do not add a background plate to compensate; the mask already
provides the field.

### Optical centering

- A circle looks smaller than a square of the same bounding box; overshoot it by 1–2%.
- A triangle's visual center is lower than its geometric center; raise it.
- A dot at the bottom of a ring adds visual weight; shift the ring up 1–2 units.
- Align the mark to the pixel grid at 16/32 px; a half-pixel offset makes it fuzzy.

## 9. Export naming

```text
icon-ios-1024.png                  # RGB, no alpha
icon-play-512.png                  # RGBA, <= 1 MB
icon-mark-1024.png                 # transparent master for showcases
icon-adaptive-foreground-432.png   # transparent, safe zone
icon-adaptive-background-432.png   # opaque field
icon-monochrome-432.png            # transparent, one color
icon-mask-preview.png              # QA artifact, never upload
icon-manifest.json                 # machine-readable output list
```

Optional: `android-48/72/96/144/192.png`, `favicon-16/32/48.png`,
`apple-touch-icon-180.png`, `pwa-192/512.png` via `--preset all`.

## 10. Showcase (optional)

A logo showcase is a presentation artifact, not a store asset. If using an
AI-generated backdrop:

- generate an abstract field with no text, logo, device, or UI
- composite the real SVG mark and type deterministically over it
- keep the mark sharp and undistorted
- label the output `Showcase · not a store asset`
- check contrast on the actual backdrop, not the prompt

See `references/research-and-ai.md` for prompts and the `make_showcase.py` command.

## 11. Final QA

- [ ] The mark is recognizable in one color at 32 px.
- [ ] It has 1–2 core elements and at least 40% negative space.
- [ ] No text, no UI, no screenshot, no photographic detail.
- [ ] Strokes are ≥2.5 units, or ≥6 units for a small-size icon.
- [ ] Negative-space cuts are rounded and at least 8–12 units wide.
- [ ] It survives circle, squircle, rounded square, and full-square masks.
- [ ] iOS icon is 1024 × 1024, RGB, no alpha, no rounded corners.
- [ ] Play icon is 512 × 512, RGBA, ≤1 MB, no baked corners.
- [ ] Adaptive foreground content stays inside the central 66/108 safe zone.
- [ ] Ink/field contrast is ≥7:1; accent/field is ≥3:1 for large type.
- [ ] The icon looks intentional next to the five gallery images.
- [ ] The showcase is labeled as a showcase, not a store upload.
