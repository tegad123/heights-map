"""Review or surgically fill unclassified DATA fields from an evidence snapshot.

No network access. Input baseline is a browser capture including stored DATA and
runtime product values; parcel matches are exact-address HCAD features. Preview
is the default. Existing recognized products and runtime tag labels are protected.
"""
import argparse
import collections
import json
from pathlib import Path
from permit_pull import extract_data
from product_classification import classify, context_signals, parcel_evidence, stored_product, record_fields


def decisions(baseline, matches, holds):
    output = {}
    for market, capture in baseline.items():
        context = context_signals(capture['source'])
        runtime = {r['id']:r for r in capture['rows']}
        for r in capture['rows']:
            for twin in r.get('twins',[]):
                runtime[twin['id']] = dict(product=stored_product(twin), **{'raw':twin})
        reviewed = []
        for row in capture['source']:
            if row['id'] not in runtime:
                continue
            features = matches.get(market,{}).get(row['id'],[])
            if len(features) == 1:
                parcel = parcel_evidence(features[0], 'HCAD unique exact-address polygon')
            else:
                parcel = {'source':'unavailable' if not features else 'ambiguous exact-address accounts',
                          'geometry_error':'no exact-address match' if not features else 'multiple parcel accounts'}
            hold = holds.get(market,{}).get(row['id'])
            decision = classify(legal=parcel.get('legal',''), parcel=parcel,
                                hold=json.dumps(hold,sort_keys=True) if hold else None,
                                **context[row['id']])
            current = stored_product(row) or runtime[row['id']].get('product')
            reviewed.append(dict(id=row['id'], address=row['a'], stored=current,
                                 eligible=not current, decision=decision))
        output[market] = reviewed
    return output


def splice(html, updates):
    """Insert fields before each object's final brace; retain all original bytes."""
    start,end,rows = extract_data(html)
    decoder = json.JSONDecoder()
    pos = start + 1
    changes = []
    for row in rows:
        while html[pos].isspace() or html[pos] == ',':
            pos += 1
        value, stop = decoder.raw_decode(html,pos)
        assert value == row
        fields = updates.get(row['id'])
        if fields:
            assert not stored_product(row), row['id']
            # Explicitly protect even unrecognized preexisting prod/ty fields.
            assert 'ty' not in row and 'prod' not in row, row['id']
            assert 'product_classification' not in row
            insertion = ', ' + json.dumps(fields, separators=(', ', ': '))[1:-1]
            assert html[stop-1] == '}'
            changes.append((stop-1,insertion))
        pos = stop
    for pos,insertion in reversed(changes):
        html = html[:pos] + insertion + html[pos:]
    _,_,after = extract_data(html)
    assert len(after) == len(rows)
    for before,new in zip(rows,after):
        assert new == dict(before, **updates.get(before['id'],{}))
    return html, len(changes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    baseline = json.loads((args.evidence/'baseline.json').read_text())
    matches = json.loads((args.evidence/'parcel_matches.json').read_text())
    holds = json.loads((root/'product_classification_holds.json').read_text())
    reviewed = decisions(baseline,matches,holds)
    summary = {}
    for market, reviews in reviewed.items():
        path = root/(market+'.html')
        original = path.read_text()
        _,_,current = extract_data(original)
        byid = {r['id']:r for r in current}
        updates = {}
        unknown = [r for r in reviews if r['eligible']]
        for r in unknown:
            # Holds remain byte-for-byte untouched, with reasons in the ledger.
            if r['decision']['reason_code'] == 'HELD_TRIAGE':
                continue
            fields = record_fields(r['decision'])
            saved = byid[r['id']]
            if all(saved.get(k) == v for k,v in fields.items()):
                continue
            if 'prod' in saved or 'ty' in saved or 'product_classification' in saved:
                raise ValueError(f'existing assignment changed since baseline: {market}/{r["id"]}')
            updates[r['id']] = fields
        edited,touched = splice(original,updates)
        summary[market] = dict(before_unknown=len(unknown),
            product=dict(collections.Counter(r['decision']['product'] for r in unknown)),
            confidence=dict(collections.Counter(r['decision']['confidence'] for r in unknown)),
            remaining_reasons=dict(collections.Counter(r['decision']['reason_code'] for r in unknown if r['decision']['product']=='Unknown')),
            touched=touched, existing_protected=sum(not r['eligible'] for r in reviews))
        if args.apply and edited != original:
            path.write_text(edited)
        print(market,json.dumps(summary[market],sort_keys=True))
    (args.evidence/'decisions.json').write_text(json.dumps(reviewed,indent=2)+'\n')
    (args.evidence/'backfill_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('APPLIED' if args.apply else 'PREVIEW: no HTML writes')


if __name__ == '__main__':
    main()
