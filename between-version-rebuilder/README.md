# Between Version Rebuilder

A Codex skill for rebuilding the Between messaging app from a 1.0 baseline into code-sensitive, design-distinct 1.1 and 1.2 releases while preserving the shipped product behavior, commercial logic, and Romi backend contracts.

## Install

Place the folder at:

```text
${CODEX_HOME:-$HOME/.codex}/skills/between-version-rebuilder
```

Codex discovers it from `SKILL.md`.

## Use

```text
Use $between-version-rebuilder to rebuild this 1.0 baseline into 1.1 and 1.2.
Keep the Romi backend contract and shipped business rules.
Use a different implementation and visual language from the reference.
Produce the parity ledger, tests, screenshots, and originality audit.
```

## What is included

- `SKILL.md` — operating workflow and hard constraints.
- `references/source-of-truth.md` — PRD, shipped behavior, baselines, and conflict rules.
- `references/version-matrix.md` — 1.0/1.1/1.2 feature and business parity.
- `references/backend-contract.md` — Romi HTTP/protobuf, messaging gateway, TCP typing, commerce, intimacy.
- `references/protocols/` — exact protobuf definitions.
- `references/design-quality.md` — visual quality bar and release-specific design references.
- `references/originality-and-app-review.md` — code/design differentiation and 4.3(a) package requirements.
- `references/release-workflow.md` — test gates, evidence, screenshots, and release artifacts.
- `assets/iteration-brief.template.md` — starting brief and parity ledger.
- `scripts/audit_originality.py` — exact/near-duplicate source and asset audit.

## Originality audit

```bash
python3 scripts/audit_originality.py \
  --reference /path/to/reference \
  --candidate /path/to/rebuild \
  --allow-glob 'references/**' \
  --allow-glob '**/*.proto'
```

The audit is a review aid. It does not replace manual source, screen, asset, and product review.
