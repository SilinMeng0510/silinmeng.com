# Profile sources and update policy

`profile.json` is the user-approved career and education snapshot. The current experience selection is **Boson AI Member of Technical Staff and UCLA Master Researcher only**, approved in this task on September 9, 2026. The user explicitly excluded the Boson AI internship and removed the homepage Selected projects section. Do not restore internships, other LinkedIn positions, or the projects section during automatic updates.

`publications.json` contains the six papers read from the user's specified [Google Scholar profile](https://scholar.google.com/citations?user=wJdoPLsAAAAJ&hl=en), with full author lists and links verified against arXiv, ACL Anthology, OpenReview, and the COLM accepted-paper list. The profile links back to silinmeng.com and identifies Silin Meng at Boson AI. The source URLs and Scholar article IDs are part of every future verification, not just a name-based search.

## Scheduled updates

A weekly Codex task attached to this conversation reads the specified Scholar profile. It can use the normal browser when web retrieval is unavailable. It supplies a verified JSON snapshot to `scripts/update_publications.py`; the website itself never scrapes a visitor's browser or requires a LinkedIn session.

The task runs through Codex on this computer. It is not an always-on GitHub Action or a cloud crawler. Login, rate limits, or a computer/task that is unavailable can delay a check. On an unreadable source, preserve the previous version and report the actionable problem. Do not bypass a login, CAPTCHA, or rate limit; do not deploy a guessed or empty result.

After checking changes, use:

```sh
python3 scripts/update_publications.py /absolute/path/to/verified-snapshot.json
python3 -m unittest discover -s tests
python3 scripts/build.py
```

The importer merges by the stable Scholar citation ID, rejects mismatched profiles, unverified authorship, duplicates and empty input, and never automatically removes missing papers. New versions of a paper update its existing entry. Do not infer acceptance from a submission or replace a verified venue with an older arXiv comment. Changes need first-party evidence. A check with no content changes does not change the saved date or trigger a deployment.

## Work experience needs confirmation

Only the user can authorize a change to the selected experience, titles, dates, headline, or summary. Present the concrete proposed differences in this conversation and wait for the response. A pending proposal may be saved under `review/`, which is ignored by Git and never packaged. Do not modify `profile.json` while waiting.

After explicit confirmation, update only the agreed fields and approval date, then calculate `experience_approval.sha256` with `experience_digest(profile)` from `scripts/render_site.py`. The renderer compares that digest with the actual experience, headline, and summary and refuses stale approval. This protects against accidental edits; the digest is a consistency check, not an authorization system. Never refresh it merely to pass a build.

Future education changes should also be verified and presented for review before changing the approved profile. Do not publish LinkedIn account analytics, contact lists, posts, or unrelated personal information.

## Rendering and publishing

The homepage and printable CV use the same approved data. Edit `templates/index.html` and `templates/cv.html` for layout; the root `index.html` and `cv.html` are generated and committed for the existing static GitHub setup. The build's explicit public-file list excludes profile data, review proposals, source files, and automation metadata from the private Sites package.

The public repository is `SilinMeng0510/silinmeng.com`, with `silinmeng.com` configured in `CNAME`. The owner authorized publishing the redesigned website to GitHub on September 9, 2026. After a verified publication update passes validation, commit the updated data and generated pages to the current publishing branch, `main`, without overwriting unrelated changes. Keep the original domain and repository access unchanged. `.openai/hosting.json` configures the separate owner-private Sites preview, which can be updated from the same validated source. Work-experience and education changes still require explicit confirmation before either destination is updated.
