# Google Play screenshot and feature graphic style system

Reference implementation: Between v1.1 / v1.2, Google Play five-image set.

The set is a quiet editorial system built around real app screens. It is not five unrelated marketing posters: the grid, type scale, brand lockup, device treatment, and footer stay fixed; the screenshot, background color, and message change. The feature graphic is a separate composition, not a sixth screenshot.

## Production sequence

1. Capture the five real app screens from the submitted build.
2. Build one reusable layout with layers: background, brand lockup, divider, eyebrow, headline, body, rule/slide number, device frame, screenshot, footer.
3. Fill the five copy blocks from the PRD gallery table.
4. Render all five images through the same layout component. Change only the text, background color, and screenshot.
5. Compose the feature graphic from the same brand system with one message.
6. Assemble the overview sheet from the five rendered images.
7. Validate the gallery manifest before exporting.

Use HTML/CSS, a design tool, or an image compositor. Do not let the model redraw or generate the app UI inside the phone.

## Canvas and delivery

- Produce five individual portrait RGB JPEGs or 24-bit PNGs, in upload order `01`–`05`, with no alpha channel or transparency.
- Use **1440 × 2560** (9:16) as the master canvas and export **1080 × 1920** for lighter files. Both are accepted.
- Phone screenshots: 2–8 per device type, each side between 320 and 3840 px, aspect ratio no wider than 2:1.
- A raw 20:9 or 19.5:9 phone capture exceeds 2:1. Fit the capture inside the device frame on a 9:16 canvas; never upload the raw capture.
- Five is this set's editorial convention. Google Play accepts 2–8 screenshots per device type.
- 7-inch and 10-inch tablet tiers accept up to 8 screenshots each. Compose a tablet variant when the app supports tablets; do not stretch the phone layout.
- Chromebook and Android XR have their own counts, ratios, and minimum resolutions. Re-check the device catalog in Play Console at submission time.
- Feature graphic: **1024 × 500**, RGB JPEG or 24-bit PNG with no alpha, at most 15 MB. It is required.
- Keep a separate overview sheet for the PRD/review. The reference overview is a wide sheet with the title `[App] / [Version] / Google Play five-image set`, five thumbnails in a row, and labels below. Do not upload the overview as one of the screenshots.
- Keep the screenshot source files, the five finished images, the feature graphic, the overview, the copy, and the gallery manifest together.

## Shared layout

Use these proportions as starting values; keep them consistent across all five images.

| Element | Placement |
|---|---|
| Brand lockup | top left, roughly 84–92 px from each edge; logo mark + wordmark on one line |
| Divider | thin horizontal rule below the brand row, with a small accent segment |
| Eyebrow | uppercase, wide tracking, directly below the divider |
| Headline | large serif display, two lines, first line roman, second line italic accent |
| Supporting copy | two lines of humanist sans below the headline |
| Accent rule + slide number | short accent-colored rule at left; slide number at right |
| Device | one large portrait device mockup with a real screenshot, centered in the lower two-thirds |
| Footer | one small centered line near the bottom edge |

Approximate 1440 × 2560 layout:

- side margin: 84–92 px
- brand row: y 90–168
- divider: y 212
- eyebrow: y 278
- headline block: y 356–620
- body block: y 664–756
- accent rule and slide number: y 848–868
- device top: y 908; device width: about 69–72% of canvas
- footer: y 2478–2510

These are proportions, not fixed pixels. When rendering 1080 × 1920 or another accepted size, scale every value by the canvas height so the grid stays identical.

The device may overlap the lower copy zone slightly, but never clip the headline or supporting copy. Keep the screenshot undistorted and the status bar readable.

## Typography

- Display headline: `Instrument Serif` or an equivalent high-contrast editorial serif.
- First headline line: roman, brand ink.
- Second headline line: italic, accent color.
- Body: the app's existing sans, such as `Public Sans`, at a restrained editorial weight.
- Eyebrow: uppercase sans, roughly 26–30 px, 4–6 px tracking.
- Headline: roughly 100–116 px with tight line-height (0.96–1.0).
- Body: roughly 38–42 px with 1.3–1.4 line-height.
- Footer: roughly 22–24 px.

Keep each headline to two lines and each body block to two lines. If the copy does not fit, shorten it; do not reduce the type until it becomes unreadable at thumbnail size. The values above are for the 1440 × 2560 master; scale them proportionally for other accepted sizes.

## Color

Derive the palette from the app's own brand system. The reference uses a paper base and one deep field color plus a citron or mint accent.

Between v1.2 palette:

- wine: `#3C2634`
- paper: `#F7F4ED`
- light green field: `#E3ECB8`
- citron: `#D7EA8E`
- rose accent: `#7D3F5E`

Between v1.1 palette:

- forest: `#193F38`
- paper: `#F7F4ED`
- mint: `#DDEBAE`
- teal accent: `#277668`

Use a rhythm rather than five identical backgrounds. The v1.2 set alternates dark, paper, citron, paper, dark. Keep body and headline contrast high in every combination.

## Device and screenshot treatment

