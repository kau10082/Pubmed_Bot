"""
SCImago Journal Rank (SJR) quartile lookup for Branch C filtering.

Loads the official SCImago CSV (semicolon-delimited; download once a year from
https://www.scimagojr.com/journalrank.php -> "Download data" -> save as data/scimago.csv)
and resolves a journal's quartile by ISSN, honoring axis-specific categories with a
best-quartile fallback.

CSV columns of interest (header names as published by SCImago):
  - "Issn"             : ISSNs without hyphens, comma-separated, e.g. "00031305, 15372731"
  - "SJR Best Quartile": e.g. "Q1"
  - "Categories"       : e.g. "Critical Care... (Q1); Pulmonary and Respiratory Medicine (Q2)"
  - "Title"            : journal title
"""

import csv
import gzip
import os
import re

_CATEGORY_RE = re.compile(r'^\s*(.*?)\s*\((Q[1-4])\)\s*$')


def _norm_issn(raw):
    """Normalize an ISSN to 8 alphanumerics (digits + trailing X), uppercase, no hyphen."""
    return re.sub(r'[^0-9Xx]', '', raw or '').upper()


def _parse_categories(cell):
    """'Foo (Q1); Bar (Q2)' -> {'foo': 'Q1', 'bar': 'Q2'} (keys lowercased)."""
    cats = {}
    for part in (cell or '').split(';'):
        m = _CATEGORY_RE.match(part)
        if m:
            cats[m.group(1).strip().lower()] = m.group(2)
    return cats


class SJRIndex:
    def __init__(self):
        self.by_issn = {}   # normalized ISSN -> {'best': 'Q1', 'cats': {cat: 'Qn'}, 'title': str}
        self.loaded = False

    def load(self, path):
        if not path or not os.path.exists(path):
            print(f"[SJR] Index file not found ({path}). SJR filtering DISABLED (all journals pass).")
            return self
        try:
            opener = gzip.open if path.endswith('.gz') else open
            with opener(path, mode='rt', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    entry = {
                        'best': (row.get('SJR Best Quartile') or '').strip(),
                        'cats': _parse_categories(row.get('Categories') or ''),
                        'title': (row.get('Title') or '').strip(),
                    }
                    for raw in (row.get('Issn') or '').split(','):
                        issn = _norm_issn(raw)
                        if len(issn) == 8:
                            self.by_issn[issn] = entry
            self.loaded = True
            print(f"[SJR] Loaded {len(self.by_issn)} ISSN entries from {path}")
        except Exception as e:
            print(f"[SJR] Failed to load index: {e}. SJR filtering DISABLED (all journals pass).")
        return self

    def _entry_for(self, issns):
        for issn in issns or []:
            entry = self.by_issn.get(_norm_issn(issn))
            if entry:
                return entry
        return None

    def lookup(self, issns, axis_categories):
        """
        Resolve a journal's quartile.

        issns:           list of ISSN strings from PubMed (any format)
        axis_categories: list of SCImago category names (any case) for the article's matched axes

        Returns a dict:
          {'status': 'indexed', 'q': 'Q1', 'category': '<cat>'|'best-Q fallback',
           'fallback': bool, 'title': str}   when found in SJR
          {'status': 'unindexed'}            when the journal is not in the SJR table
          {'status': 'disabled'}             when no index is loaded (filter off)
        """
        if not self.loaded:
            return {'status': 'disabled'}

        entry = self._entry_for(issns)
        if not entry:
            return {'status': 'unindexed'}

        wanted = [c.strip().lower() for c in (axis_categories or [])]
        matched = [(entry['cats'][c], c) for c in wanted if c in entry['cats']]
        if matched:
            q, cat = min(matched, key=lambda x: int(x[0][1]))  # best (lowest) quartile number
            return {'status': 'indexed', 'q': q, 'category': cat,
                    'fallback': False, 'title': entry['title']}

        if entry['best']:
            return {'status': 'indexed', 'q': entry['best'], 'category': 'best-Q fallback',
                    'fallback': True, 'title': entry['title']}

        return {'status': 'unindexed'}


def quartile_rank(q):
    """'Q1' -> 1 ... 'Q4' -> 4; None/invalid -> 99."""
    if q and len(q) == 2 and q[0] == 'Q' and q[1].isdigit():
        return int(q[1])
    return 99
