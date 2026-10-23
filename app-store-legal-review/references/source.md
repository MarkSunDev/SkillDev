# Source and provenance

- Document: 《App 上架协议审核 · 操作指引》
- URL: https://presence.feishu.cn/docx/NQ8fd5BcLomTgGx9bEBcMLNdnzf
- Revision: 47
- Retrieved: 2026-10-22
- Attachment: `app-function-checklist.html`, token
  `AUgvbeSvXoULtVxGtFrcsuGrnwF`, 21,384 bytes

The document has three sections:

1. Two things to send legal: the agreement draft and the HTML checklist result.
2. The HTML checklist tool and its filling rules.
3. The Chinese AI drafting prompt.

`references/drafting-prompt.txt` is the prompt from section 3, verbatim. The six
`{...}` inputs and the feature line are intentionally left as placeholders;
`scripts/prepare_brief.py` fills them from a config file.

The checklist was downloaded with `docs +media-preview`; the user identity used
for retrieval had no export permission for `docs +media-download`. The bundled
copy differs from the source attachment in one line: the platform row is
multi-select so that an app shipping on both stores can be recorded. The
generated output format is unchanged.

The source document describes an internal legal-review workflow. This skill
packages the workflow; it does not add legal conclusions. The draft remains
subject to review by qualified counsel.

## Four-page extension and benchmark

The four-page outline, preflight, and account-deletion/child-safety rules were
added on 2026-10-23. The structural benchmark was retrieved from public pages:

- Tinder Terms: https://policies.tinder.com/terms/intl/en/
- Tinder Privacy: https://policies.tinder.com/privacy/intl/en/
- Tinder deletion: https://www.help.tinder.com/hc/en-us/articles/6956972185229-Delete-your-Tinder-Account
- Bumble Terms: https://bumble.com/en-us/terms
- Bumble Privacy: https://bumble.com/privacy-policy/en/print
- Bumble deletion: https://support.bumble.com/hc/en-us/articles/28784017124381-Deleting-your-account
- Hily Terms: https://hily.com/terms-of-use/
- Hily Privacy: https://hily.com/privacypolicy/
- Hily deletion: https://hily-support-team.zendesk.com/hc/en-us/articles/360017081060-How-do-I-deactivate-or-delete-my-account

The benchmark is a structural reference, not legal advice and not a license to
copy another company's text. See `mature-dating-app-benchmark.md` for the
comparison and `four-page-set.md` for the page-by-page requirements.
