---
name: content-policy-gate
description: "Add or audit a transparent, deterministic content-availability gate in an app. Use for regional legal gating, age gating, account-state restrictions, or moderation modes. Do not use for reviewer detection, VPN/device fingerprinting, cloaking, or hiding content from app-store review."
---

# Content Policy Gate

Build one policy decision that every content surface can share. The gate takes
only declared inputs, returns a mode plus human-readable reasons, and records a
bounded audit trail.

## Hard boundaries

- Do not infer who is reviewing the app. No reviewer-location heuristics, VPN
  detection, device-model checks, time-zone guesses, IP geolocation, or
  attribution-based cloaking.
- Do not hide a policy from the people it applies to. The app must be able to
  show the same mode and reasons the gate used.
- Do not let UI code re-implement the rules. One gate, one decision, every
  surface reads it.

## Workflow

1. **Declare the inputs.** Model country/region, age band, account state, and
   server-issued compliance flags as explicit values. Nothing is read from the
   device or network inside the gate. When the app lacks an input, use
   `.unknown` rather than guessing.
2. **Implement a pure engine.** Add a `ContentPolicyGate` that takes a context
   and a versioned configuration and returns a decision. Inject the evaluation
   date so tests are deterministic. The result contains a mode, ordered reason
   codes, the policy version, and the evaluation time.
3. **Make precedence explicit.** Evaluate every applicable rule, not just the
   first one, then choose the most restrictive mode. This keeps the reasons
   complete and makes the decision explainable.
4. **Integrate once.** Evaluate at the app-state boundary and publish the
   decision. Update the context when declared inputs change (region, age,
   account state) and re-evaluate. Do not add second gate calls in views.
5. **Audit without surveillance.** Record the declared inputs, decision, and
   reason codes in a bounded log. Never add IP addresses, device identifiers,
   VPN status, or other inferred signals.
6. **Test the matrix, not just one path.** Cover full access, each restriction,
   precedence when rules overlap, unknown inputs, determinism, normalization,
   audit capacity, and the app-state integration point.

## Default precedence

Most restrictive wins:

`unavailable` > `ageVerificationRequired` > `limited` > `full`

Server-issued legal blocks and blocked regions produce `unavailable`. Age
verification, under-minimum age, and unknown age produce
`ageVerificationRequired`. Account restrictions, limited regions, server
limits, and minor-account restrictions produce `limited`. Unknown regions use
the configuration's explicit fallback mode.

## Reference

Read `references/swift-implementation.md` when implementing in Swift or when
you need the decision matrix and audit-log shape.
