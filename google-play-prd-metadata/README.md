# Google Play PRD Metadata

A skill for adding Google Play submission material to an app PRD without duplicating existing sections. It writes the application information table, review notes with App access instructions, a five-image plan plus feature graphic, App content declarations, and optional English Privacy Policy / Terms of Service drafts.

## When to use

- The PRD needs Google Play listing copy, character-count checks, review notes, or screenshot planning.
- The app needs Data safety, content rating, target audience, ads, account deletion, or restricted-permission declarations.
- An existing Play section needs to be updated in place rather than duplicated.

## What it writes

1. **Application information** — a two-column table with current count and limit for every field: icon, feature graphic, name, short/full description, category, tags, contact details, privacy policy, legal entity, agreement version.
2. **Review notes and App access** — working credentials, exact reviewer path, and any approval or login prerequisites.
3. **Five-image set and feature graphic** — one shared editorial wrapper across five portrait screenshots. Master canvas `1440 × 2560`; also export `1080 × 1920`. Feature graphic is exactly `1024 × 500`, JPEG or 24-bit PNG with no alpha.
4. **App content declarations** — Data safety, IARC content rating, target audience, ads, app access, account deletion, news/government/financial/health declarations, sensitive permissions.
5. **Privacy Policy & Terms** — English drafts in Terms-first order, consistent with the declared data flows.
6. **PRD alignment** — listing copy, declarations, SDK inventory, and legal URLs stay consistent.

## Inputs

- The PRD and a precise description of the build being submitted.
- App name, short/full description, category, tags, contact details, legal entity.
- A working demo account and the reviewer navigation path.
- Real screenshots from the submitted build, or an explicit `[待截图]` plan.
- SDK inventory and data flows for Data safety and the legal drafts.

## Validate

```bash
python3 scripts/check_metadata.py metadata.json
python3 scripts/check_metadata.py metadata.json --pretty
python3 scripts/check_gallery.py gallery.json --pretty
python3 scripts/check_gallery.py gallery.json --pretty \
  --check-files --assets-dir ./assets --size 1440x2560
```

`--check-files` verifies screenshot dimensions and ratios, the 512 × 512 32-bit icon, the 1024 × 500 feature graphic, and alpha-channel rules. Install Pillow first if needed:

```bash
python3 -m pip install Pillow
```

## Files

- `SKILL.md` — full workflow, field limits, screenshot and feature-graphic rules, declaration matrix.
- `references/metadata-template.md` — PRD planning tables.
- `references/screenshot-style.md` — editorial wrapper and composition system.
- `references/prd-integration.md` — where sections go and how to update in place.
- `references/privacy-terms.md` — required clauses and reusable drafting prompt.
- `scripts/check_metadata.py`, `scripts/check_gallery.py` — validators.

## Related skills

- `brand-store-assets` — render icons, five-image sets, feature graphics, overview sheets, and device mockups.
- `legalH5` — host the privacy, terms, and account-deletion pages on a real domain.
- `app-store-prd-metadata` — the App Store counterpart with App Review Notes.