- Use the actual app screenshot from the submitted build. Do not recreate, redraw, or AI-generate the UI.
- Place the screenshot inside a black rounded device frame with a subtle drop shadow. Keep the device upright; no perspective tilt or floating collage.
- Preserve the status bar, navigation, keyboard, and real content where they help the story. Do not crop out the primary control.
- Use representative, non-sensitive demo content. Label seeded demo data in the PRD; never present simulated users or metrics as real.
- Do not reuse the same screenshot in multiple images. Each image should show a different tab, feature, or state.
- If the app supports tablets, fit the same screenshot into a tablet frame rather than stretching the phone frame.

## Copy system

Each image has five text slots:

1. Eyebrow: feature or context, 2–5 words, uppercase.
2. Headline line 1: a short benefit or tension, roman.
3. Headline line 2: the turn or payoff, italic accent.
4. Supporting copy: two concrete sentences or two short lines.
5. Footer: a four-to-eight-word brand line.

The eyebrow names the area. The headline sells the benefit. The supporting copy explains the actual behavior. The footer closes the set. Do not turn the headline into a feature list or repeat the Full Description.

## Five-image narrative

Use one distinct product pillar per image. A useful sequence for a social/chat product:

1. Core promise + primary screen (for a chats-first product, Chats).
2. Discovery or people.
3. Content or feed.
4. Signature differentiator or AI/utility.
5. Personalization, account, or trust.

For another product, replace these with its actual primary tabs and differentiators. Image 01 must carry the core promise. The remaining four should make the product feel broader than one screen. Do not repeat a tab or feature just to fill the set.

Google Play shows the carousel in upload order, so treat image 01 as the hero. Do not assume reviewers will swipe: the first image must communicate the product without the other four.

## Feature graphic

The feature graphic is 1024 × 500 and is used in placements where the full screenshot carousel is unavailable. It should read as a brand poster, not a screenshot with a title.

Layout:

- Keep a safe margin of at least 48–64 px; some placements crop the edges.
- Put the brand lockup at top left or center-left, one line.
- Use one headline of 2 lines maximum at 56–72 px. Add at most one supporting line at 26–32 px.
- Keep all critical text and the logo inside the central safe area.
- Use the same palette as the screenshot set. A solid field color is stronger than a gradient at this size.

Rules:

- Use one message and the brand. It must stand alone.
- Do not build a screenshot collage, device grid, or stretch one screenshot.
- Do not include star ratings, awards, “Editor's Choice”, rankings, prices, or download call-to-actions.
- Do not use alpha, transparency, or a transparent PNG background.
- Do not shrink a paragraph to make it fit; cut the copy instead.
- Check the graphic at 50% scale. If the headline is unreadable, make it shorter and larger.

## Worked example: Between v1.2

The five-image set uses the following copy and palette. Keep this as a reference for tone and proportion, not as copy to reuse for another app.

| # | Eyebrow | Headline | Supporting copy | Footer | Background |
|---|---|---|---|---|---|
| 01 | CONVERSATION COMES FIRST | Less noise. / *More conversation.* | A simpler inbox. Clear unread messages. / Straight to the people you want to talk to. | A little less between you. | `#3C2634` |
| 02 | PEOPLE YOU MAY KNOW | People you / *may know.* | Start with everyone. Use filters / to choose who you see. | Your next conversation starts here. | `#F7F4ED` |
| 03 | LIFE, LATELY | Little moments. / *More connection.* | A lighter feed that leaves room / for the conversation. | Small updates. Shared moments. | `#E3ECB8` |
| 04 | A LITTLE CREATIVE HELP | Your chat. / *A little more useful.* | Catch up, find a detail or make a reminder. / Meet your conversation's Private-AI. | Useful tools, one conversation at a time. | `#F7F4ED` |
| 05 | MAKE YOURSELF AT HOME | Your space. / *Your choices.* | Your profile, preferences and account. / Everything in one familiar place. | Between. Made for your everyday. | `#3C2634` |

The corresponding manifest fields are:

```json
{
  "slug": "01-chats",
  "feature": "CONVERSATION COMES FIRST",
  "title": ["Less noise.", "More conversation."],
  "body": ["A simpler inbox. Clear unread messages.", "Straight to the people you want to talk to."],
  "src": "01-chats.png",
  "bg": "#3C2634",
  "ink": "#F7F4ED",
  "accent": "#D7EA8E",
  "footer": "A little less between you.",
  "size": "1440x2560",
  "artwork": "v1.2/01-chats.png"
}
```

The manifest root also carries the two required store assets:

```json
{
  "icon": { "src": "icon-512.png" },
  "feature_graphic": { "src": "feature-graphic-1024x500.png" },
  "images": [ "..." ]
}
```

## QA checklist

- All five images use the same margins, type scale, brand lockup, and device treatment.
- Headlines and body copy fit their planned line count without clipping.
- The first image states the core promise and shows the primary screen.
- The five screens are distinct and exist in the submitted build.
- The device frame, screenshot, and status bar look coherent.
- Text remains readable at Play thumbnail size and at 50% scale.
- Background colors alternate with a deliberate rhythm and maintain contrast.
- Every screenshot is JPEG or 24-bit PNG, no alpha, 320–3840 px per side, and no wider than 2:1.
- The feature graphic is exactly 1024 × 500, RGB, no alpha, and stands alone as a brand poster.
- The icon is 512 × 512, 32-bit PNG with alpha, and at most 1 MB.
- The overview sheet is clearly a review artifact, not a sixth upload.
- The image order matches the PRD gallery table, metadata, and screenshot evidence.
