"""Render the homepage and CV from reviewed, source-backed profile data."""

from datetime import date
from html import escape
import hashlib
import json
from pathlib import Path
import re
from string import Template
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SCHOLAR_ID = "wJdoPLsAAAAJ"
ARROW = '<span aria-hidden="true">↗</span>'


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected nonempty text")
    return escape(value, quote=True)


def safe_url(value):
    if not isinstance(value, str) or re.search(r"[\x00-\x20\x7f]", value):
        raise ValueError("Invalid link")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Source and profile links must be public HTTPS URLs")
    return escape(value, quote=True)


def validate_publications(data):
    if data.get("schema_version") != 1 or data.get("profile_id") != SCHOLAR_ID:
        raise ValueError("The publication snapshot must belong to the configured Scholar profile")
    source = urlparse(data["source_url"])
    from urllib.parse import parse_qs
    if source.hostname != "scholar.google.com" or parse_qs(source.query).get("user") != [SCHOLAR_ID]:
        raise ValueError("Unexpected Scholar source")
    safe_url(data["source_url"])
    date.fromisoformat(data["verified_on"])
    publications = data.get("publications")
    if not isinstance(publications, list) or not publications:
        raise ValueError("An empty or incomplete fetch must not replace the saved publications")
    ids, titles = set(), set()
    for paper in publications:
        identity = paper["id"]
        if not isinstance(identity, str) or not identity.startswith(SCHOLAR_ID + ":") or identity in ids:
            raise ValueError("Invalid or duplicate Scholar article ID")
        ids.add(identity)
        title_key = re.sub(r"\W+", "", paper["title"]).casefold()
        if not title_key or title_key in titles:
            raise ValueError("Duplicate or empty publication title")
        titles.add(title_key)
        text(paper["title"])
        text(paper["venue"])
        if type(paper["year"]) is not int or not 1900 <= paper["year"] <= date.today().year + 1:
            raise ValueError("Invalid publication year")
        authors = paper["authors"]
        if not isinstance(authors, list) or "Silin Meng" not in authors:
            raise ValueError("Verify the full author list and Silin Meng's authorship before importing")
        for author in authors:
            text(author)
        safe_url(paper["url"])
        if "project_url" in paper:
            safe_url(paper["project_url"])
        if not paper.get("evidence"):
            raise ValueError("Every publication needs a supporting source")
        for source_url in paper["evidence"]:
            safe_url(source_url)


def experience_digest(profile):
    content = {key: profile[key] for key in ('headline', 'summary', 'experience')}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def validate_profile(profile):
    if profile.get("schema_version") != 1 or profile.get("name") != "Silin Meng":
        raise ValueError("Unexpected profile")
    approval = profile.get("experience_approval", {})
    if approval.get("status") != "approved":
        raise ValueError("Work experience must be approved before publication")
    if approval.get("sha256") != experience_digest(profile):
        raise ValueError("Work experience has changed since the user's approval; request confirmation first")
    date.fromisoformat(approval["approved_on"])
    for link in profile["links"].values():
        safe_url(link)
    safe_url(profile["source_url"])
    if not re.fullmatch(r"[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", profile["email"]):
        raise ValueError("Invalid contact email")
    for entry in profile["experience"] + profile["education"]:
        for field in ("start", "end"):
            if entry[field] is not None:
                if not re.fullmatch(r"\d{4}-\d{2}", entry[field]):
                    raise ValueError("Dates must use YYYY-MM")
                date.fromisoformat(entry[field] + "-01")
        if not entry["start"] or (entry["end"] and entry["start"] > entry["end"]):
            raise ValueError("Invalid experience or education date range")


def dates(entry):
    def month(value):
        return date.fromisoformat(value + "-01").strftime("%b %Y") if value else "Present"
    return f'{month(entry["start"])} – {month(entry["end"])}'


def experience_html(profile, cv=False):
    entries = []
    for entry in profile["experience"]:
        entries.append(f'''<li class="experience-item">
          <div class="experience-title"><h3>{text(entry['organization'])}</h3><span class="date-range">{dates(entry)}</span></div>
          <p>{text(entry['role'])}</p>
        </li>''')
    return '<ul class="experience-list">' + "\n".join(entries) + '</ul>'


