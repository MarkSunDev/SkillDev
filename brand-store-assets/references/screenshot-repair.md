# Screenshot repair

A screenshot can be imperfect without being unusable: a placeholder silhouette, a
gray avatar, an empty card, a missing photo, or a person region that must be
replaced. Repair the **specific region**, keep the rest of the screenshot intact.

This is a layer-compositing operation, not a redesign. Do not use it as an excuse
to change the app's layout, copy, hierarchy, or claims.

## What can be repaired

- placeholder silhouettes and generic user icons
- gray/blank avatars
- empty photo cards or missing images
- a person photo that must be replaced with a new fictional adult
- a cropped or low-quality subject region

## What must not be invented

- ratings, awards, download counts, or user counts
- a feature or screen that does not exist
- legal, medical, or financial claims
- a real person's likeness or a celebrity
- text in the app UI that changes the product's meaning

## Workflow

1. **Measure the region.** Use a coordinate grid on the cleaned screenshot. Write
   down `x, y, w, h` and the corner radius.
2. **Generate a replacement.** Use a fictional adult or a lifestyle image,
   text-only. For a profile card, use three-quarter/full body; for an avatar, use
   head-and-shoulders. Inspect modesty, likeness, text, and logos.
3. **Fill the region** with `scripts/repair_region.py`:

```bash
python3 scripts/repair_region.py base/likes.png people/isabella.png \
  --rect 18,300,265,245 --radius 30 --centering 0.5,0.22 \
  --fade-bottom 80 --fade-color "#2B1E24" \
  --out screens/likes.png
```

4. **Keep the text outside the region.** If the placeholder includes the name and
   label below the image area, fill only the image area; do not cover the text.
5. **Inspect** the result at full size and thumbnail size. Look for seams, a
   hard crop line, mismatched lighting, or a face cut at the edge.
6. **If the placeholder includes text inside the region**, do not fill over it.
   Recreate the card layer at the original size and text slots instead; see
   `layer-compositing.md`.

## Options

- `--shape rect|circle` — circle for avatars, rounded rect for cards/photos.
- `--radius` — card corner radius; use the original card's radius.
- `--centering x,y` — crop focus. For faces, `0.5,0.2`–`0.5,0.3`.
- `--fade-bottom` and `--fade-color` — blend the bottom of the replacement into
  the card background. Use the sampled card color.
- The base is never modified outside the rect/circle.

## Example: Flicker Likes

The original Likes card had a placeholder silhouette above the name. The repaired
screen fills only the image area:

- base: the original Likes screenshot (585 × 1313)
- region: `18,300,265,245`
- replacement: a new fictional **Isabella, 28**
- radius: 30
- centering: `0.5,0.22`
- fade: 80 px to `#2B1E24`
- the name “Isabella, 28” and “VISITED YOU” remain original

The phone screen now has a person, the card layout is unchanged, and the overflow
card uses the same Isabella portrait.

## QA

- [ ] The repaired region matches the original bounds and corner radius.
- [ ] The subject is fully clothed, non-explicit, and not the supplied person.
- [ ] The face is not cut by the crop; centering is adjusted if needed.
- [ ] The bottom fade blends into the card; no hard seam.
- [ ] Name, age, labels, buttons, and nav outside the region are unchanged.
- [ ] The screenshot still reads as the same app, with one imperfection fixed.
- [ ] No fake metrics, awards, or features were added.
