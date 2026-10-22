# Privacy Policy and Terms of Service drafting

Source: https://presence.feishu.cn/docx/NQ8fd5BcLomTgGx9bEBcMLNdnzf

Use this reference when an App Store PRD needs English legal copy, or when the user asks for a Privacy Policy or Terms of Service draft. The output is a first draft for legal review, not a substitute for legal sign-off.

## Inputs

Collect these before drafting:

- App name as shown on the store.
- Platforms: iOS, Google Play, or both.
- Distribution regions; use `United States` when the PRD targets the US.
- One contact email for privacy, support, account deletion, data-rights requests, DMCA, and all other external legal contacts.
- Monetization: free, subscription, in-app purchases, advertising, or a combination.
- Actual age gate in the submitted build. The source prompt defaults to 18+ with age verification; do not claim an age gate the build does not enforce.
- Current-version feature inventory. Do not include future or unreleased features.

Feature inventory to check against the build:

- Account registration and login
- Social or user-generated content
- Payments, subscriptions, or in-app purchases
- AI generation or AI-assisted features
- Location
- Camera or microphone
- Contacts or photo library
- Push notifications
- Health or fitness data
- Cloud storage
- Advertising, analytics, crash-reporting, login, or other SDKs

## Drafting rules

- Write in English for a US-market app and cover the minimum expectations of Apple App Store, Google Play, CCPA/CPRA, COPPA, and general US consumer-protection rules.
- Do not include the company legal name, registered address, website, or entity details. Do not use placeholders such as `[COMPANY LEGAL NAME]`, `[WEBSITE URL]`, or `[ADDRESS]`. Refer to the app by its store name or use “we / us / our”.
- Use one contact email for every external privacy, support, deletion, rights, and complaint channel.
- Use “may” and category-level wording. Do not make absolute negative commitments such as “we do not collect”, “we do not sell”, “we never share”, or “we retain data for no more than X days”.
- Do not name third-party SDKs, data recipients, cross-border destinations, or retention periods in the first draft. Describe categories and say providers may be updated from time to time.
- Do not state that the app collects or shares a category unless the current build actually does so. Keep the drafts aligned with the completed feature/SDK checklist.
- Use plain, executable contract language rather than generic boilerplate.
- Output the full Terms of Service first, then the full Privacy Policy, both in English Markdown with numbered sections.

## Terms of Service required sections

1. Acceptance of Terms and eligibility (18+ where the source prompt applies and the build enforces an age gate).
2. Accounts: registration, account security, and the operator's right to suspend or terminate.
3. Purchases, subscriptions, and in-app purchases: pricing, billing, auto-renewal disclosure, cancellation through the applicable platform, and platform refund rules.
4. User content and UGC, when applicable: license to the operator, prohibited conduct, moderation, and removal rights.
5. AI features, when applicable: accuracy disclaimer, no professional advice, and usage boundaries.
6. Intellectual property and limited license.
7. Disclaimer of warranties; service provided “AS IS”.
8. Limitation of liability to the maximum extent permitted by law.
9. Indemnification by the user.
10. Governing law: laws of the State of Delaware, without conflict-of-law rules.
11. Dispute resolution: binding individual arbitration under the American Arbitration Association Consumer Arbitration Rules, one arbitrator, Wilmington, Delaware; clear class-action waiver; preserve small-claims court, injunctive relief, and intellectual-property exceptions.
12. Changes to the Terms and notice through the app or the published policy channel.
13. Contact using the single contact email.

## Privacy Policy required sections

1. Who we are and how to contact us, using the app name and the single contact email.
2. Information we collect, by category: account, profile, device and advertising identifiers such as IDFA/GAID, IP and network status, location when applicable, usage and diagnostics, user-submitted content, photos/camera/microphone when applicable, and payment information handled by platforms or payment processors.
3. How information is used: provide the service, improve and develop it, security, analytics, advertising and marketing where permitted, and enforce the Terms.
4. How information is shared: service providers, payment processors, advertising and analytics partners, legal or regulatory requirements, and corporate transactions. Use “may” wording and do not take a definitive position on whether data is sold.
5. Cookies and similar technologies, including advertising identifiers and device-level controls for personalized advertising.
6. Data retention: retain as long as necessary to provide the service, comply with legal obligations, resolve disputes, and enforce agreements; no fixed day count.
7. User rights: access, correction, deletion, account deletion, opt-out of sale/sharing, and opt-out of targeted advertising, with the single contact email for requests. Include CCPA/CPRA rights for California users without definitively stating whether the operator sells or shares personal information.
8. Children's privacy: the service is for users 18+ where the source prompt applies; do not knowingly collect information from children under 13, and provide the contact email for deletion requests.
9. International data transfers, described at category level when applicable.
10. Security: administrative, technical, and physical safeguards, without promising absolute security.
11. Policy updates and notice method.
12. Contact using the single contact email.

## Legal handoff

1. Generate the two drafts from the prompt below using the current-version feature inventory.
2. Open the HTML checklist linked in the source document, select only what the current build does, add SDK names where required, and press “生成结果”.
3. Send the draft and the copied checklist result to legal together.
4. After legal review, record the agreement version, effective date, and live URLs in the PRD. Do not mark either document live before the URL resolves and matches the submitted build.
5. When a future feature or SDK goes live, update the checklist and ask legal to revise the agreements before release.

## Reusable prompt

Replace every `{...}` value with actual content. Delete feature categories that do not apply. Do not leave placeholder names or URLs in the output.

