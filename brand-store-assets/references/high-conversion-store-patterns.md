# High-conversion store image patterns

Analysis of eight reference sets supplied in October 2026. The goal is not to copy
their surface style, but to extract the structural moves that make a store set
feel like a campaign instead of a screenshot with a caption.

## The core difference

A weak set asks: “How do I put this screenshot on a nice background?”

A strong set asks: “What is the one thing this image must make the viewer feel or
understand, and what visual proof proves it?”

The best references change the **app content** from panel to panel. The phone is a
prop in a composed story, not a fixed object dropped onto five backgrounds.

When the user only wants the people replaced, do **not** rebuild the app UI. Use
layer compositing: keep the original screenshot as the base, replace the person
regions, and add the marketing layers around it. See `layer-compositing.md`.

## Ten patterns worth adopting

### 1. One panel, one idea

Each panel has a single short headline (2–5 words) and one visual proof. The
headline is not a feature list. The phone shows the exact state that proves the
headline.

- Strong: `no more inventory chaos` + a Locations screen.
- Strong: `find any items in seconds` + a search result screen.
- Weak: a generic home screen with a paragraph of body copy.

### 2. The headline is the hero

Display type occupies 30–50% of the panel. It is short, high-contrast, and
readable at thumbnail size. Some sets use a heavy sans, some use a high-contrast
serif, some use outlined type. The common rule is **size and contrast**, not a
specific font.

- 2–4 lines maximum.
- Sentence case or all caps, but consistent across the set.
- One word or line can switch color/italic for emphasis.
- Supporting copy is one short line, not a paragraph.

### 3. Color-blocked panels

Each panel gets a full-bleed field from a tightly controlled palette. The field
changes, the system stays fixed. This creates rhythm and makes the carousel feel
designed rather than assembled.

- Alternate dark / paper / accent / dark.
- Keep the same ink and accent roles across the set.
- Use a large shape, circle, or card behind the phone for depth, not a busy photo.

### 4. The phone is a prop, not a passport photo

The strongest sets tilt, overlap, crop, or float the phone. They add UI cards,
chat bubbles, callouts, and small stickers around it. The frame stays visible and
recognizable.

- Tilt 2–5°; more looks unstable.
- Let a card or callout overlap the frame edge.
- Keep the screen readable; do not bury the primary control.
- For an overflow card, place it **behind** the phone, about 80% visible and 20%
  hidden, with its text aligned to the visible side. A card that covers the app's
  name or primary control reads as a mistake, not a layout.
- For device-specific sets, use the correct frame: Pixel for Google Play, iPhone
  for the App Store.

### 5. Custom app content proves the claim

The reference sets often show a screen that does not exist as a raw capture: a
search result with the searched item highlighted, a profile card with the exact
interests, a live room with chat overlays, a grade card with the score.

For a real submitted build, capture the exact screen and add callouts around it.
For a concept/mockup set, rebuild the screen deterministically with the app's own
design system and label it as a mockup internally. Never pretend a mockup is a
real build capture in review notes or legal copy.

### 6. Add graphic props with a job

Props should explain, not decorate:

- a starburst badge for a qualitative claim (`REAL PROFILES`, `MADE FOR NIGHT OWLS`)
- a count chip for a true metric (`200k+`, `4.9 ★`) — only if true
- a callout pill pointing at a UI element (`Tap to superlike`)
- a chat bubble or card that shows the outcome (`“What size is this?”`)
- a hand-drawn arrow or circle to direct the eye

Avoid props that imply a rating, award, or user count that the product cannot
substantiate.

### 7. Sequence: hook → feature → proof → feature → brand

A five-panel set usually follows:

1. **Hook** — the core promise and the primary screen.
2. **Feature** — a distinct pillar with a clear visual.
3. **Proof** — a result, social proof, or comparison.
4. **Differentiator** — the thing competitors cannot claim.
5. **Brand / personalization** — the closing emotional beat.

The first panel must work alone. The others can assume the viewer has seen it.

### 8. Social proof, handled honestly

Ratings, user counts, and awards are powerful, but they are also the easiest way
to make a listing non-compliant or misleading.

