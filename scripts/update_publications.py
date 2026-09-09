"""Import a source-verified Scholar snapshot without deleting cached papers.

This command performs no scraping. A scheduled Codex task reads the specified
public profile and supplies a verified snapshot. Failed reads never touch data.
"""

import argparse
from copy import deepcopy
import json
from pathlib import Path

from render_site import ROOT, validate_publications


def merge_publications(current, incoming):
    validate_publications(current)
    validate_publications(incoming)
    if incoming['verified_on'] < current['verified_on']:
        raise ValueError('Refusing an older snapshot')
    papers = {paper['id']: deepcopy(paper) for paper in current['publications']}
    for paper in incoming['publications']:
        papers[paper['id']] = deepcopy(paper)
    merged = deepcopy(current)
    merged['publications'] = sorted(papers.values(), key=lambda paper: (-paper['year'], paper['id']))
    validate_publications(merged)
    before = {p['id']: p for p in current['publications']}
    after = {p['id']: p for p in merged['publications']}
    if before == after:
        # No empty weekly commits or deployments for a check with no changes.
        return deepcopy(current)
    merged['verified_on'] = incoming['verified_on']
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path, help='Verified Scholar snapshot JSON')
    args = parser.parse_args()
    target = ROOT / 'data/publications.json'
    current = json.loads(target.read_text())
    incoming = json.loads(args.snapshot.read_text())
    merged = merge_publications(current, incoming)
    if merged == current:
        print('No publication changes; saved data left unchanged.')
        return
    temporary = target.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(target)
    print(f"Saved {len(merged['publications'])} publications. Work experience was not changed.")


if __name__ == '__main__':
    main()
