"""One pin per address, and no two drawn markers on the same point.

Run: python3 -B -m unittest tests.test_pin_overlap
"""
import json
import unittest
from pathlib import Path

import pin_overlap
from deed_ingest import span
from market_config import MARKETS

ROOT = Path(__file__).resolve().parents[1]
OLD_SPREAD = """// spread coincident pins (e.g. units A/B/C at one address) so each is individually clickable
const dispLL={};{const grp={};for(const r of DATA){const k=r.lat.toFixed(6)+','+r.lng.toFixed(6);(grp[k]=grp[k]||[]).push(r);}
  for(const k in grp){const a=grp[k];if(a.length<2){dispLL[a[0].id]=[a[0].lat,a[0].lng];continue;}
    const rad=0.000058*(a.length>4?1.5:1),cl=Math.cos(a[0].lat*Math.PI/180)||1;
    a.forEach((r,i)=>{const ang=2*Math.PI*i/a.length;dispLL[r.id]=[r.lat+rad*Math.cos(ang),r.lng+rad*Math.sin(ang)/cl];});}}"""


def fixture_market():
    text = """let DATA = [{"id": "pmt_1-main", "a": "1 Main St", "llc": "Permit Owner", "kind": "permit", "lat": 29.7, "lng": -95.4, "permits": [{"proj": "100", "desc": "Building"}]}, {"id": "acq_1-main", "a": "1 Main Street", "llc": "Buyer Llc", "kind": "permit", "prod": "Deed Transfer", "v": "", "sd": "", "lat": 29.7002, "lng": -95.4002}];
const SEED_POINTS={"pmt_1-main": {"notes": "Permit #100", "tags": ["permit"]}, "acq_1-main": {"notes": "Corporate acquisition 2026-01-02 by Buyer Llc.", "tags": ["deed"]}};
const LIFE={"acq_1-main": {"s": "deed", "note": "Lifecycle: Deed transfer 2026-01-02 · Buyer Llc"}};
const DEED_PULL={"acq_1-main": "Jan 02, 2026"};
const RECONCILE={"off": {}, "relist": {}, "pending": {}};
"""
    data = span(text, 'DATA')[2]
    return dict(text=text, data=data)