```text
You are a US-market app compliance lawyer drafting an English Terms of Service and Privacy Policy for an iOS / Google Play app. You may refer to the structure and common wording of well-known US-facing apps with similar features, but do not copy their text, company names, SDK lists, or specific commitments. Draft both documents to meet the minimum expectations of Apple App Store, Google Play, CCPA/CPRA, COPPA, and general US consumer-protection law, while limiting our liability and avoiding commitments beyond legal requirements.

APP INFORMATION
- App name as shown on the store: {App name}
- Platforms: {iOS / Google Play / both}
- Distribution regions: {United States / other: ___}
- Single contact email for privacy, support, account deletion, data-rights requests, and all other external contacts: {contact@example.com}
- Monetization: {free / subscription / in-app purchases / advertising; select all that apply}
- Age threshold: default to 18+ with age verification at entry; users under 18 are not permitted to use the service.

CURRENT-VERSION FEATURES
Keep only the features that exist in the submitted build:
{account registration and login / social or UGC / payments / AI generation / location / camera or microphone / contacts or photo library / push notifications / health or fitness data / cloud storage}

DRAFTING PRINCIPLES
1. Do not include the company legal name, registered address, website, entity details, or placeholders such as [COMPANY LEGAL NAME], [WEBSITE URL], or [ADDRESS]. Refer to the app by its store name or use “we / us / our”.
2. Do not write “we do not collect”, “we do not sell”, “we never share”, “we retain data for no more than X days”, or similar absolute commitments. Use “we may collect/share ... as described in this Policy” and similar qualified wording.
3. In this first draft, do not name third-party SDKs, specific data recipients, cross-border destinations, or retention periods. Use category-level wording such as “we may share information with analytics, advertising, crash-reporting, payment and login service providers as necessary; the list of providers may be updated from time to time.”
4. Use the single contact email above for every external contact channel, including privacy questions, support, account deletion, data-rights requests, and DMCA complaints. Do not include any other email or address.

TERMS OF SERVICE REQUIRED SECTIONS
1. Acceptance of Terms and eligibility (18+ only).
2. Accounts: registration, account security, and our right to suspend or terminate.
3. Purchases, subscriptions, and in-app purchases: pricing, billing, auto-renewal disclosure, cancellation through the applicable platform, and platform refund rules.
4. User content and UGC, if applicable: license to us, prohibited conduct, moderation, and removal rights.
5. AI features, if applicable: accuracy disclaimer, no professional advice, and usage boundaries.
6. Intellectual property and limited license.
7. Disclaimer of warranties; service provided “AS IS”.
8. Limitation of liability to the maximum extent permitted by law.
9. Indemnification by the user.
10. Governing law: laws of the State of Delaware, without conflict-of-law rules.
11. Dispute resolution: any dispute goes to binding individual arbitration under the American Arbitration Association Consumer Arbitration Rules, with one arbitrator, in Wilmington, Delaware. Include a clear CLASS ACTION WAIVER: users waive the right to bring or participate in any class, collective, consolidated, or representative action, and all disputes must be brought individually. Preserve the standard exceptions for small-claims court, injunctive relief, and intellectual-property enforcement.
12. Changes to the Terms and notice through the app or the published policy channel.
13. Contact using the single contact email.

PRIVACY POLICY REQUIRED SECTIONS
1. Who we are and how to contact us, using the app name and the single contact email.
2. Information we collect, by category: account information, profile information, device information and advertising identifiers such as IDFA/GAID, IP address and network status, location if applicable, usage and diagnostic data, user-submitted content, photos/camera/microphone if applicable, and payment information processed by platforms or payment processors. Do not list specific SDK names.
3. How we use information: provide the service, improve and develop it, security, analytics, advertising and marketing where permitted, and enforce the Terms.
4. How we share information: service providers, payment processors, advertising and analytics partners, legal or regulatory requirements, and corporate transactions. Use “may” wording and do not definitively state whether we sell data.
5. Cookies and similar technologies, including advertising identifiers and device-level controls for personalized advertising.
6. Data retention: we retain information for as long as necessary to provide the service, comply with legal obligations, resolve disputes, and enforce our agreements. Do not give a specific number of days.
7. Your rights: describe the categories of rights users may have (access, correction, deletion, account deletion, opt-out of sale/sharing, opt-out of targeted advertising) and how to exercise them through the single contact email. For California users, include the standard CCPA/CPRA rights (Right to Know, Right to Delete, Right to Correct, Right to Opt-Out of “Sharing/Selling”, Right to Non-Discrimination), without definitively stating whether we sell or share personal information.
8. Children's privacy: the service is for users 18+; we do not knowingly collect information from children under 13, and users can contact us at the single email to request deletion if a child has provided information.
9. International data transfers, if applicable: information may be processed in jurisdictions outside the user's country.
10. Security: administrative, technical, and physical safeguards, without promising absolute security.
11. Policy updates and notice method.
12. Contact using the single contact email.

OUTPUT
- Output the full Terms of Service first, then the full Privacy Policy.
- Use English Markdown with numbered sections.
- Use plain, executable contract language; do not add generic filler.
- Do not include company names, SDK lists, URLs, addresses, or commitments not supplied above.
```

## QA checklist

- Both documents are present, with Terms first and Privacy Policy second.
- All required sections above are covered.
- No company legal name, address, website, or bracketed entity placeholder appears.
- One contact email is used everywhere.
- No absolute negative commitment or fixed retention period appears.
- No SDK name, recipient name, transfer destination, or retention period appears in the first draft.
- Only current-version features are described.
- The age gate, AI behavior, encryption, and data practices match the submitted build.
- The HTML checklist result and the drafts are ready to send to legal together.
