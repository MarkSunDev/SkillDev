# Google Play PRD integration standard

Sources: Google Play Console Help pages on store listing, screenshot and feature graphic specifications, Data safety, content ratings, target audience and content, account deletion, and app bundles. Re-check the live pages at submission time; the numbers below are a starting point, not a permanent contract.

Apply these rules when adding metadata, review notes, and declarations to a Google Play PRD:

- Put the application information table, review notes with App access instructions, screenshot plan, and App content declarations at the beginning of the PRD, before workflow, product, design, and technical sections.
- Keep the listing copy, legal/support surfaces, screenshots, feature graphic, declarations, review instructions, and demo path aligned with the exact build being submitted.
- Describe a first-minute review path with three observable beats: the promise is clear within 0–10 seconds, the signature action is reachable within 10–30 seconds, and a useful consequence is visible within 30–60 seconds.
- Demo credentials must use the product's normal sign-in path. Do not create hidden reviewer-only behavior.
- Only list tabs, features, purchases, AI behavior, safety controls, and monetization that work in the submitted build.
- Do not present seeded or simulated data as real users, metrics, or press.
- For live UGC, ensure report, block, account deletion, and support paths exist before claiming review readiness.
- For AI features, state where AI acts, what data crosses the local/remote boundary, and what consent or control exists only when those mechanisms are implemented.
- If the product uses a Chats-first or other specific navigation model, record the actual tab order and default destination; do not invent a different first-run path for review.
- Keep legal, privacy, terms, support, website, and deletion URLs live and consistent with the in-app surfaces.

## Metadata limits

- App name: 30 characters. No emoji, decorative symbols, call-to-action words, ranking claims, other brands, or Google/Android/Play trademarks.
- Short description: 80 characters. One sentence, no emoji, no keyword stuffing.
- Full description: 4,000 characters, plain text, no HTML. The first two lines must carry the promise.
- Category: one Play category, no subcategory. Tags: up to five, from the list Play Console offers.
- Icon: 512 × 512, 32-bit PNG with alpha, at most 1 MB. It is a separate asset from the in-app adaptive launcher icon and from a flattened App Store icon.
- Feature graphic: 1024 × 500, JPEG or 24-bit PNG with no alpha, at most 15 MB, required.
- Phone screenshots: 2–8 per device type, 320–3840 px per side, aspect ratio no wider than 2:1, JPEG or 24-bit PNG with no alpha.
- Tablets, Chromebook, and Android XR have separate tiers and requirements. Check the device catalog in Play Console.
- Re-check every size and count against Play Console before export; do not rely on this file as the current source of truth.

## Screenshot and feature graphic rules

- Treat the five-image set as part of the submission package, not decoration. Use real screenshots from the exact build, one shared editorial layout, and five distinct product pillars.
- Compose screenshots on a 9:16 canvas at 1440 × 2560, then export 1080 × 1920. Never upload a raw 20:9 capture that exceeds the 2:1 limit.
- Make the first image state the core promise with the primary screen. The remaining images should cover discovery, content, signature utility/AI, account/personalization, or the actual product pillars.
- Keep the image order, gallery copy, Full Description, and screenshot evidence in one manifest so they cannot drift apart.
- Keep the overview sheet in the PRD for review; upload only individual screenshots to Play Console.
- The feature graphic is a brand poster with one message. Do not reuse a screenshot, add ratings/awards, or put critical content near the cropped edges.

## App content declarations

- Complete every declaration in Play Console → App content before submitting: Data safety, content rating, target audience and content, ads, app access, account deletion, and the applicable news/government/financial/health declarations.
- Data safety must match the SDK inventory, the runtime behavior, and the Privacy Policy. When an SDK changes, update Data safety and the legal drafts before release.
- Content rating answers must include UGC, AI-generated content, ads, purchases, and mature themes that actually appear in the build.
- Do not select an audience that includes children unless the app complies with the Families policy in ads, data practices, and content. If the app is 18+, state that consistently in the listing, declarations, and legal copy.
- Apps that let users create accounts must offer account deletion in-app and through a publicly reachable web URL. The same URL is used in Data safety.
- Restricted permissions (SMS/Call Log, background location, all-files access, package visibility, and similar) need a declaration and an in-app rationale. Do not request permissions the current feature set does not use.
- Use one contact email for every privacy, support, deletion, data-rights, and complaint channel.

## Legal drafts

- Draft Privacy Policy and Terms of Service in English for the current build, using the workflow in `references/privacy-terms.md`.
- Describe purchases as processed by Google Play where that is how the build bills; cancellation and refunds follow Google Play policy.
- Describe account deletion as available in-app and at the published web URL when both exist.
- Do not add absolute negative commitments such as “we do not collect”, “we do not sell”, “we never share”, or a fixed retention period.
- Do not name SDKs, data recipients, transfer destinations, or retention periods in the first draft; leave those for the feature/SDK checklist and legal review.
- Send the legal drafts and the completed HTML checklist result to legal together. Do not mark the policies live before legal review.
- Record the agreement version, effective date, Privacy Policy URL, Terms URL, and account deletion URL in the PRD and keep them consistent.

## Release mechanics

- Google Play requires an Android App Bundle (AAB) for new apps and updates. Confirm signing, version code, and the submitted track before referencing the build in the PRD.
- New apps and updates must meet the current target API level requirement. Check the annual deadline in Play Console instead of assuming last year's API level is still accepted.
- New personal developer accounts must complete a closed test with the current required tester count and duration before applying for production access. Check the live requirement; organization accounts are subject to different rules.
- Use internal testing, closed testing, and staged rollout as the PRD's release path, and record which track contains the build shown in the screenshots.
- Localized listings must use the same build and the same claims. Do not localize screenshots and descriptions independently.
