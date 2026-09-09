# silinmeng.com

Silin Meng's personal website: research, selected projects, experience, and a printable CV.

[Website](https://silinmeng.com/) · [CV](https://silinmeng.com/cv.html) · [Google Scholar](https://scholar.google.com/citations?user=wJdoPLsAAAAJ&hl=en)

A minimal, responsive site built with HTML and CSS, with serif typography, generous whitespace, and a small warm accent. The homepage and CV share the same profile and publication data.

## Local development

Python 3 is the only build requirement. All scripts use the standard library.

```sh
git clone https://github.com/SilinMeng0510/silinmeng.com.git
cd silinmeng.com
python3 scripts/build.py
python3 -m http.server 4173 --bind 127.0.0.1
```

Open [localhost:4173](http://localhost:4173/) for the homepage or [localhost:4173/cv.html](http://localhost:4173/cv.html) for the CV.

The CV supports printing and saving as PDF through the browser. Its small JavaScript file enables the print button; all page content is available without JavaScript.

## Project structure

```text
data/
  profile.json             Approved profile, experience, education, and links
  publications.json        Verified publication records and source links
  README.md                Content verification and update policy
templates/
  index.html               Homepage template, including selected projects
  cv.html                  Printable CV template
scripts/
  render_site.py           Data validation and HTML generation
  update_publications.py   Import and merge verified publication snapshots
  build.py                 Render pages and package public assets
dist/css/                  Screen and print styles
dist/js/cv.js              Optional CV print button
tests/                     Profile, publication, and rendering checks
index.html                 Generated homepage
cv.html                    Generated CV
CNAME                      Custom domain configuration
out/                       Generated deployment package; ignored by Git
```

## Editing content

Update `data/profile.json` for approved profile content and `data/publications.json` for verified publication records. Work experience currently includes Boson AI and UCLA.

Edit the files in `templates/` for page structure and selected projects, and `dist/css/` for styling. Rebuild after changes rather than editing the generated root HTML files.

```sh
python3 -m unittest discover -s tests
python3 scripts/build.py
```

The generated `index.html` and `cv.html` are committed alongside their sources so the repository can be served as a static site.

## Publication updates

A local Codex automation checks Google Scholar every Monday at 09:00 in the configured local timezone. It verifies publication changes against their sources and supplies a JSON snapshot to the importer:

```sh
python3 scripts/update_publications.py /absolute/path/to/verified-snapshot.json
python3 -m unittest discover -s tests
python3 scripts/build.py
```

Papers are merged by stable Scholar IDs. Incomplete results retain existing papers, invalid or empty snapshots are rejected, and unchanged checks leave the saved data untouched.

The schedule runs in Codex on the owner's computer and requires that computer, Codex, and source access to be available. No GitHub Actions workflow performs the synchronization, and visitors' browsers do not fetch Scholar or LinkedIn data.

Changes to work experience require the owner's confirmation before publication. The renderer checks the approved profile snapshot for accidental changes. See [the content policy](data/README.md) for the verification process.

## Deployment

The repository is [SilinMeng0510/silinmeng.com](https://github.com/SilinMeng0510/silinmeng.com), with `silinmeng.com` configured in `CNAME`. The generated root HTML files and public assets are published from the repository's `main` branch through its GitHub Pages setup.

The build also writes a compact static package to `out/`, containing only the generated pages and required public assets. `.openai/hosting.json` configures a separate private Sites preview.

The website has no third-party runtime dependencies or externally hosted fonts.
