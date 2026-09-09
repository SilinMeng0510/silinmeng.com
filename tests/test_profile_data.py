from copy import deepcopy
import json
from pathlib import Path
import re
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from render_site import papers_html, render, safe_url, validate_profile, validate_publications
from update_publications import merge_publications


class ProfileDataTests(unittest.TestCase):
    def setUp(self):
        self.papers = json.loads((ROOT / 'data/publications.json').read_text())
        self.profile = json.loads((ROOT / 'data/profile.json').read_text())

    def test_partial_snapshot_preserves_missing_papers(self):
        incoming = deepcopy(self.papers)
        incoming['publications'] = incoming['publications'][:1]
        incoming['publications'][0]['venue'] = 'A newly verified venue'
        merged = merge_publications(self.papers, incoming)
        self.assertEqual(len(merged['publications']), len(self.papers['publications']))
        self.assertEqual(next(p for p in merged['publications'] if p['id'] == incoming['publications'][0]['id'])['venue'], 'A newly verified venue')
        self.assertNotEqual(self.papers['publications'][0]['venue'], 'A newly verified venue')

    def test_empty_fetch_does_not_erase_snapshot(self):
        incoming = deepcopy(self.papers)
        incoming['publications'] = []
        with self.assertRaises(ValueError):
            merge_publications(self.papers, incoming)

    def test_no_changes_do_not_update_only_timestamp(self):
        older = deepcopy(self.papers)
        older['verified_on'] = '2026-09-08'
        incoming = deepcopy(self.papers)
        self.assertEqual(merge_publications(older, incoming), older)

    def test_old_snapshot_rejected(self):
        incoming = deepcopy(self.papers)
        incoming['verified_on'] = '2026-09-08'
        with self.assertRaises(ValueError):
            merge_publications(self.papers, incoming)

    def test_other_scholar_profile_rejected(self):
        incoming = deepcopy(self.papers)
        incoming['source_url'] = 'https://scholar.google.com/citations?user=someone_else'
        with self.assertRaises(ValueError):
            validate_publications(incoming)

    def test_ambiguous_authorship_rejected(self):
        incoming = deepcopy(self.papers)
        incoming['publications'][0]['authors'] = ['Someone Else']
        with self.assertRaises(ValueError):
            validate_publications(incoming)

    def test_duplicate_title_with_new_scholar_id_rejected(self):
        incoming = deepcopy(self.papers)
        duplicate = deepcopy(incoming['publications'][0])
        duplicate['id'] = 'wJdoPLsAAAAJ:duplicate'
        incoming['publications'].append(duplicate)
        with self.assertRaises(ValueError):
            validate_publications(incoming)

    def test_unsafe_url_rejected(self):
        for url in ('javascript:alert(1)', '//example.com', 'https://user:password@example.com', 'https://example.com/\nattack'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                safe_url(url)

    def test_external_text_is_escaped(self):
        incoming = deepcopy(self.papers)
        incoming['publications'][0]['title'] = '<script>alert("title")</script>'
        rendered = papers_html(incoming)
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_career_changes_require_fresh_user_approval(self):
        validate_profile(self.profile)
        self.profile['experience'][0]['role'] = 'Unapproved new title'
        with self.assertRaisesRegex(ValueError, 'approval'):
            validate_profile(self.profile)

    def test_unapproved_profile_cannot_render(self):
        self.profile['experience_approval']['status'] = 'pending'
        with self.assertRaises(ValueError):
            validate_profile(self.profile)

    def test_css_changes_refresh_both_pages_without_churning_other_assets(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ('data', 'templates', 'dist'):
                shutil.copytree(ROOT / folder, root / folder)
            render(root)

            def assets(page):
                return re.findall(r'(?:href|src)="(\./dist/[^\"]+)"', (root / page).read_text())

            before = {page: assets(page) for page in ('index.html', 'cv.html')}
            self.assertIn('?v=', before['index.html'][0])
            render(root)
            self.assertEqual(before, {page: assets(page) for page in before})
            stylesheet = root / 'dist/css/main.css'
            stylesheet.write_text(stylesheet.read_text() + '\n/* A new stylesheet release. */\n')
            render(root)
            self.assertNotEqual(before['index.html'][0], assets('index.html')[0])
            self.assertEqual(assets('index.html')[0], assets('cv.html')[0])
            self.assertEqual(before['cv.html'][1:], assets('cv.html')[1:])


if __name__ == '__main__':
    unittest.main()
