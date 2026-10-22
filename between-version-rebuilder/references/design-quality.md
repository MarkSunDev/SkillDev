# Design quality

The rebuild must look and feel authored, not templated. “Same design quality” does not mean pixel-copying the reference. It means the same level of hierarchy, restraint, legibility, state clarity, accessibility and craft.

## Visual charter

Before writing screens, lock these decisions in `DESIGN.md`:

- one scene or emotional promise;
- anti-references;
- colour roles, not isolated hex values;
- type roles and scale;
- spacing and radius scales;
- surface/elevation rules;
- icon and illustration rules;
- motion rules and Reduce Motion behavior;
- image and video treatment;
- accessibility commitments;
- what makes this release visually distinct from the reference.

Do not mix two competing visual directions. Do not use an editorial font for controls, and do not use decorative typography where the user needs to scan.

## Release-specific references

These describe the shipped reference direction. A differentiated rebuild may replace them entirely, but must meet or exceed the craft bar.

### 1.1 reference

- Lighter social surface: forest/teal accent, off-white paper, soft mint.
- Native typography for controls; one custom family for headings in the reference.
- Five tabs with visible labels.
- Chats is the primary destination; Contacts and Feed support conversation rather than portrait browsing.
- Rows are compact but readable; avatars are small; media does not dominate.
- Private-AI is shown as a quiet per-chat capability, not a dashboard or chatbot console.

### 1.2 reference

- Mature editorial direction: deep wine, warm paper and restrained citron.
- Serif display headings for discovery, Feed, profile and membership; native type for utility text.
- Chats-first hierarchy; compact rows and 16-point insets.
- People You May Know is a single-column list, not a portrait catalog.
- Feed uses small photo previews and opens full size on tap.
- Membership appears as one quiet editorial block, not a storefront.
- Motion is sparse: state transitions, typing dots, media controls. No decorative animation that competes with reading.

If the target visual language is new, write it as a complete system and do not borrow the reference's screenshots, icon set, wordmark treatment, typography pairing or exact palette.

## Screen quality bar

### Onboarding

- One clear promise per screen. Copy is short and concrete.
- Media supports the promise; it is never a fake person recommendation.
- Actions remain below the media, never floating over it.
- The whole page scrolls at accessibility sizes and on small screens.
- Every advance returns to the top; no clipped text or hidden action.

### Chats

- The first screen reads like a familiar inbox, not a dashboard.
- One unread treatment, one preview line, one timestamp. No repeated dots, locks or badges.
- Avatar, name and message text align on a clean baseline grid.
- The composer stays above the keyboard and safe area.
- Incoming avatar, relationship entry and unread back-count remain secondary to the message content.

### Contacts

- PYMK is for reading people, not browsing a photo wall.
- Real avatar, name and one short sentence do the work.
- Filters are a native sheet, not a permanent row of chips.
- Active filter state is visible without adding a summary row to the list.
- Empty, error, loading and real-empty results look different.

### Feed

- The post, not the chrome, carries the page.
- Author, time and actions stay compact.
- Photos are thumbnails until opened; they never reflow the page while loading.
- Large text and dark mode preserve contrast and tap targets.

### Private-AI

- Show the consent and memory state plainly.
- The memory visual is driven by real counts and the real window.
- Receipts are attached to answers, not buried in settings.
- Avoid AI-dashboard language, model jargon and decorative gradients.
- The two-key lock may be a metaphor only when the underlying state is honest.

### Commerce

- Benefits, prices, periods and balances are readable without a sales pitch.
- The purchase button states what happens; pending, unavailable and verification failure are distinct.
- Locked visitor entries do not reveal identities the account has not unlocked.
- Never use a fake discount, countdown or simulated success.

## Typography

- Use a small number of roles with clear jobs.
- Body text should remain comfortable at 15–17 pt depending on density; utility text should not fall below a readable caption size.
- Support Dynamic Type through accessibility sizes. Avoid fixed heights that clip text.
- Long names, long phrases and localized strings must wrap or truncate deliberately.
- Numeric badges and prices use tabular figures where available.

## Colour and surfaces

- Define semantic roles: canvas, grouped canvas, surface, ink, secondary text, line, accent, destructive, success, warning, locked.
- Check contrast for text, icons and message bubbles in light and dark appearance.
- Prefer flat grouped surfaces and hairline separators. Use elevation only when it communicates layering.
- Do not use colour alone to communicate consent, unread state, gender filter or purchase status.

## Motion

- Motion explains a state change; it does not decorate idle screens.
- Honor Reduce Motion with an opacity-only or static alternative.
- Pause background video when the app is inactive or the view disappears.
- Do not autoplay video with Reduce Motion or Low Power Mode.
- Keep typing dots and loading indicators from shifting layout.

## Accessibility

- Minimum 44-point hit target for every control.
- VoiceOver labels for stateful controls, badges and receipts.
- Voice Control names for icon-only controls.
- Dynamic Type through AX5 where the platform allows it; test the largest size on every primary screen.
- Light and dark appearance tested independently.
- No gesture-only action. Provide a visible or menu equivalent.
- Error messages name the failed action and the recovery step without exposing raw server text.

## Five-image set

Each release needs five real screenshots at 1290 × 2796, RGB PNG, en-US:

### 1.1

1. Hello — brand and product promise.
2. Conversation — real chat and message clarity.
3. Meet people — profile to conversation.
4. Everyday Feed — life updates, not a portrait catalog.
5. Private-AI — catch up, find, remind, one chat at a time.

### 1.2

1. Chats first — compact inbox and unread clarity.
2. People You May Know — default mixed list and user-controlled filters.
3. Life, lately — lighter Feed.
4. Private-AI — help inside the conversation.
5. Your space — profile, preferences and account.

Use one shared layout system across each set. Screenshots must come from the submitted build and real service data. Do not composite a concept UI or use a fake person.

## Design review gate

Before release, review the installed build at:

- standard text size, light appearance;
- standard text size, dark appearance;
- largest accessibility text size, light and dark;
- small-screen device;
- empty, loading, error and real-empty states;
- reduced motion and low power behavior;
- keyboard open, photo picker, filters sheet and purchase sheet.

Reject the build if the primary action is hidden, text clips, a badge is duplicated, an image shifts the layout after load, or a state is communicated only by colour.
