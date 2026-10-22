# Content Policy Gate

A skill for adding or auditing one transparent, deterministic content-availability gate in an app. Every content surface reads the same decision instead of re-implementing policy rules.

## What it does

- Takes only declared inputs: country/region, age band, account state, and server-issued compliance flags.
- Runs a pure engine that returns a mode, ordered reason codes, the policy version, and the evaluation time.
- Applies the most restrictive applicable mode. Default precedence:

```text
unavailable > ageVerificationRequired > limited > full
```

- Records a bounded audit trail of declared inputs, decision, and reasons.
- Keeps the decision explainable to the person it applies to: the app can show the same mode and reasons the gate used.

## When to use

- Regional legal gating, age gating, account-state restrictions, or moderation modes.
- Auditing an existing gate for hidden inputs, duplicated rules, or unexplainable decisions.
- Adding a compliance boundary that must be consistent across feed, chat, profile, and commerce surfaces.

## Hard boundaries

This skill is for transparent policy enforcement, not review evasion.

- Do not infer who is reviewing the app. No reviewer-location heuristics, VPN detection, device-model checks, time-zone guesses, IP geolocation, or attribution-based cloaking.
- Do not hide a policy from the people it applies to.
- Do not let UI code re-implement the rules. One gate, one decision, every surface reads it.

## Workflow

1. Declare the inputs and use `unknown` when a value is missing.
2. Implement a pure `ContentPolicyGate` with a versioned configuration and an injected evaluation date.
3. Evaluate every applicable rule, then choose the most restrictive mode.
4. Evaluate once at the app-state boundary and publish the decision; re-evaluate only when declared inputs change.
5. Log declared inputs, decision, and reason codes without surveillance data.
6. Test the matrix, not one path.

## Test matrix

- Full access.
- Each individual restriction.
- Overlapping rules and precedence.
- Unknown inputs.
- Determinism across repeated evaluations.
- Input normalization.
- Audit capacity and truncation behavior.
- App-state integration and re-evaluation triggers.

## Files

- `SKILL.md` — workflow, boundaries, and default precedence.
- `references/swift-implementation.md` — Swift reference implementation, decision matrix, and audit-log shape.

## Related skills

- `social-app-delivery` — product-level state and error contracts that the gate decision feeds into.
- `legalH5` — privacy and terms pages must describe the same regional, age, and account-state behavior.
