# Five-image gallery system

One editorial wrapper, two stores. The grid, type scale, brand lockup, device
treatment, and footer stay fixed across all five images; the screenshot,
background color, and message change. The set should feel like one campaign, not
five unrelated posters.

**Two layout modes.** The editorial layout described below is the quiet option. For
a high-conversion set, use `layout: "poster"` and read
`high-conversion-store-patterns.md`: big benefit headline, color-blocked panels,
Pixel / iPhone 18 frame, proof badge, sticker, callout, and a custom app screen per
panel. The poster mode still uses the same store canvas sizes and export rules.

**Layer compositing.** When the layout is approved and only people/content change,
keep the original screenshot and replace only the subject regions; do not rebuild
the UI. Add one overflow card behind the phone (80% visible, 20% hidden) with its
text on the visible side. See `layer-compositing.md`.

**Device frames.** Google Play sets use a Pixel-style frame with a punch-hole
camera and side buttons. App Store sets use an iPhone 18-style frame with a
Dynamic Island and a thin titanium edge. The frame is a marketing prop inside the
screenshot; it does not change the required canvas size. Keep the frame fully
visible, including the bottom edge.

## 1. The two stores at a glance

| | App Store | Google Play |
|---|---|---|
| Master canvas | **1320 × 2868** | **1440 × 2560** (9:16) |
| Required secondary export | **1206 × 2622** (medium display) | **1080 × 1920** |
| Other accepted sizes | 1260 × 2736, 1290 × 2796; iPad 2064 × 2752 or 2048 × 2732 | 320–3840 px per side, ratio ≤2:1 |
| Count | 3–10 per device size; **5** is this system's convention | 2–8 per device type; **5** is this system's convention |
| Format | PNG or JPEG, **no alpha** | JPEG or 24-bit PNG, **no alpha** |
| App icon | 1024 × 1024, RGB, no alpha | 512 × 512, 32-bit PNG with alpha, ≤1 MB |
| Extra required asset | — | **Feature graphic 1024 × 500** |
| Featured placements | Search, product page, editorial | Search, charts, home, ads; feature graphic used where screenshots are hidden |

Re-check the live specs in App Store Connect and Play Console before submitting.
The numbers above are current as of October 2026.

## 2. Shared layout

Use one layout component for all five. The proportions below are the reference
implementation in `assets/templates/gallery.html`.

| Element | Placement |
|---|---|
| Brand lockup | top left; mark + uppercase wordmark, one line |
| Divider | thin rule below the brand row, with a short accent segment |
| Eyebrow | uppercase, wide tracking, directly below the divider |
| Headline | large serif, two lines; line 1 roman, line 2 italic accent |
| Supporting copy | two lines of humanist sans |
| Accent rule + slide number | short accent bar left; `01 / 05` right |
| Device | one upright portrait frame with a real screenshot, centered |
| Footer | one small uppercase brand line near the bottom edge |

Approximate **Apple 1320 × 2868** positions:

- side margin: 82 px
- brand row: y 82–154
- divider: y 196
- eyebrow: y 258
- headline: y 328
- body: y 617
- accent rule + number: y 781
- device top: y 878
- footer: y 2779

Approximate **Play 1440 × 2560** positions:

- side margin: 90 px
- brand row: y 90–168
- divider: y 200
- eyebrow: y 261
- headline: y 328
- body: y 620
- accent rule + number: y 783
- device top: y 845
- footer: y 2478

The template computes the device height from the real screenshot's aspect ratio
and the space above the footer. A full portrait phone plus a bottom footer cannot
both occupy 70% of a 9:16 canvas; the renderer sizes the device to fit (typically
~64% of the width on Apple and ~51–54% on Play). Do not force the device to a
fixed percentage if it causes clipping or a footer over the screen.

## 3. Typography

- Display: `Instrument Serif` (regular + italic) or an equivalent high-contrast editorial serif.
- Body: the app's sans, default `Public Sans`; humanist, restrained.
- Eyebrow: 2–5 words, uppercase, 0.22–0.24em tracking.
- Headline: 1–4 words per line, 0.96–0.98 line-height, tight tracking.
- Body: 5–9 words per line, 1.35–1.4 line-height.
- Footer: 4–8 words, uppercase, 0.18–0.2em tracking.
- Keep each headline to two lines and each body block to two lines. Shorten the copy before shrinking the type.

For Chinese or mixed CJK copy, override the font stack:

```json
"typography": {
  "headline": "\"Instrument Serif\", \"Songti SC\", \"Noto Serif SC\", serif",
  "body": "\"Public Sans\", \"PingFang SC\", \"Noto Sans SC\", sans-serif"
}
```

CJK headlines should be 10–16 characters per line; body 16–24 characters per
line. Do not translate the layout independently from the copy.

## 4. Copy system

Each image has five text slots:

