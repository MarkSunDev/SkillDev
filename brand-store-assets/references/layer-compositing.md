# Layer compositing

Use layer compositing when the user wants the **existing app layout preserved** and
only the people/content layers replaced. Do not rebuild the whole UI; that changes
spacing, type, and hierarchy, and it usually looks worse than the real app.

## When to use it

- “Keep the layout, replace the people.”
- “Only the person in the screenshot should change.”
- “The app content should look the same, but with new profiles/avatars.”
- A real screenshot exists and the design is already approved.
- The marketing wrapper can be exaggerated, but the app screen must stay faithful.

If the user wants a new feature, a new flow, or a screen that does not exist, that
is a **mockup** (see `mockups-and-cast.md`), not layer compositing.

## The layer stack

1. **Base** — the original screenshot, window chrome removed. Keep the status bar,
   header, controls, and nav.
2. **Subject layer** — only the person regions: a full profile card, an avatar
   circle, a selfie rectangle.
3. **Original UI layer** — everything outside the subject regions stays untouched.
4. **Overflow card layer** — a marketing card placed behind the phone, peeking out
   from the side. It is not part of the app screen.
5. **Device frame** — Pixel for Google Play, iPhone 18 for the App Store.
6. **Wrapper** — type, badge, sticker, callout, footer.

## Replacing a full profile card

If the person fills the card, replace the **whole card** with a new card layer at
the same coordinates:

- same card size, corner radius, and position
- same progress bars, gradient, name/age, location, tags
- new photo and, if needed, new name/tags
- rest of the screenshot untouched

This covers the old person and preserves the card's role in the layout. In the
Flicker example, the Discover card is `x=16, y=196, w=553, h=794` in a
585 × 1313 screenshot. The new card is drawn at 2× and downsampled for crisp type.

Do not paste a new photo over the card and leave the old name/tags floating on top;
that produces mismatched text and a visible seam.

## Replacing avatars and photo regions

- Avatars: use the exact circle bounds and a circular mask; replace only the
  circle, not the name/time beside it.
- Large photos: use the exact rounded-rectangle bounds; keep the post text and
  actions outside the photo.
- Feather the mask edges by 1–2 px so the replacement does not show a hard seam.
- Match the crop direction: a face should stay in the upper third; use
  `object-position` or `ImageOps.fit(..., centering=(0.5, 0.2))`.

If the person is embedded in a complex background and a clean cutout is impossible,
use an image-edit/inpainting model with a mask, or generate a new scene that
matches the background. Never use the supplied face as a reference.

## Repairing placeholders

If the imperfect area is a placeholder silhouette, gray avatar, empty card, or
missing photo, use `scripts/repair_region.py`:

```bash
python3 scripts/repair_region.py base/likes.png people/isabella.png   --rect 18,300,265,245 --radius 30 --centering 0.5,0.22   --fade-bottom 80 --fade-color "#2B1E24" --out screens/likes.png
```

Fill only the image area; keep the name/label below it. For a full card whose text
is inside the region, recreate the card layer instead. See
`screenshot-repair.md` for the full workflow.

## Overflow cards that exceed the phone

The user may ask for cards that “break out” of the phone. The best version is a
card **peeking out from behind** the phone, not a card covering the screen:

- Place the card behind the phone (z-index below the device).
- Show about 80% of the card; keep ~20% behind the frame.
- Align the card's text to the visible side:
  - left card: text starts at the left and stops before the hidden right edge
  - right card: text starts after the hidden left edge and ends at the right
- Keep the card name/sub inside the visible width; wrap the sub line instead of
  letting it disappear behind the phone.
- Do not cover the app's primary control, name, or nav. The card is a marketing
  layer, not a replacement for the UI.
- Use one overflow card per panel. More than one becomes a collage.

Manifest shape:

```json
"overflow": {
  "photo": "people/hannah.png",
  "name": "Hannah, 26",
  "sub": "HEAVY METAL · TATTOOS",
  "side": "left",
  "rotate": -7,
  "photo_position": "50% 16%"
}
```

`poster.html` positions the card relative to the computed phone box, sets the text
to the visible side, and keeps it behind the device. If the card is hidden because
the content is below the headline, check the `overflow` object and the photo path.

## Cast rules

- Generate **new fictional adults** from text only. Never pass the supplied
  screenshot or the original face as a reference.
- Full profile cards: three-quarter/full body, fully clothed, knee-length bottoms,
  high neckline, modest.
- Avatars/selfies: head-and-shoulders, fully buttoned high-neck clothing, no
  exposed chest, no suggestive pose, no tight clothing.
- Inspect every output. Delete failures; do not crop around them.
- Keep one cast consistent across screens.

## QA

- [ ] The original layout is unchanged outside the replaced regions.
- [ ] The new card uses the original card's size, radius, gradient, and text slots.
- [ ] Avatars/photo replacements align with the original bounds; no visible seam.
- [ ] The original person does not appear anywhere in the deliverable.
- [ ] Placeholder silhouettes/gray avatars are repaired, not left empty.
- [ ] The overflow card peeks from behind, not over the primary UI.
- [ ] The card name/sub is fully visible; the sub wraps inside the visible area.
- [ ] The device frame is correct and fully visible.
- [ ] The wrapper palette matches the app; no random style that fights the product.
- [ ] The final images still read as the same app, just with new people and a
      stronger marketing composition.
