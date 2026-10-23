# Google Form deletion request — branded POST

The standard integration is a **branded form on the Account Deletion page that
POSTs to the Google Form's `formResponse` endpoint**. The user fills our fields,
our page validates them, and the submission lands in the form owner's Google
account. Do not embed the Google Form in an iframe and do not send users to a
separate Google Form page.

## What Google Play requires

Google Play requires:

1. An in-app path to delete the account and associated data.
2. A public web resource where users who cannot access the app can request
   deletion.
3. The web URL declared in Play Console → App content → Data safety → Data
   deletion.

The web resource must load, name the app or developer, and offer a way to submit
a request. Google Play accepts a customer-service email or a form. The Play
Console field is the **public page URL** (for example
`https://example.com/account-deletion`), not the Google Form URL. The page posts
to the form behind the scenes.

## Create the form

Use a company-owned Google account that the team can keep and share. A personal
account creates an ownership and continuity risk.

Create a form with:

| Field | Type | Required | Notes |
|---|---|---|---|
| Account email / contact email | Short answer | Yes | Where the team replies; may differ from the app login |
| Account name / identifier | Short answer | Yes | Profile name or account ID used to locate the account |
| Reason | Dropdown | No | Break, privacy, not a fit, bug, other |
| Anything else | Paragraph | No | Device, approximate sign-up date, details |

Form title and description must name the app and the developer, e.g.
"<App> account deletion request — operated by <Developer Legal Name>". Include a
line that the request may require ownership verification and is not
instantaneous.

Settings:

- Published, anyone with the link can respond.
- Do not require Google sign-in.
- Do not limit to one response unless the team has a reason.
- Collect email addresses only if the team needs the respondent's Google
  account email; the "Account email" field already captures a contact address.
- Responses: link a Google Sheet and restrict access to the deletion team.
- Confirmation message: state that the request was received and that the team
  may follow up; do not promise immediate deletion.

## Copy the response endpoint and entry IDs

- Public form (for reference only; not used as the page UI):
  `https://docs.google.com/forms/d/e/<FORM_ID>/viewform`
- Response endpoint (required):
  `https://docs.google.com/forms/d/e/<FORM_ID>/formResponse`
- Field IDs (required): open the published form, view source, and find
  `entry.<number>` for each question. They look like `entry.123456789`.

Map the page fields to the Google Form entries:

| Page field | Google Form entry |
|---|---|
| contact email | `entry.<email>` |
| account identifier/name | `entry.<account>` |
| reason | `entry.<reason>` |
| details | `entry.<details>` |

All four `entry.*` values are required for the branded POST, even when the
reason and details fields are optional to the user. Re-read the entry IDs after
any form edit; Google can change them when questions are edited or reordered.

## Integrate the branded form

Use a hidden iframe as the form target so the browser is not blocked by CORS:

```html
<form id="delete-form" novalidate>
  <input id="del-email" type="email" required>
  <input id="del-account" type="text" required>
  <select id="del-reason">...</select>
  <textarea id="del-details"></textarea>
  <button type="submit">Submit deletion request</button>
</form>
<iframe name="delete-sink" hidden></iframe>
```

On submit:

1. Validate the email and account identifier.
2. Generate a local reference number.
3. Build a hidden form with `method="POST"`,
   `action="https://docs.google.com/forms/d/e/<FORM_ID>/formResponse"` and
   `target="delete-sink"`.
4. Add one input per mapped `entry.*` field. Append the reference number to the
   details value so the team can match the submission.
5. Submit the hidden form.
6. Show a confirmation with the reference. Tell the user that the team may
   contact them to verify ownership.
7. Keep a direct email link as a fallback for browsers that block the POST, but
   do not use it as the primary path.

The page cannot read Google's response through the hidden iframe (cross-origin),
so do not promise a real-time result. The confirmation means the browser
submitted the form, not that the account has been deleted.

## Privacy and operations

- Google is a third-party form/processor provider. Add "form and survey
  providers" (or equivalent) to the Privacy Policy's sharing categories.
- Link Google's privacy policy from the form or the deletion page.
- Restrict the response Sheet to the deletion team; do not use a shared drive
  that the whole company can browse.
- Assign an owner and a response-time target. The form does not delete
  accounts; a human must verify ownership and process the request.
- Delete or archive form responses when they are no longer needed, consistent
  with the retention wording.
- Do not claim that submissions go to Google Play; they go to the form owner.
- Do not claim automatic deletion or a fixed completion time unless the team
  can meet it.

## Verification before launch

1. Open the public page in a private window with no Google session.
2. Fill the branded form and submit; confirm the response appears in the Sheet.
3. Confirm the confirmation state and reference number appear.
4. Confirm the direct email fallback works.
5. Confirm the Play Console Data safety URL is the public page URL and returns
   200 without login.
6. Confirm the app config's account deletion URL matches both.
