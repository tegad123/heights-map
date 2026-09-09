#!/usr/bin/env python3
"""Dated HAR market evidence and read-only construction reconciliation.

Dry run by default. --apply writes a separate snapshot, audit, dropped ledger,
and SOLD_DATA/SOLD_METRICS only. DATA and RECONCILE remain byte-identical.
Runtime capture must come from tests/timeline_browser.py with raw/points added.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from active_ingest import address_key
from deed_ingest import span, encode, in_boundary
from sold_classification import classify_lot
from sold_ingest import money, parse_close, refresh_derived, metrics_for, OPTIONAL, TEXT

ROOT = Path(__file__).resolve().parent
AS_OF = '2026-09-09'
INPUTS = [
    ('heightsactivesinglelots909.csv', 'active', 'Single Lot'),
    ('heightsactivesplitlots909.csv', 'active', 'Split Lot'),
    ('heightspendingsinglelots909.csv', 'pending', 'Single Lot'),
    ('heightspendingsplitlots909.csv', 'pending', 'Split Lot'),
    ('heightssoldsinglelotslast180days.csv', 'sold', 'Single Lot'),
    ('heightssoldsplitlotslast180days.csv', 'sold', 'Split Lot'),
]


def jsontxt(value):
    return json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n'


def csvtxt(rows, fields):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def load_inputs(html):
    zone = re.compile(re.search(r'const OUT_OF_ZONE=/(.*?)/i;', html)[1], re.I)
    boundary = json.loads((ROOT / 'heights_boundary.geojson').read_text())
    records, ledger, summaries = [], [], []
    seen = set()
    seen_properties = set()
    for filename, status, expected in INPUTS:
        payload = (ROOT / filename).read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        reader = csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))
        required = {'MLS Number', 'Address', 'Lot Size', 'Longitude', 'Latitude',
                    'Original List Price', 'Close Price', 'Close Date', 'DOM',
                    'Builder Name', 'Year Built', 'Building SqFt'} | set(TEXT.values()) | set(OPTIONAL.values())
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('Missing columns: ' + filename)
        rows = list(reader)
        if not rows:
            raise ValueError('Empty input: ' + filename)
        summary = dict(file=filename, sha256=digest, read=len(rows), accepted=0,
                       classification_matches=0, excluded=Counter())
        for line, raw in enumerate(rows, 2):
            lot = money(raw['Lot Size'])
            product = classify_lot(lot)
            if product != expected:
                raise ValueError(f'Lot classification mismatch: {filename}:{line}')
            summary['classification_matches'] += 1
            mls, address = raw['MLS Number'].strip(), raw['Address'].strip()
            lat, lng = money(raw['Latitude']), money(raw['Longitude'])
            close = parse_close(raw['Close Date'])
            key = address_key(address)
            reason = None
            if not mls or not address or lat is None or lng is None or not (-90 <= lat <= 90 and -180 <= lng <= 180):
                raise ValueError(f'Invalid identity/coordinates: {filename}:{line}')
            if money(raw['Original List Price']) is None or money(raw['DOM']) is None:
                raise ValueError(f'Missing numeric evidence: {filename}:{line}')
            if status == 'sold' and (not close or close > date.fromisoformat(AS_OF) or not money(raw['Close Price'])):
                raise ValueError(f'Invalid closing: {filename}:{line}')
            if status != 'sold' and (close or raw['Close Price'].strip()):
                raise ValueError(f'Unexpected closing in {status}: {filename}:{line}')
            if zone.search(address): reason = 'OOZ_REGEX'
            elif lng > -95.370: reason = 'OOZ_EAST'
            elif not in_boundary(boundary, lng, lat): reason = 'OOZ_POLY'
            identity = (mls, status, close.isoformat() if close else '')
            property_identity = (key, status, close.isoformat() if close else '')
            if identity in seen: reason = 'DUP_INPUT'
            elif property_identity in seen_properties: reason = 'DUP_PROPERTY_STATUS'
            seen.add(identity)
            seen_properties.add(property_identity)
            rec = dict(mls=mls, status=status, address=address, address_key=key,
                       original_list_price=money(raw['Original List Price']),
                       current_list_price=None, close_price=money(raw['Close Price']),
                       close_date=close.isoformat() if close else None,
                       dom=money(raw['DOM']), lot_sqft=lot, product=product,
                       builder=raw['Builder Name'], year_built=money(raw['Year Built']),
                       building_sqft=money(raw['Building SqFt']), lat=lat, lng=lng,
                       agents={k: v for k, v in raw.items() if 'Agent' in k or 'Office' in k or 'Team' in k},
                       as_of=AS_OF, source_file=filename, source_row=line,
                       source_sha256=digest, exclusion=reason, raw=raw)
            records.append(rec)
            if reason:
                summary['excluded'][reason] += 1
                ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls,
                                   ADDRESS=address, REASON=reason, RAW_JSON=json.dumps(raw, sort_keys=True)))
            else: summary['accepted'] += 1
        assert summary['read'] == summary['accepted'] + sum(summary['excluded'].values())
        summaries.append(summary)
    return records, ledger, summaries


def merge_sales(existing, records):
    """Union transactions; preserve all existing resale/history records verbatim."""
    rows = json.loads(json.dumps(existing))
    updates, additions, overlaps, conflicts = [], [], [], []
    for rec in records:
        if rec['status'] != 'sold' or rec['exclusion']:
            continue
        rid = 's' + rec['mls']
        matches = [r for r in rows if r['id'] == rid]
        if not matches:
            matches = [r for r in rows if address_key(r['a']) == rec['address_key'] and r['cd'] == rec['close_date']]
        if len(matches) > 1:
            conflicts.append(dict(mls=rec['mls'], reason='AMBIGUOUS_EXISTING_CLOSING'))
            continue
        if matches:
            old = matches[0]
            if old['cd'] != rec['close_date'] or address_key(old['a']) != rec['address_key']:
                conflicts.append(dict(mls=rec['mls'], reason='MLS_IDENTITY_CONFLICT'))
                continue
            overlaps.append(rec['mls'])
            # Refresh source facts, retaining legacy fields and transaction identity.
            row = dict(old)
        else: row = dict(id=rid)
        raw = rec['raw']
        row.update(a=rec['address'], lat=round(rec['lat'], 7), lng=round(rec['lng'], 7),
                   cp=rec['close_price'], sq=rec['building_sqft'], cd=rec['close_date'],
                   psf=round(rec['close_price'] / rec['building_sqft'], 1) if rec['building_sqft'] else None)
        row.update({k: money(raw[v]) for k, v in OPTIONAL.items()})
        row.update({k: raw[v].strip() for k, v in TEXT.items()})
        row['coh'] = 'nc' if rec['year_built'] and rec['year_built'] >= 2025 else 'resale'
        if row.get('lp'): row['svl'] = round((row['cp'] - row['lp']) / row['lp'], 4)
        if row.get('dom') == 0: row['p'] = 1
        else: row.pop('p', None)
        row = refresh_derived([row], date.fromisoformat(AS_OF))[0]
        if matches:
            # Window aging alone must not rewrite historical sales.
            if all(old.get(k) == v for k, v in row.items() if k != 'win'):
                continue
            rows[rows.index(old)] = row
            updates.append(rec['mls'])
        else:
            rows.append(row)
            additions.append(rec['mls'])
    assert {r['id'] for r in existing}.issubset({r['id'] for r in rows})
    assert len({r['id'] for r in rows}) == len(rows)
    return rows, dict(added=additions, updated=updates, existing_matches=overlaps, conflicts=conflicts)


def reconcile(runtime, records, sold):
    lookup = defaultdict(list)
    phases = {r['id']: r for r in runtime['rows']}
    members = []
    for pin in runtime['raw']:
        for member in [pin] + ([pin['_twin']] if pin.get('_twin') else []):
            value = (pin, member)
            lookup[address_key(member['a'])].append(value)
            members.append(value)
    fresh = defaultdict(list)
    for rec in records:
        if not rec['exclusion']: fresh[rec['address_key']].append(rec)
    sold_by_address = defaultdict(list)
    for sale in sold: sold_by_address[address_key(sale['a'])].append(sale)

    def evidence(key):
        rr = fresh[key]
        current = [r for r in rr if r['status'] in ('active', 'pending')]
        statuses = set(r['status'] for r in current)
        if len(statuses) > 1: return 'conflict', rr
        if current: return current[0]['status'], rr
        if any(r['status'] == 'sold' for r in rr) or any(s.get('yb', 0) and s['yb'] >= 2025 for s in sold_by_address[key]): return 'sold', rr
        return 'no market record', rr

    classes = {k: [] for k in 'ABCDEFGH'}
    table, complete = [], []
    def prior(member):
        return runtime['points'].get(member['id'], {}).get('tags', [])
    def detail(pin, member):
        key = address_key(member['a'])
        status, rr = evidence(key)
        sales = sorted(sold_by_address[key], key=lambda r: r['cd'], reverse=True)
        phase = phases[pin['id']]['phase']
        tags = prior(member)
        flags = []
        if phase == 'complete': flags.append({'sold': 'A', 'active': 'B', 'pending': 'C', 'no market record': 'D'}.get(status, 'CONFLICT'))
        elif phase and status == 'sold': flags.append('E')
        tagstatus = set()
        if any(t in tags for t in ['market', 'active_single', 'active_split', 'listed']): tagstatus.add('active')
        if 'pending' in tags: tagstatus.add('pending')
        if any(t.startswith('off_market') for t in tags): tagstatus.add('off market')
        if status != 'no market record' and tagstatus - {status}: flags.append('F')
        if phase and phase != 'complete' and status == 'active': flags.append('H')
        return dict(address=member['a'], MLS=', '.join(sorted({r['mls'] for r in rr})) or (sales[0]['id'][1:] if sales else ''),
                    construction_phase=phase, current_market_status=status,
                    prior_stored_tag=tags, conflict_class=flags, pin=pin['id'], member=member['id'],
                    phase_scope='paired project' if pin.get('_twin') else 'property',
                    historical_sales=[dict(MLS=s['id'][1:], close_date=s['cd'], close_price=s['cp'], year_built=s.get('yb'), evidence_scope='new-construction closing' if s.get('yb', 0) and s['yb'] >= 2025 else 'prior-structure resale; not current build sold') for s in sales],
                    in_current_supply=pin['id'] in runtime['supplyIds'])
    for pin, member in members:
        row = detail(pin, member)
        table.append(row)
        for k in row['conflict_class']:
            if k in classes: classes[k].append(row)
        if row['construction_phase'] == 'complete': complete.append(row)
    # Explicitly account for home weights exceeding named members; do not invent addresses/status.
    for pin in runtime['raw']:
        n = phases[pin['id']]['weight'] - (2 if pin.get('_twin') else 1)
        if phases[pin['id']]['phase'] == 'complete':
            for i in range(max(0, n)):
                row = dict(address=f'Unidentified represented home {i+1} at {pin["a"]}', MLS='', construction_phase='complete', current_market_status='no market record', prior_stored_tag=[], conflict_class=['D'], pin=pin['id'], member=None, inferred_weight=True)
                complete.append(row); classes['D'].append(row)
    source_table = []
    for rec in records:
        matches = lookup[rec['address_key']]
        row = dict(address=rec['address'], MLS=rec['mls'], source_file=rec['source_file'], source_status=rec['status'],
                   construction_phase='; '.join(sorted({phases[p['id']]['phase'] or 'no evidenced phase' for p, m in matches})) or 'untracked',
                   current_market_status=evidence(rec['address_key'])[0] if not rec['exclusion'] else 'excluded from Heights',
                   prior_stored_tag=sorted({t for p, m in matches for t in prior(m)}),
                   conflict_class=sorted({k for p, m in matches for k in detail(p, m)['conflict_class']}),
                   matches=[dict(pin=p['id'], member=m['id'], construction_phase=phases[p['id']]['phase']) for p, m in matches], exclusion=rec['exclusion'])
        if not matches or not any(phases[p['id']]['phase'] for p, m in matches):
            assessment = 'Out of Heights zone; not a coverage gap' if rec['exclusion'] else 'Recent-build construction coverage gap' if rec['year_built'] and rec['year_built'] >= 2025 else 'Resale candidate; year built predates 2025, construction linkage unverified'
            gap = dict(**row, assessment=assessment, year_built=rec['year_built'])
            classes['G'].append(gap)
            row['conflict_class'] = sorted(set(row['conflict_class']) | {'G'})
        source_table.append(row)
    old = [r for f in ['heights_active_single_lots0908.csv', 'heights_active_split_lots0908.csv'] for r in csv.DictReader((ROOT / f).open(encoding='utf-8-sig'))]
    active_ids = {r['mls'] for r in records if r['status'] == 'active'}
    delta = []
    for rec in old:
        if rec['MLS Number'] not in active_ids:
            status, rr = evidence(address_key(rec['Address']))
            delta.append(dict(address=rec['Address'], MLS=rec['MLS Number'], disposition=status if status in ('sold', 'pending') else 'unconfirmed; absence does not establish off-market', evidence_mls=[r['mls'] for r in rr]))
    counts = Counter(r['current_market_status'] for r in complete)
    assert len(complete) == runtime['columns']['complete'], (len(complete), runtime['columns']['complete'])
    removed_building = [r for r in table if r['in_current_supply'] and r['current_market_status'] in ('sold', 'pending')]
    # Complete is currently outside comingOnline; A and C subtraction is necessarily zero.
    # Scenario follows requested B+D convention; D availability remains unverified.
    impact = dict(current=runtime['supply'], A_total=len(classes['A']), A_current_supply=sum(r.get('in_current_supply', False) for r in classes['A']),
                  C_total=len(classes['C']), C_current_supply=sum(r.get('in_current_supply', False) for r in classes['C']),
                  B_added=counts['active'], D_added=counts['no market record'],
                  requested_result=runtime['supply'] + counts['active'] + counts['no market record'],
                  additional_known_unavailable_members=len(removed_building),
                  availability_scenario_including_building_exclusions=runtime['supply'] + counts['active'] + counts['no market record'] - len(removed_building),
                  pending_or_sold_under_construction_in_current_supply=removed_building,
                  caveat='D means no matching evidence in finite exports/archive, NOT verified unlisted or unsold. B+D is a requested scenario, not confirmed availability. Paired construction evidence is not per-unit certification.')
    return dict(source_table=source_table, tracked_table=table, classes=classes, complete=complete,
                historical_resale_matches=[r for r in table if r['construction_phase'] and r['construction_phase'] != 'complete' and r['historical_sales'] and r['current_market_status'] == 'no market record'],
                complete_counts=dict(counts), supply_impact=impact, active_delta=delta,
                match_rate=dict(total=len(records), unique_pin=sum(len(r['matches']) == 1 for r in source_table),
                                with_phase=sum(any(m['construction_phase'] for m in r['matches']) for r in source_table)),
                display_decision='DEFER: only 3/48 sold rows have a construction phase; 34 have no tracked pin. No cross-market exports supplied. Resolve construction linkage before Phase 4.')


def run(args):
    html = (ROOT / 'index.html').read_text()
    capture = json.loads(Path(args.runtime).read_text())
    runtime = capture.get('index', capture.get('runtime'))
    if runtime is None: raise ValueError('Runtime capture missing')
    records, ledger, summaries = load_inputs(html)
    existing = span(html, 'SOLD_DATA')[2]
    sold, sold_merge = merge_sales(existing, records)
    if sold_merge['conflicts']:
        raise ValueError('Sold identity conflicts require review: ' + json.dumps(sold_merge['conflicts']))
    oldpath = ROOT / 'heights_market_status.data.json'
    old = json.loads(oldpath.read_text())['records'] if oldpath.exists() else []
    oldidx = {(r['mls'], r['status'], r['close_date']): r for r in old}
    accepted = [r for r in records if not r['exclusion']]
    for summary in summaries:
        summary.update(added=0, updated=0, unchanged=0)
        for rec in accepted:
            if rec['source_file'] != summary['file']: continue
            prior = oldidx.get((rec['mls'], rec['status'], rec['close_date']))
            summary['unchanged' if prior == rec else 'updated' if prior else 'added'] += 1
    status_conflicts = []
    for key in sorted({r['address_key'] for r in accepted}):
        rr = [r for r in accepted if r['address_key'] == key]
        if {'active', 'pending'}.issubset({r['status'] for r in rr}):
            status_conflicts.append(dict(address_key=key, records=rr))
    audit = reconcile(runtime, records, sold)
    # Stable provenance baseline lives with the snapshot for repeatable audit output.
    baseline_path = ROOT / 'docs/market-status-baseline-2026-09-09.json'
    baseline = json.loads(baseline_path.read_text()) if baseline_path.exists() else dict(sold_before=len(existing), sold_ids=[r['id'] for r in existing], runtime=runtime)
    sold30 = [r for f in ['Heightssoldsinglelotslast30days.csv', 'Heightssoldsplitlotslast30days.csv'] for r in csv.DictReader((ROOT / f).open(encoding='utf-8-sig'))]
    audit.update(as_of=AS_OF, input_rows=len(records), classification_matches=sum(s['classification_matches'] for s in summaries), status_conflicts=status_conflicts,
                 files=[{k: v for k, v in s.items() if k not in ('added', 'updated', 'unchanged')} for s in summaries],
                 sold_reconciliation=dict(before=baseline['sold_before'], after=len(sold), additions_since_baseline=[r['id'] for r in sold if r['id'] not in baseline['sold_ids']],
                                          overlap_30_vs_180=sorted({r['MLS Number'] for r in sold30} & {r['mls'] for r in records if r['status'] == 'sold'}),
                                          all_prior_ids_preserved=set(baseline['sold_ids']).issubset({r['id'] for r in sold})),
                 limitations=['Inputs total 119, not 159.', 'Current asking price is not provided: Original List Price is preserved and labeled.',
                              'APN/MLS absent from DATA; exact normalized-address joins only, no coordinate proximity inference.',
                              'No records deleted or retired; phase, tags, supply and RECONCILE unchanged.'])
    candidate = html
    for name, value in [('SOLD_DATA', sold), ('SOLD_METRICS', metrics_for(sold, date.fromisoformat(AS_OF)))]:
        start, end, prior = span(candidate, name)
        if prior != value: candidate = candidate[:start] + encode(value) + candidate[end:]
    for name in ['DATA', 'RECONCILE']:
        a, z, _ = span(html, name); c, d, _ = span(candidate, name)
        assert html[a:z] == candidate[c:d], name + ' changed'
    skeletons = []
    for body in [html, candidate]:
        for name in ['SOLD_DATA', 'SOLD_METRICS']:
            a, z, _ = span(body, name); body = body[:a] + 'null' + body[z:]
        skeletons.append(body)
    assert skeletons[0] == skeletons[1], 'Unrelated HTML changed'
    fields = ['address', 'MLS', 'construction_phase', 'current_market_status', 'prior_stored_tag', 'conflict_class']
    flat = [{k: json.dumps(r[k]) if isinstance(r[k], (list, dict)) else r[k] for k in fields} for r in audit['source_table']]
    lines = ['# Market status reconciliation — 2026-09-09', '',
             'Phase 4 deferred for construction-coverage review. Supply calculation unchanged. All six files contain **119 rows**, not 159.', '',
             'Original List Price is not current asking price. A missing market record is not proof of unsold/unlisted status. Paired phases belong to the project.', '',
             '## Input counts and sold union', '```json', jsontxt({k: audit[k] for k in ['files', 'sold_reconciliation', 'match_rate', 'active_delta', 'complete_counts', 'supply_impact']}), '```',
             '## All input rows', '| ' + ' | '.join(fields) + ' |', '|' + '|'.join(['---'] * len(fields)) + '|']
    for r in flat: lines.append('| ' + ' | '.join(str(r[k]).replace('|', '/') for k in fields) + ' |')
    labels = dict(A='Complete but sold', B='Complete but active', C='Complete but pending', D='Complete, no market record (availability unverified)', E='Under construction but sold', F='Stale tags', G='Listed/sold without tracked construction evidence', H='Under construction and active')
    for key, values in audit['classes'].items():
        lines += ['', f'## {key}. {labels[key]} — {len(values)}', '']
        lines += ['- ' + json.dumps(r, ensure_ascii=False) for r in values]
    lines += ['', '## Complete: all represented homes', '```json', jsontxt(audit['complete']), '```',
              '## Under-construction active phase distribution', '```json', jsontxt(dict(Counter(r['construction_phase'] for r in audit['classes']['H']))), '```',
              '## Historical resale matches — not current-build sold evidence', '```json', jsontxt(audit['historical_resale_matches']), '```',
              '## Review gate', audit['display_decision'], '', 'Supply scenario: 144 − 0 (A already excluded) − 0 (C already excluded) + ' + str(audit['supply_impact']['B_added']) + ' (B) + ' + str(audit['supply_impact']['D_added']) + ' (D) = ' + str(audit['supply_impact']['requested_result']) + '. D availability remains unverified. Under-construction pending/sold members are listed separately above.', '']
    outputs = {
        ROOT / 'heights_market_status.data.json': jsontxt(dict(as_of=AS_OF, price_basis='Original List Price; current asking price unavailable', records=accepted, conflicts=status_conflicts)),
        ROOT / 'docs/market-status-reconciliation-2026-09-09.json': jsontxt(audit),
        ROOT / 'docs/market-status-reconciliation-2026-09-09.csv': csvtxt(flat, fields),
        ROOT / 'docs/market-status-reconciliation-2026-09-09.md': '\n'.join(lines),
        baseline_path: jsontxt(baseline),
        ROOT / 'pulls/dropped_market_status_2026-09-09.csv': csvtxt(ledger, ['FILE', 'SHA256', 'ROW', 'MLS', 'ADDRESS', 'REASON', 'RAW_JSON']),
        ROOT / 'index.html': candidate,
    }
    changed = [str(p.relative_to(ROOT)) for p, content in outputs.items() if not p.exists() or p.read_text() != content]
    report = dict(files=summaries, rows=len(records), accepted=len(accepted), excluded=len(ledger), status_conflicts=len(status_conflicts), sold_merge=sold_merge, sold_total=len(sold), changed_files=changed, complete=audit['complete_counts'], supply=audit['supply_impact'], match_rate=audit['match_rate'])
    print(jsontxt(report))
    if args.output:
        target = Path(args.output)
        for path, content in outputs.items():
            out = target / path.relative_to(ROOT); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(content)
    if args.apply:
        for path, content in outputs.items():
            if not path.exists() or path.read_text() != content:
                path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', required=True)
    parser.add_argument('--output')
    parser.add_argument('--apply', action='store_true')
    run(parser.parse_args())