class MergeTest(unittest.TestCase):
    def test_drop_member_keeps_neighbors(self):
        text = 'const DATA=[{"id":"a","n":1},{"id":"b","n":2},{"id":"c","n":3}];\nconst SEED_POINTS={"a":{"notes":"A"},"b":{"notes":"B"},"c":{"notes":"C"}};\n'
        text = pin_overlap.drop_member(text, 'DATA', 'b')
        text = pin_overlap.drop_member(text, 'SEED_POINTS', 'b')
        self.assertEqual([row['id'] for row in span(text, 'DATA')[2]], ['a', 'c'])
        self.assertEqual(set(span(text, 'SEED_POINTS')[2]), {'a', 'c'})
        text = pin_overlap.drop_member(text, 'DATA', 'a')
        text = pin_overlap.drop_member(text, 'DATA', 'c')
        self.assertEqual(span(text, 'DATA')[2], [])
        self.assertIn('const SEED_POINTS=', text)
        text = pin_overlap.drop_member(text, 'SEED_POINTS', 'a')
        text = pin_overlap.drop_member(text, 'SEED_POINTS', 'c')
        self.assertEqual(span(text, 'SEED_POINTS')[2], {})

    def test_same_address_collapses_and_keeps_both_facts(self):
        market = fixture_market()
        merges = pin_overlap.collapse_market(market)
        self.assertEqual(merges, [dict(address='1 MAIN ST', canonical='pmt_1-main', retired=['acq_1-main'])])
        self.assertEqual([row['id'] for row in market['data']], ['pmt_1-main'])
        kept = market['data'][0]
        self.assertEqual(kept['permits'][0]['proj'], '100')
        self.assertEqual(kept['llc'], 'Permit Owner')
        self.assertIn('acq_1-main', kept['listing_alias_ids'])
        seed = span(market['text'], 'SEED_POINTS')[2]['pmt_1-main']
        self.assertIn('Permit #100', seed['notes'])
        self.assertIn('Corporate acquisition 2026-01-02', seed['notes'])
        self.assertIn('Buyer Llc', seed['notes'])
        self.assertIn('deed', seed['tags'])
        self.assertIn('permit', seed['tags'])
        self.assertNotIn('pmt_1-main', span(market['text'], 'LIFE')[2])
        self.assertNotIn('acq_1-main', span(market['text'], 'LIFE')[2])
        self.assertEqual(span(market['text'], 'DEED_PULL')[2]['pmt_1-main'], 'Jan 02, 2026')
        self.assertEqual(pin_overlap.collapse_market(market), [])
        report = pin_overlap.audit(market['data'])
        self.assertEqual(report['addresses'], [])
        self.assertEqual(report['property_ids'], [])

    def test_deed_pair_adopts_lifecycle_and_is_stable(self):
        text = """let DATA = [{"id": "2131146866", "a": "1300 Waverly St", "llc": "Tomo Development Llc", "v": "$775,265", "sd": "2026-03-16", "lot": "8000", "prod": "Single Lot", "ty": "active_single", "lat": 29.794494, "lng": -95.404335}, {"id": "2131146860", "a": "1300 Waverly Street", "llc": "Tomo Development Llc", "v": "$468,000", "sd": "2026-03-16", "lot": "5200", "lat": 29.794517, "lng": -95.404112}];
const SEED_POINTS={};
const LIFE={"2131146866": {"s": "deed", "note": "Lifecycle: Deed transfer 2026-03-16 · Tomo Development Llc"}, "2131146860": {"s": "deed", "note": "Lifecycle: Deed transfer 2026-03-16 · Tomo Development Llc"}};
const DEED_PULL={};
"""
        market = dict(text=text, data=span(text, 'DATA')[2])
        merges = pin_overlap.collapse_market(market)
        self.assertEqual(merges[0]['canonical'], '2131146866')
        self.assertEqual(merges[0]['retired'], ['2131146860'])
        kept = market['data'][0]
        self.assertEqual(kept['v'], '$775,265')
        self.assertEqual(kept['lot'], '8000')
        self.assertEqual(kept['prod'], 'Single Lot')
        seed = span(market['text'], 'SEED_POINTS')[2]['2131146866']
        self.assertIn('2131146860', seed['notes'])
        self.assertIn('$468,000', seed['notes'])
        self.assertIn('5200', seed['notes'])
        self.assertIn('deed', seed['tags'])
        life = span(market['text'], 'LIFE')[2]
        self.assertEqual(set(life), {'2131146866'})
        self.assertEqual(pin_overlap.collapse_market(market), [])

    def test_distinct_units_are_not_merged(self):
        rows = [
            {'id': '2131318586', 'a': '711 E 25th St A', 'lat': 1, 'lng': 2},
            {'id': 'pmt_711-b', 'a': '711 E 25th St B', 'u': 'https://app.dealmachine.com/leads#property(id)=2131318586', 'lat': 1, 'lng': 2},
        ]
        self.assertEqual(pin_overlap.address_groups(rows), {})
        self.assertEqual(pin_overlap.same_address_ids(rows), [])

    def test_stacked_points_are_spread(self):
        rows = [
            {'id': 'a', 'a': '10 Oak St A', 'lat': 29.80, 'lng': -95.40},
            {'id': 'b', 'a': '10 Oak St B', 'lat': 29.80, 'lng': -95.40},
            {'id': 'c', 'a': '12 Oak St', 'lat': 29.80002, 'lng': -95.40},
        ]
        self.assertEqual(pin_overlap.stacked_display(rows), [])
        positions = pin_overlap.display_positions(rows)
        self.assertGreater(pin_overlap.meters(*positions['a'], *positions['b']), pin_overlap.NEAR_M)
        # 12 Oak is about 2m north, outside the same-point cluster, so it stays put.
        self.assertEqual(positions['c'], (29.80002, -95.40))


class MapAuditTest(unittest.TestCase):
    def test_every_market_page_spreads_same_point_pins(self):
        pages = [cfg['html'] for cfg in MARKETS.values()] + ['springvalley.html']
        for name in pages:
            text = (ROOT / name).read_text()
            self.assertIn(pin_overlap.DISP_LL_JS, text, name)
            self.assertNotIn(OLD_SPREAD, text, name)

    def test_no_duplicate_address_or_stacked_marker(self):
        pages = [(name, cfg['html']) for name, cfg in MARKETS.items()]
        pages.append(('springvalley', 'springvalley.html'))
        for name, html in pages:
            records = span((ROOT / html).read_text(), 'DATA')[2]
            report = pin_overlap.audit(records)
            self.assertEqual(report['addresses'], [], name)
            self.assertEqual(report['property_ids'], [], name)
            self.assertEqual(report['stacked'], [], name)

    def test_deed_metadata_does_not_repeat_an_event(self):
        for path in sorted(ROOT.glob('*_deed.data.json')):
            meta = json.loads(path.read_text())
            seen = set()
            for pull in meta.get('pulls') or []:
                for prop in pull.get('properties') or []:
                    key = (prop.get('id'), prop.get('sale_date'), prop.get('v'), prop.get('apn'))
                    self.assertNotIn(key, seen, path.name)
                    seen.add(key)


if __name__ == '__main__':
    unittest.main()
