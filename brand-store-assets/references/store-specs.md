# Store specifications and validation

Current as of **2026-10-22**. Store requirements change; verify the live
documentation before submitting. This file records what the scripts enforce and
what to re-check manually.

## App Store

### Screenshots

| Device tier | Accepted portrait sizes | Notes |
|---|---|---|
| iPhone large display | 1320 × 2868, 1260 × 2736, 1290 × 2796 | 6.9"/6.7"/6.5" class |
| iPhone medium display (Dynamic Island) | 1206 × 2622, 1179 × 2556 | Required tier |
| iPad 13-inch | 2064 × 2752, 2048 × 2732 | Required when the app supports iPad |
| iPad 12.9-inch (older) | 2048 × 2732 | Accepted |
| iPhone 5.5-inch (legacy) | 1242 × 2208 | Only if the app supports the legacy tier |

- 3–10 screenshots per device size.
- PNG or JPEG, **no alpha channel**, no transparency.
- Keep the same five compositions across tiers; export a scaled copy, do not redesign.
- The overview contact sheet is a review artifact; never upload it.

Official reference: <https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications/>

### App icon

- **1024 × 1024**, PNG, **RGB, no alpha**.
- No rounded corners; Apple applies the mask.
- No transparency, no text, no screenshots.
- Keep critical content inside the central ~824 × 824 safe area.

Official reference: <https://developer.apple.com/design/human-interface-guidelines/app-icons>

## Google Play

### Screenshots

- 2–8 per device type.
- Each side **320–3840 px**.
- Aspect ratio **no wider than 2:1** (height/width ≤ 2 and width/height ≤ 2).
- JPEG or 24-bit PNG, **no alpha**.
- Phone master: **1440 × 2560** (9:16); lighter export: **1080 × 1920**.
- 7-inch and 10-inch tablets: up to 8 each; compose a tablet layout when supported.
- Chromebook and Android XR: check the device catalog in Play Console.
- Raw 20:9 / 19.5:9 captures exceed 2:1; place them inside a device frame on a 9:16 canvas.

Official reference: <https://support.google.com/googleplay/android-developer/answer/9866151>

### App icon

- **512 × 512**, **32-bit PNG with alpha channel**, **≤1 MB**.
- No baked rounded corners; Play applies a mask.
- Full-bleed artwork is safer than a floating transparent mark.

### Feature graphic

- **1024 × 500**, JPEG or 24-bit PNG, **no alpha**, **≤15 MB**.
- Required for every listing.
- Not a sixth screenshot. One message, brand lockup, 48–64 px safe margin.
- Some placements crop the edges; keep critical text and logo central.
- No ratings, awards, rankings, prices, or download CTAs.

### Android adaptive icon (for the app build, not the Play listing)

- 108 × 108 dp canvas; 72 × 72 dp visible; 66 × 66 dp safe zone (61.1%).
- Foreground and background layers at **432 × 432 px** (4×).
- Foreground: transparent, content inside the central 264 × 264 px.
- Background: opaque, no alpha.
- Monochrome layer for themed icons: transparent, one color.

Official reference: <https://developer.android.com/develop/ui/views/launch/icon_design_adaptive>

## What `check_assets.py` enforces

### Icons

- `icon-ios-1024.png`: 1024 × 1024, PNG, no alpha.
- `icon-play-512.png`: 512 × 512, PNG, alpha channel present, ≤1 MB.
- `icon-mark-1024.png`: 1024 × 1024, PNG, alpha.
- `icon-adaptive-foreground-432.png`: 432 × 432, alpha, content inside the central 264 × 264 safe zone.
- `icon-adaptive-background-432.png`: 432 × 432, no alpha.
- `icon-monochrome-432.png`: 432 × 432, alpha, safe zone.
- `icon-mask-preview.png`: optional QA sheet.

### Galleries

- exactly five images (the skill's editorial convention)
- required fields: `slug`, `feature`, `title`, `body`, `src`, `bg`, `ink`, `accent`, `footer`
- unique slugs, output filenames, and source screenshots
- two-line `title` and `body`; eyebrow/footer length; emoji; unverifiable claims
- valid six-digit hex colors
- ink/bg contrast ≥3:1 minimum, 4.5:1 warning, 7:1 recommendation
- accent/bg contrast ≥3:1 for large type
- PNG/JPEG, no alpha
- Apple accepted dimensions or Play 320–3840 px / 2:1
- declared `size` matches the raster
- source screenshot exists; warns on unusually tall/landscape captures

### Feature graphic

- 1024 × 500, PNG/JPEG, no alpha, ≤15 MB.

## Device frames and mockups

The canvas sizes above are the upload sizes. A phone frame is a design element
inside the screenshot, not a separate store asset. When the user asks for
device-specific frames:

- Google Play: Pixel-style frame with a punch-hole camera and side buttons.
- App Store: iPhone 18-style frame with a Dynamic Island and a thin titanium edge.
- Keep the whole frame visible, including the rounded bottom edge.

If the set is a mockup, rebuild the app UI deterministically from the product's
design system and use a generated fictional adult cast. Label it internally as a
mockup and never claim it is a real build capture. See `mockups-and-cast.md`.

## What the scripts do not check

- Whether the UI in the screenshot is real or a mockup. This is a human responsibility.
- Whether a mockup accurately reflects a submitted build. For a real listing, use real screenshots.
- Store policy for claims, pricing, or regulated categories.
- Text legibility on every physical device. Inspect the images.
- The actual App Store Connect / Play Console upload. The validators check documented dimensions and common rules, not acceptance.
- Localized copy quality. A human must review each locale.

## Re-check before submission

- [ ] App Store Connect screenshot specifications and required device tiers.
- [ ] Play Console screenshot, icon, and feature graphic specifications.
- [ ] The current target API level and build number.
- [ ] The submitted build matches the screenshots.
- [ ] The icon in the build matches the listing icon.
- [ ] The feature graphic is present and exactly 1024 × 500.
- [ ] No alpha in any store screenshot or the feature graphic.
- [ ] The Play icon is RGBA and ≤1 MB.
- [ ] The iOS icon is RGB and 1024 × 1024.
- [ ] Localized screenshots use the same build and claims.

## Official links

- App Store Connect screenshot specifications: <https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications/>
- Apple Human Interface Guidelines, app icons: <https://developer.apple.com/design/human-interface-guidelines/app-icons>
- Google Play screenshot requirements: <https://support.google.com/googleplay/android-developer/answer/9866151>
- Android adaptive icons: <https://developer.android.com/develop/ui/views/launch/icon_design_adaptive>
- Lucide license: <https://lucide.dev/license>
- iconLibrary: <https://iconlibrary.top/>
- Mobbin: <https://mobbin.com/>
- logo-generator-skill: <https://github.com/op7418/logo-generator-skill>