1. **Eyebrow** — names the feature or context. `DEEP FOCUS`, `YOUR DAY`, `EVENING REVIEW`.
2. **Headline line 1** — the tension or benefit, roman. `Focus that`
3. **Headline line 2** — the turn or payoff, italic accent. `protects your time.`
4. **Body** — two concrete lines explaining actual behavior. `Start a session and let the rest wait. / A gentle timer, not a pressure clock.`
5. **Footer** — a four-to-eight-word brand line. `Deep work, without the drama.`

Formulas that work:

- **Tension → payoff**: `Less noise. / More focus.`
- **Category → specific**: `Your day, / in clear view.`
- **Problem → mechanism**: `Focus that / protects your time.`
- **Ritual → outcome**: `A nightly / clean slate.`
- **Product → ownership**: `Made to / feel like yours.`

Rules:

- Image 01 carries the core promise and the primary screen. It must work without the other four.
- Images 02–05 each own one distinct pillar. Do not repeat a screen, tab, or feature.
- The eyebrow names the area. The headline sells the benefit. The body explains the behavior. The footer closes the set.
- Do not turn the headline into a feature list or paste the store description.
- No emoji, star ratings, awards, `#1`, `Editor's Choice`, prices, or `Download now`.
- Keep claims true in the submitted build. No invented metrics, users, or AI capabilities.

Length guardrails (the validator warns/errors):

| Slot | Latin warn | Latin error | CJK warn | CJK error |
|---|---|---|---|---|
| Headline line | 26 chars | 34 chars | 15 chars | 20 chars |
| Body line | 42 chars | 58 chars | 24 chars | 36 chars |
| Eyebrow | 5 words | 7 words | — | — |
| Footer | 8 words | — | — | — |

## 5. Five-image narratives by category

Pick one row and replace the pillars with the actual tabs and differentiators.

| Category | 01 Hero | 02 | 03 | 04 | 05 |
|---|---|---|---|---|---|
| Social / chat | Chats + core promise | People / discovery | Feed / content | AI or utility | Profile / trust |
| AI utility | Core action | Input / context | Output / result | History / memory | Privacy / control |
| Productivity | Today / plan | Focus | Capture | Review | Personalization |
| Notes / knowledge | Editor | Organization | Search | Sync / sharing | Templates |
| Commerce | Discover | Product detail | Checkout / trust | Orders / tracking | Sell / creator |
| Health / fitness | Today | Activity | Insight | Program | Community / privacy |
| Finance | Overview | Send / pay | Cards / budget | Insights | Security |
| Education | Learn | Practice | Progress | Library | Community |
| Travel | Discover | Plan | Book | Trip | Account |
| Games | Hero gameplay | Progression | Social | Events | Customization |

Games often use key art rather than UI screenshots; if the build is a game, use
real captured gameplay frames and keep the copy short. Do not invent gameplay.

## 6. Palette rhythm

Use a deliberate sequence, not five identical backgrounds. The reference rhythm:

1. dark field
2. paper
3. accent-tinted field
4. paper
5. dark field

or:

1. paper
2. dark
3. paper
4. accent field
5. dark

Keep ink/field contrast ≥ 7:1 for body copy. Accent is for the second headline
line, the divider segment, the rule, and small details; do not flood the canvas
with accent unless the accent field is the point of that image.

## 7. Device and screenshot treatment

- Use a real screenshot from the submitted build. Do not redraw, mock, or AI-generate the UI.
- Place it inside an upright black rounded frame with a subtle shadow. No perspective tilt, floating collage, or 3D rotation.
- Preserve the status bar, navigation, keyboard, and real content where they help the story. Do not crop the primary control.
- Use representative, non-sensitive demo content. Label seeded data in the PRD; never present simulated users or metrics as real.
- Do not reuse the same screenshot in two images.
- Use `frame: "card"` for a borderless rounded screenshot if a phone frame feels heavy; keep the same grid.
- Do not draw a second notch/island if the screenshot already contains one. Set `"notch": true` only when the capture has no status bar and you want the frame to supply it.

### Capture checklist

- one locale, one appearance (light or dark), one status-bar time
- full battery and signal; no charging bolt
- no debug banner, internal ID, test watermark, or "DEMO" label
- representative data; no real names, emails, phone numbers, or faces without permission
- distinct screens; five images should show five different states
- native resolution, no upscaling; keep the status bar and bottom navigation
- for Play, fit a raw 20:9 capture inside the device frame; never upload a raw capture that exceeds 2:1

## 8. App Store specifics

- Produce five portrait RGB PNGs in upload order `01`–`05`.
- Master **1320 × 2868**; export **1206 × 2622** for the required medium-display tier.
- App Store Connect also accepts **1260 × 2736** and **1290 × 2796** for the large-display tier.
- iPad 13-inch: **2064 × 2752** or **2048 × 2732** when the app supports iPad.
- App Store Connect accepts 3–10 screenshots per device size; five is this system's convention.
- No alpha channel or transparency. Flatten to RGB.
- The app icon is **1024 × 1024**, RGB, no alpha, no rounded corners.
- Keep the overview sheet as a review artifact; never upload it as a sixth image.

