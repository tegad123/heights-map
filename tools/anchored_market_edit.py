"""Apply identical unique code replacements to eight hand-authored market pages.

Extends the prior /tmp/heights_g6.py pattern: preflight every market, retain
exact JSON payload bytes, then write. No HTML or embedded data regeneration.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETS = ['index.html','montrose.html','riveroaks.html','springbranch.html',
           'springvalley.html','timbergrove.html','westu.html','gardenoaksoakforest.html']


def protected(source):
    blocks = {}
    for name in ['DATA','SOLD_DATA','SOLD_METRICS','SEED_POINTS','LIFE','RECONCILE']:
        matches = list(re.finditer(r'\b(?:const|let) '+name+r'\s*=\s*', source))
        if not matches:
            continue
        if len(matches) != 1:
            raise ValueError('Ambiguous data declaration: '+name)
        start = matches[0].end()
        _, length = json.JSONDecoder().raw_decode(source[start:])
        blocks[name] = source[start:start+length]
    return blocks


def apply(replacements):
    prepared = {}
    for name in MARKETS:
        path = ROOT/name
        source = path.read_text()
        candidate = source
        for old, new in replacements:
            old = old[name] if isinstance(old, dict) else old
            new = new[name] if isinstance(new, dict) else new
            if candidate.count(old) != 1:
                raise ValueError(f'{name}: expected one anchor, got {candidate.count(old)}: {old[:90]}')
            candidate = candidate.replace(old, new, 1)
        if protected(source) != protected(candidate):
            raise ValueError(name+': embedded data changed')
        prepared[path] = candidate
    for path, candidate in prepared.items():
        path.write_text(candidate)
        print(f'{path.name}: {len(replacements)} anchored edits; protected JSON byte-identical')
