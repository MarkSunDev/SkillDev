# App Store five-image style system

Reference implementation: Between v1.1 / v1.2, App Store five-image set.

The set is a quiet editorial system built around real app screens. It is not five unrelated marketing posters: the grid, type scale, brand lockup, device treatment, and footer stay fixed; the screenshot, background color, and message change.

## Production sequence

1. Capture the five real app screens from the submitted build.
2. Build one reusable layout with layers: background, brand lockup, divider, eyebrow, headline, body, rule/slide number, device frame, screenshot, footer.
3. Fill the five copy blocks from the PRD gallery table.
4. Render all five images through the same layout component. Change only the text, background color, and screenshot.
5. Assemble the overview sheet from the five rendered images.
6. Validate the gallery manifest before exporting.

Use HTML/CSS, a design tool, or an image compositor. Do not let the model redraw or generate the app UI inside the phone.

## Canvas and delivery

- Produce five individual portrait RGB PNGs, in upload order `01`–`05`, with no alpha channel or transparency.
- Use **1320 × 2868** as the master canvas (current large-display iPhone). As of October 2026, App Store Connect also accepts **1260 × 2736** (iPhone Air) and **1290 × 2796** (iPhone 14/15 Pro Max, iPhone 16 Plus) for the large-display tier.
- App Store Connect currently requires at least one “iPhone with Dynamic Island (medium display)” screenshot at **1179 × 2556** or **1206 × 2622**. Export the same five images at 1206 × 2622 as well; do not redesign per size.
- If the app supports iPad, the 13-inch tier is required at **2064 × 2752** or **2048 × 2732**.
- Five is this set's editorial convention. App Store Connect accepts 3–10 screenshots per device size.
- Re-check the live screenshot specifications at submission time. Export the sizes that are required then; never treat these numbers as permanent.
- Keep a separate overview sheet for the PRD/review. The reference overview is a wide sheet with the title `[App] / [Version] / App Store five-image set`, five thumbnails in a row, and labels below. Do not upload the overview as one of the five App Store images.
- Keep the screenshot source files, the five finished images, the overview, the copy, and the gallery manifest together.

## Shared layout

Use these proportions as starting values; keep them consistent across all five images.

| Element | Placement |
|---|---|
| Brand lockup | top left, roughly 74–82 px from each edge; logo mark + wordmark on one line |
| Divider | thin horizontal rule below the brand row, with a small accent segment |
| Eyebrow | uppercase, wide tracking, directly below the divider |
| Headline | large serif display, two lines, first line roman, second line italic accent |
| Supporting copy | two lines of humanist sans below the headline |
| Accent rule + slide number | short accent-colored rule at left; slide number at right |
| Device | one large portrait device mockup with a real screenshot, centered in the lower two-thirds |
| Footer | one small centered line near the bottom edge |

Approximate 1320 × 2868 layout:

- side margin: 74–82 px
- brand row: y 82–154
- divider: y 195
- eyebrow: y 257
- headline block: y 328–575
- body block: y 616–708
- accent rule and slide number: y 780–800
- device top: y 841; device width: about 70–72% of canvas
- footer: y 2780–2811

These are proportions, not fixed pixels. When rendering 1290 × 2796, 1206 × 2622, or another accepted size, scale every value by the canvas height so the grid stays identical.

The device may overlap the lower copy zone slightly, but never clip the headline or supporting copy. Keep the screenshot undistorted and the status bar readable.

## Typography

- Display headline: `Instrument Serif` or an equivalent high-contrast editorial serif.
- First headline line: roman, brand ink.
- Second headline line: italic, accent color.
- Body: the app's existing sans, such as `Public Sans`, at a restrained editorial weight.
- Eyebrow: uppercase sans, roughly 24–28 px, 4–6 px tracking.
- Headline: roughly 100–116 px with tight line-height (0.96–1.0).
- Body: roughly 36–40 px with 1.3–1.4 line-height.
- Footer: roughly 20–22 px.

Keep each headline to two lines and each body block to two lines. If the copy does not fit, shorten it; do not reduce the type until it becomes unreadable at thumbnail size. The values above are for the 1320 × 2868 master; scale them proportionally for other accepted sizes.

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

## Copy system

Each image has five text slots:

1. Eyebrow: feature or context, 2–5 words, uppercase.
2. Headline line 1: a short benefit or tension, roman.
3. Headline line 2: the turn or payoff, italic accent.
4. Supporting copy: two concrete sentences or two short lines.
5. Footer: a four-to-eight-word brand line.

The eyebrow names the area. The headline sells the benefit. The supporting copy explains the actual behavior. The footer closes the set. Do not turn the headline into a feature list or repeat the App Store description.

## Five-image narrative

Use one distinct product pillar per image. A useful sequence for a social/chat product:

1. Core promise + primary screen (for a chats-first product, Chats).
2. Discovery or people.
3. Content or feed.
4. Signature differentiator or AI/utility.
5. Personalization, account, or trust.

For another product, replace these with its actual primary tabs and differentiators. Image 01 must carry the core promise. The remaining four should make the product feel broader than one screen. Do not repeat a tab or feature just to fill the set.

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
  "size": "1320x2868",
  "artwork": "v1.2/01-chats.png"
}
```

## QA checklist

- All five images use the same margins, type scale, brand lockup, and device treatment.
- Headlines and body copy fit their planned line count without clipping.
- The first image states the core promise and shows the primary screen.
- The five screens are distinct and exist in the submitted build.
- The device frame, screenshot, and status bar look coherent.
- Text remains readable at App Store thumbnail size.
- Background colors alternate with a deliberate rhythm and maintain contrast.
- Every file matches an accepted App Store Connect size for its device tier, including the required medium-display tier, and has no alpha channel.
- The overview sheet is clearly a review artifact, not a sixth upload.
- The image order matches the PRD gallery table, metadata, and screenshot evidence.
