# Originality and App Review

## Objective

The rebuild must be an independent product expression with the same functional and commercial contract. App Review 4.3(a) is a risk when an app is a copy, a repackaging, or a near-identical variant of another app. Renaming symbols, rearranging files or changing a colour is not differentiation.

Produce a genuinely authored implementation. Do not treat this skill as an obfuscation recipe.

## What may be identical

- protobuf field numbers, message IDs, routes and backend semantics;
- public product terminology required for user recognition, such as `Private-AI`, tab names and state labels;
- legal, privacy and support copy that must describe the same facts;
- backend-required constants, error codes and field names;
- the product's five-destination information architecture.

These are contract, not implementation.

## What must be independently authored

- source files, module boundaries, type names, function names, comments and test names;
- state ownership and data flow;
- navigation composition and screen construction;
- design tokens, palette, typography pairing, iconography and illustration;
- custom assets, video, sound, motion and screenshots;
- App Store copy beyond the product facts that must remain true;
- the target stack's platform adapters and accessibility implementation.

## Differentiation strategy

Write an `ORIGINALITY.md` that answers all of these:

1. What is the target stack, and why does the architecture fit it?
2. What is the visual scene, palette, type pairing, composition and motion language?
3. Which screens are recognizably the same user job but structurally different in layout and interaction?
4. Which assets are newly commissioned or generated for this build?
5. What code-level properties show that this is not a port of the reference file tree?
6. What real product value does 1.2 add beyond 1.1's visual treatment?
7. What evidence demonstrates the submitted build, not a concept?

If the answer to 6 is only “a different theme”, the release is not sufficiently differentiated. It must add real product or workflow value, as the reference 1.2 does with PYMK filters, chat enhancements and commerce.

## Automated audit

Run:

```bash
python3 scripts/audit_originality.py \
  --reference /path/to/reference/repo \
  --candidate /path/to/rebuild \
  --allow-glob 'references/**' \
  --allow-glob '**/*.proto' \
  --allow-glob '**/LICENSE*'
```

The script reports:

- exact text-file duplicates;
- exact asset duplicates;
- high token n-gram overlap between files;
- global token overlap ratio.

It exits nonzero when it finds an exact duplicate or a high-similarity source pair. Review every hit. A validator pass does not prove originality; it only catches copy-paste and asset reuse.

Do not add reference source to the candidate repository. Do not commit screenshots from the reference app as if they came from the rebuild.

## Manual review

Review the candidate against the reference:

- side-by-side source tree;
- side-by-side primary screens at the same text size;
- icon and asset inventory;
- string inventory, excluding API and legal terms;
- test names and fixtures;
- App Store five-image sets;
- onboarding sequence;
- chat composer, list row and profile composition;
- Private-AI and memory presentation;
- commerce sheet and visitor treatment.

Flag any copied screen structure even if colours and fonts differ.

## App Review package

Include:

- a short product description that names the real user job;
- the exact first-minute path that demonstrates the signature action;
- a screen recording from the submitted build;
- working demo credentials or a reviewer-safe account path;
- a list of real tabs and features;
- privacy and AI claims that match the build;
- purchase paths that work, or a clear unavailable state;
- report/block/delete-account paths where UGC is present;
- the five-image set with consistent framing and real UI.

Do not:

- describe unshipped MLS, encryption, model, call or push behavior;
- present fixtures as real people or real messages;
- claim a purchase succeeded without server verification;
- reuse another app's screenshots, icon, wordmark or proprietary visual assets;
- submit a build whose only difference is renamed code or a reskinned theme.

## Reviewable differentiation checklist

- [ ] Different stack or substantially different architecture.
- [ ] Different visual system and component construction.
- [ ] Different screen composition for at least the primary five tabs.
- [ ] Newly created assets and screenshots.
- [ ] Real 1.2 product value beyond 1.1 styling.
- [ ] No exact source or asset duplicate.
- [ ] No copied screen structure disguised by new colours.
- [ ] Claims match the submitted build.
- [ ] Evidence exists for every feature shown to a reviewer.