## 9. Google Play specifics

- Produce five portrait RGB PNGs or JPEGs in upload order `01`–`05`.
- Master **1440 × 2560** (9:16); export **1080 × 1920**.
- Phone screenshots: 2–8 per device type, each side 320–3840 px, aspect ratio no wider than 2:1.
- 7-inch and 10-inch tablets accept up to 8 screenshots each; compose a tablet variant when the app supports tablets.
- Chromebook and Android XR have their own counts, ratios, and minimum resolutions. Check the device catalog in Play Console.
- Screenshots must be JPEG or 24-bit PNG with no alpha/transparency.
- The **feature graphic is required**: 1024 × 500, JPEG or 24-bit PNG, no alpha, ≤15 MB.
- The app icon is **512 × 512**, 32-bit PNG with alpha, ≤1 MB.

## 10. Feature graphic

The feature graphic is a brand poster, not a sixth screenshot. It appears where
the carousel is unavailable, so it must stand alone.

- Canvas 1024 × 500, no alpha.
- Safe margin 48–64 px; some placements crop the edges.
- Brand lockup at top left or center-left, one line.
- One headline of two lines maximum at 56–72 px; at most one supporting line at 22–32 px.
- Same palette and type as the five-image set; a solid field is stronger than a busy gradient.
- No device collage, screenshot grid, stretched screenshot, star rating, award, ranking, price, or download CTA.
- Check at 50% scale. If the headline is unreadable, shorten it and make it larger.
- The renderer uses `feature_graphic` copy in the manifest and writes `feature-graphic-1024x500.png`.

## 11. Overview sheet

The overview is a wide contact sheet for the PRD and design review:

- 3200 × 1280, paper background, app name/version title, store and canvas subtitle.
- Five thumbnails in upload order with `01`–`05` labels and eyebrow names.
- Same palette and type as the individual assets.
- Clearly a review artifact: never upload it as a screenshot.

## 12. Validation rules

`scripts/check_assets.py` checks:

- exactly five images (this system's convention)
- required fields and unique slugs/output filenames
- duplicate source screenshots
- two-line title and body, eyebrow/footer length, emoji
- hex colors and contrast ratios
- PNG/JPEG format, no alpha
- Apple accepted sizes or Play 320–3840 px / 2:1
- feature graphic 1024 × 500, no alpha, ≤15 MB
- icon dimensions, alpha rules, Play 1 MB limit, adaptive safe zone

Run it before delivering:

```bash
python3 scripts/check_assets.py --gallery out/apple/gallery.json --store apple --pretty
python3 scripts/check_assets.py --gallery out/play/gallery.json --store play --pretty
python3 scripts/check_assets.py --feature out/play/feature-graphic-1024x500.png --pretty
```

## 13. Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| Screenshot rejected for alpha | Exported PNG with transparency | Flatten to RGB; use `save_rgb` or export JPEG |
| Play says ratio too wide | Raw 20:9/19.5:9 capture uploaded directly | Compose on a 9:16 canvas inside a device frame |
| Text clipped at thumbnail | Headline too long; font shrunk to the floor | Shorten the copy; keep two lines |
| Five images feel repetitive | Same screen or same background five times | One distinct pillar and one background rhythm per image |
| Feature graphic rejected | Wrong size or alpha | Exactly 1024 × 500, RGB, no alpha |
| iOS icon looks rounded | Rounded corners baked into the artwork | Export a square 1024 master; let Apple mask it |
| Play icon rejected | Flattened RGB or over 1 MB | RGBA PNG, 512 × 512, optimize to ≤1 MB |
| Icon disappears at 16 px | Thin strokes or too much detail | Thicken to 6–8 units or use a solid silhouette |
| Device looks stretched | Source aspect differs from the frame | Fit the real capture inside a frame with its own aspect |
| Copy is unreadable on a busy backdrop | Low contrast or a texture behind text | Use a solid field or a stronger ink; keep body contrast ≥7:1 |

## 14. Final QA

- [ ] Five images, five distinct real screens, upload order `01`–`05`.
- [ ] Image 01 carries the core promise and the primary screen.
- [ ] One shared grid, type scale, brand lockup, and device treatment.
- [ ] Headlines and body fit their planned two lines without clipping.
- [ ] Body copy is readable at thumbnail size and at 50%.
- [ ] Backgrounds alternate with a deliberate rhythm and keep contrast.
- [ ] No unverifiable claims, ratings, awards, or download CTAs.
- [ ] Apple files are 1320 × 2868 (plus 1206 × 2622 exports), RGB, no alpha.
- [ ] Play files are 1440 × 2560 (plus 1080 × 1920 exports), RGB, no alpha, ≤2:1.
- [ ] Feature graphic is 1024 × 500, RGB, no alpha, ≤15 MB.
- [ ] Icon matches the store's alpha and size rules.
- [ ] Overview is clearly a review artifact, not an upload.
- [ ] The manifest, IDs, copy, and screenshots describe the same build.
