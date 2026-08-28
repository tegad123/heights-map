#!/usr/bin/env python3
"""Sold-data staleness check — rides the Sunday weekly ingest report.

Per enabled market, find the newest sale date: SOLD_METRICS['as_of'] for
heights, else the max date-shaped `sd` in the page's DATA array. Markets
whose newest sale is older than SOLD_STALE_DAYS (default 21) are listed on
one reminder line to stdout; prints nothing when everything is fresh.
Exit 0 always — a staleness reminder must never fail the ingest run.
"""
import json, os, re, sys
from datetime import date

REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
from market_config import MARKETS, INGEST_ORDER

STALE_DAYS = int(os.environ.get('SOLD_STALE_DAYS', '21'))
DATE = re.compile(r'^20\d\d-\d\d-\d\d$')


def newest_sale(mk, cfg):
    html = open(os.path.join(REPO, cfg['html']), encoding='utf-8').read()
    if mk == 'heights':
        m = re.search(r'SOLD_METRICS\s*=\s*\{', html)
        if m:
            try:
                obj, _ = json.JSONDecoder().raw_decode(html, m.end() - 1)
                if DATE.match(str(obj.get('as_of', ''))):
                    return obj['as_of']
            except ValueError:
                pass
        return None
    m = re.search(r'\bDATA\s*=\s*\[', html)
    if not m:
        return None
    try:
        data, _ = json.JSONDecoder().raw_decode(html, m.end() - 1)
    except ValueError:
        return None
    ds = sorted(str(r.get('sd')) for r in data if DATE.match(str(r.get('sd', ''))))
    return ds[-1] if ds else None


def main():
    today = date.today()
    due = []
    for mk in INGEST_ORDER:
        cfg = MARKETS[mk]
        if not cfg['enabled']:
            continue
        ns = newest_sale(mk, cfg)
        if ns is None:
            due.append(f'{mk} (none)')
        elif (today - date.fromisoformat(ns)).days > STALE_DAYS:
            due.append(f'{mk} ({ns})')
    if due:
        print(f'⚠ HAR sold-comps pull due: {", ".join(due)} — newest sale per '
              f'market in (), threshold {STALE_DAYS}d')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:                          # never break the report
        print(f'(sold-staleness check errored: {e})')
    sys.exit(0)
