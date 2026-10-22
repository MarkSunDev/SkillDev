# App Store PRD integration standard

Source reviewed: https://presence.feishu.cn/docx/G780dyCDhoBdLuxCmTZc6kzWnGe

Five-image reference: https://presence.feishu.cn/wiki/XtbYwfkJiiu4DekquUjcpCAqn5c

Privacy and Terms source: https://presence.feishu.cn/docx/NQ8fd5BcLomTgGx9bEBcMLNdnzf

Apply these rules when adding metadata and review Notes to an App Store PRD:

- Put the application information table and review Notes at the beginning of the PRD, before workflow, product, design, and technical sections.
- Keep the listing copy, legal/support surfaces, screenshots, review Notes, and demo path aligned with the exact build being submitted.
- Describe a first-minute review path with three observable beats: the promise is clear within 0-10 seconds, the signature action is reachable within 10-30 seconds, and a useful consequence is visible within 30-60 seconds.
- Demo credentials must use the product's normal sign-in path. Do not create hidden reviewer-only behavior.
- Only list tabs, features, purchases, AI behavior, safety controls, and monetization that work in the submitted build.
- Do not present seeded or simulated data as real users, metrics, or press.
- For live UGC, ensure report, block, account deletion, and support paths exist before claiming review readiness.
- For AI features, state where AI acts, what data crosses the local/remote boundary, and what consent or control exists only when those mechanisms are implemented.
- If the product uses a Chats-first or other specific navigation model, record the actual tab order and default destination; do not invent a different first-run path for review.
- Keep legal, privacy, terms, support, and marketing URLs live and consistent with the in-app surfaces.
- Draft Privacy Policy and Terms of Service in English for the current build, using the workflow in `references/privacy-terms.md`.
- Keep both legal drafts aligned with the actual data flows, SDKs, monetization, age gate, and features in the submitted build.
- Use one contact email for every privacy, support, deletion, data-rights, and complaint channel.
- Do not add absolute negative commitments such as “we do not collect”, “we do not sell”, “we never share”, or a fixed retention period.
- Do not name SDKs, data recipients, transfer destinations, or retention periods in the first draft; leave those for the feature/SDK checklist and legal review.
- Treat the 18+ age gate in the source prompt as the default for the legal draft, but only claim it when the build enforces it.
- Send the legal drafts and the completed HTML checklist result to legal together. Do not mark the policies live before legal review.
- Record the agreement version, effective date, Privacy Policy URL, and Terms URL in the PRD and keep them consistent.
- Treat the five-image set as part of the submission package, not decoration. Use real screenshots from the exact build, one shared editorial layout, and five distinct product pillars.
- Make the first image state the core promise with the primary screen. The remaining images should cover discovery, content, signature utility/AI, account/personalization, or the actual product pillars.
- Keep the image order, gallery copy, App Store description, and screenshot evidence in one manifest so they cannot drift apart.
- Keep the overview sheet in the PRD for review; upload only the five individual portrait images to App Store Connect.
- At submission readiness, verify screenshot sizes and counts against current App Store Connect requirements instead of relying on stale values.
- As of October 2026, iPhone submissions require a Dynamic Island (medium display) screenshot at 1179 × 2556 or 1206 × 2622. Large-display masters are accepted at 1260 × 2736, 1290 × 2796, or 1320 × 2868. Export flattened RGB PNG/JPEG with no alpha channel; iPad 13-inch requires 2064 × 2752 or 2048 × 2732.