- Use a rating/count only when it is live and verifiable.
- For a pre-launch or concept set, use qualitative badges instead of fake numbers.
- Never use a celebrity photo or name without permission.
- Never imply a user is real when it is a generated fictional persona.

### 9. Before/after and transformation

Two of the references use a literal before/after. It works when the product has a
visible transformation: raw screenshots → designed screens, messy inventory →
organized inventory, blurry fish photo → identified species.

For a dating product, a before/after can be “endless swiping” → “a real
conversation”, but only if the product actually delivers that. Do not invent a
transformation.

### 10. Consistency beats variety

The best sets vary color and composition but keep:

- the same type scale and headline placement
- the same corner radii and device frame
- the same badge/sticker language
- the same palette roles
- the same level of visual density

A viewer should recognize the second image as part of the same campaign before
reading the copy.

## What the eight references teach, specifically

| Reference | Main technique | What to borrow |
|---|---|---|
| Color analysis (purple) | Circular profile photo, checklist, grade card, color chips, `#1` badge, doodles, tilted phone | Proof objects beside the UI; one strong badge; a profile photo cropped into a circle |
| Inventory (olive/green) | Illustrated character, speech bubbles, star rating, phone UI, item detail cards | A human/character reaction; speech bubbles; a rating only if true |
| Live shopping (blue/red) | Floating product cutouts, live video, chat overlay, big numbers, color blocks | Floating UI cards; live-chat callouts; big numbers only when true |
| Skincare (pink) | Illustrated character, product render, `500K` badge, face scan, condition tags | A hero visual plus a detail card; condition/benefit tags |
| Trading before/after | Raw vs designed panels, 3D objects, colorful fields | Before/after only when the product visibly transforms; 3D props as focal points |
| Fishing before/after | Hero photo, `200k+` proof, fish ID card, map | One hero photo; one result card; a map/ID detail |
| Language learning | Flags, character art, chat bubbles, 60-day challenge, progress | A time-bound promise; progress UI; conversational bubbles |
| Multi-app collage | Consistent panel colors, big headlines, awards, feature callouts | A disciplined palette and type system; one feature per panel |

## What not to copy

- Fake ratings, awards, download counts, or “#1” claims.
- Celebrity photos, names, or likeness without permission.
- Trademarked logos or another app's trade dress.
- Dense collages that become unreadable at thumbnail size.
- Raw screenshots repeated with different captions.
- AI-generated people presented as real users, or real people's photos reused
  without consent.
- A device frame that is wrong for the store (iPhone frame on Play, Pixel frame on
  the App Store) when the set is device-specific.

## The poster recipe used by this skill

For a high-conversion set, use the `poster` layout instead of the quiet editorial
layout:

1. **Field** — one full-bleed color per panel; alternate dark/paper/accent.
2. **Headline** — 2–4 lines, 0.07–0.09 of canvas height, heavy sans or a
   high-contrast serif; one accent line/word.
3. **Support** — one line at 0.014–0.018 of canvas height.
4. **Phone** — Pixel or iPhone frame, 2–5° tilt, large enough to read; keep the
   frame visible.
5. **Proof prop** — one badge, callout, card, or chat bubble that explains the
   headline.
6. **Brand** — spark + wordmark at the top or bottom; small footer line.
7. **Content** — a custom mockup or a real screen that proves this panel's idea;
   never reuse the same screen with a new caption.

## QA checklist for a high-conversion set

- [ ] Each panel has one idea and one visual proof.
- [ ] The headline is readable at thumbnail size (test at 25%).
- [ ] The first panel works without the rest.
- [ ] The five screens are different; no repeated screen with a new caption.
- [ ] The phone frame is correct for the store and fully visible.
- [ ] The app layout is unchanged outside the replaced people; no full UI rebuild.
- [ ] The overflow card peeks from behind the phone and its text is fully visible.
- [ ] Props explain something; no decorative clutter.
- [ ] No fake ratings, awards, counts, or celebrity likeness.
- [ ] Generated people are fictional adults, fully clothed, and not the supplied
      source person.
- [ ] The palette and type system are consistent across all panels.
- [ ] The app content matches the headline, not just the app's home screen.