def education_html(profile):
    return '<ul class="education-list">' + "\n".join(
        f'''<li><div class="experience-title"><h3>{text(entry['organization'])}</h3><span class="date-range">{dates(entry)}</span></div>
        <p>{text(entry['degree'])}</p></li>''' for entry in profile["education"]
    ) + '</ul>'


def papers_html(data, cv=False):
    entries = []
    for paper in sorted(data["publications"], key=lambda p: -p["year"]):
        authors = ''
        if cv:
            names = ', '.join(f'<strong>{text(a)}</strong>' if a == 'Silin Meng' else text(a) for a in paper['authors'])
            authors = f'<p class="authors">{names}</p>'
        entries.append(f'''<li class="publication">
          <h3 class="paper-title"><a href="{safe_url(paper['url'])}">{text(paper['title'])} {ARROW}</a></h3>
          {authors}
          <p class="publication-meta">{text(paper['venue'])} <span aria-hidden="true">·</span> <time datetime="{paper['year']}">{paper['year']}</time></p>
        </li>''')
    return '<ol class="publication-list">' + '\n'.join(entries) + '</ol>'


def section(title, identity, number, content, extra=''):
    return f'''<section class="section" id="{identity}" tabindex="-1" aria-labelledby="{identity}-title">
      <div class="section-heading"><h2 id="{identity}-title">{title}</h2><span class="section-number" aria-hidden="true">{number}</span></div>
      {content}{extra}
    </section>'''


def asset_url(root, relative):
    version = hashlib.sha256((root / relative).read_bytes()).hexdigest()[:12]
    return f'./{relative}?v={version}'


def render(root=ROOT):
    profile = json.loads((root / 'data/profile.json').read_text())
    publications = json.loads((root / 'data/publications.json').read_text())
    validate_profile(profile)
    validate_publications(publications)
    links = profile['links']
    profile_links = '<nav class="profile-links" aria-label="Find me online">' + ''.join(
        f'<a href="{safe_url(links[key])}">{label} {ARROW}</a>'
        for key, label in [('scholar', 'Scholar'), ('github', 'GitHub'), ('linkedin', 'LinkedIn')]
    ) + '<a href="./cv.html">CV <span aria-hidden="true">↗</span></a></nav>'
    research_source = f'<p class="source-link"><a href="{safe_url(publications["source_url"])}">Google Scholar {ARROW}</a></p>'
    index = Template((root / 'templates/index.html').read_text()).substitute(
        main_css=asset_url(root, 'dist/css/main.css'),
        email=text(profile['email']), description=text(profile['summary']),
        intro=f'<p class="intro-note">{text(profile["headline"])}<br />{text(profile["focus"])}</p>',
        profile_links=profile_links,
        experience=section('Experience', 'experience', '01', experience_html(profile)),
        research=section('Research', 'research', '02', papers_html(publications), research_source),
        education=section('Education', 'education', '04', education_html(profile)),
    )
    cv = Template((root / 'templates/cv.html').read_text()).substitute(
        main_css=asset_url(root, 'dist/css/main.css'),
        cv_css=asset_url(root, 'dist/css/cv.css'),
        cv_js=asset_url(root, 'dist/js/cv.js'),
        name=text(profile['name']), email=text(profile['email']), summary=text(profile['summary']),
        linkedin=safe_url(links['linkedin']), scholar=safe_url(links['scholar']), github=safe_url(links['github']),
        experience=experience_html(profile, cv=True),
        education=education_html(profile), publications=papers_html(publications, cv=True),
        verified_on=text(publications['verified_on']),
    )
    # Both documents are fully rendered and validated before either output changes.
    for filename, content in [('index.html', index), ('cv.html', cv)]:
        target = root / filename
        temporary = target.with_suffix('.html.tmp')
        temporary.write_text('\n'.join(line.rstrip() for line in content.splitlines()) + '\n')
        temporary.replace(target)
    print(f"Rendered homepage and CV with {len(publications['publications'])} papers and {len(profile['experience'])} approved roles.")


if __name__ == '__main__':
    render()
