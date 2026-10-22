# App Store PRD Metadata

A skill for adding App Store submission material to an app PRD without duplicating existing sections. It writes the application information table, App Review Notes, a five-image plan, and optional English Privacy Policy / Terms of Service drafts.

## When to use

- The PRD needs App Store listing copy, character-count checks, review notes, or a screenshot plan.
- The app is being submitted and needs demo-account instructions, privacy/support URLs, and legal copy.
- An existing App Store section needs to be updated in place rather than duplicated.

## What it writes

1. **Application information** — a two-column table with current count and limit for every field: icon, name, subtitle, promotional text, keywords, category, age rating, regions, contact/support/marketing/privacy/terms URLs, legal entity, agreement version, description.
2. **App Review Notes** — a working demo account, the exact review path, feature toggles, and anything a reviewer must know about the submitted build.
3. **Five-image App Store set** — one shared editorial wrapper across five portrait screenshots. Master canvas `1320 × 2868`; also export `1206 × 2622` for the required medium iPhone tier. PNG/JPEG with no alpha.
4. **Privacy Policy & Terms** — English drafts in Terms-first order, using only behavior present in the current build. Final legal review is still required.
5. **PRD alignment** — the submission table, gallery status, and legal URLs stay consistent with the rest of the PRD.

## Inputs

- The PRD and a precise description of the build being submitted.
- App name, subtitle, keywords, category, age rating, regions, legal entity.
- A working demo account and the reviewer navigation path.
- Real screenshots from the submitted build, or an explicit `[待截图]` plan.
- Support, marketing, privacy, and terms URLs.

## Validate

```bash
python3 scripts/check_metadata.py metadata.json
python3 scripts/check_gallery.py gallery.json --pretty
python3 scripts/check_gallery.py gallery.json --pretty \
  --check-files --assets-dir ./screenshots --size 1320x2868
```

`--check-files` verifies existence, PNG/JPEG format, alpha rules, and exact dimensions. Install Pillow first if needed:

```bash
python3 -m pip install Pillow
```

## Files

- `SKILL.md` — full workflow, field limits, screenshot selection rules, and legal drafting rules.
- `references/metadata-template.md` — PRD planning tables.
- `references/five-image-style.md` — editorial wrapper and screenshot composition system.
- `references/prd-integration.md` — where sections go and how to update in place.
- `references/privacy-terms.md` — required clauses and reusable drafting prompt.
- `scripts/check_metadata.py`, `scripts/check_gallery.py` — validators.

## Related skills

- `brand-store-assets` — render icons, five-image sets, overview sheets, and device mockups.
- `legalH5` — host the privacy, terms, and account-deletion pages on a real domain.
- `google-play-prd-metadata` — the Google Play counterpart with Play-specific declarations.
