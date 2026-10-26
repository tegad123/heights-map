"""Four-file HAR refresh: refusals, status mapping, per-market zone guards,
listing diff rules, rolling comps, and a no-SOLD market dry run."""
import argparse
import contextlib
import csv
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'refresh'))
import combined_market_ingest as cmi
import refresh
import sold_comp_refresh

HEADER = ['MLS Number', 'Close Date', 'Status', 'County', 'Subdivision', 'Master Planned Community',
          'Builder Name', 'Lot Size', 'Building SqFt', 'Close Price', 'Price Sq Ft Sold', 'Year Built',
          'DOM', 'Original List Price', 'List Agent Full Name', 'List Office Name', 'Co List Team Name',
          'Selling Agent Full Name', 'Selling Office Name', 'Co Selling Agent Full Name',
          'Co Selling Office Name', 'School District', 'Address', 'Longitude', 'Latitude',
          'School Elementary', 'Current Price']


def row(mls, status, address, lat, lng, close='', price='', lot='5000', yb='2026'):
    return {'MLS Number': mls, 'Close Date': close, 'Status': status, 'Builder Name': 'Fixture Homes',
            'Lot Size': lot, 'Building SqFt': '3000', 'Close Price': price, 'Year Built': yb, 'DOM': '10',
            'Original List Price': '1000000', 'Address': address, 'Longitude': str(lng),
            'Latitude': str(lat), 'Current Price': '990000', 'List Agent Full Name': 'Agent'}


def write(path, rows, header=HEADER):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    return Path(path)


class LoadRefusalTest(unittest.TestCase):
    def test_empty_and_missing_columns_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            empty = write(Path(td) / 'empty.csv', [])
            with self.assertRaisesRegex(ValueError, 'Empty export'):
                cmi.load(empty, '', '2026-10-25', zone=lambda *a: None)
            for column in ('Lot Size', 'Status', 'Latitude'):
                partial = write(Path(td) / 'partial.csv', [row('1', 'Active', '1 Main St', 29.8, -95.4)],
                                [h for h in HEADER if h != column])
                with self.subTest(column=column), self.assertRaisesRegex(ValueError, 'missing columns'):
                    cmi.load(partial, '', '2026-10-25', zone=lambda *a: None)

    def test_status_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            statuses = ['Active', 'Pending', 'Option Pending', 'Pend Cont to Show', 'Terminated',
                        'Expired', 'Withdrawn', 'Terminated-Relisted']
            path = write(Path(td) / 's.csv', [row(str(i), s, f'{i} Main St', 29.8, -95.4)
                                              for i, s in enumerate(statuses)])
            records, _, _ = cmi.load(path, '', '2026-10-25', zone=lambda *a: None)
            self.assertEqual([r['status'] for r in records],
                             ['active', 'pending', 'pending', 'pending', 'terminated',
                              'terminated', 'terminated', 'terminated'])
            self.assertEqual(records[0]['current_list_price'], 990000.0)
            self.assertIsNone(records[1]['current_list_price'])
            bad = write(Path(td) / 'bad.csv', [row('9', 'Coming Soon', '9 Main St', 29.8, -95.4)])
            with self.assertRaisesRegex(ValueError, 'Unknown status'):
                cmi.load(bad, '', '2026-10-25', zone=lambda *a: None)


class ZoneGuardTest(unittest.TestCase):
    def test_heights_rules_stay_in_heights(self):
        heights = cmi.zone_guard((ROOT / 'index.html').read_text(), 'heights')
        self.assertEqual(heights('5339 Larkin Street', -95.40, 29.80), 'OOZ_REGEX')
        self.assertEqual(heights('100 Fixture St', -95.360, 29.80), 'OOZ_EAST')
        montrose = cmi.zone_guard((ROOT / 'montrose.html').read_text(), 'montrose')
        self.assertIsNone(montrose('5339 Larkin Street', -95.3985032, 29.7502339))
        self.assertEqual(montrose('5339 Larkin Street', -95.40, 29.80), 'OOZ_POLY')

    def test_westu_uses_zip_and_box_without_polygon(self):
        westu = cmi.zone_guard((ROOT / 'westu.html').read_text(), 'westu')
        self.assertIsNone(westu('3700 Fixture St', -95.43, 29.715))
        self.assertEqual(westu('3700 Fixture St', -95.30, 29.715), 'OOZ_BOX')
        self.assertEqual(westu('3700 Fixture St, Houston, TX 77006', -95.43, 29.715), 'OOZ_ZIP')


def rec(mls, status, close=None):
    return dict(mls=mls, status=status, har_status=status.title(), close_date=close, dom=5)


class ClassifyTest(unittest.TestCase):
    def test_listing_rules(self):
        ids = 'abcdefghij'
        data = {i: {'id': i, 'a': f'{i} Fixture St'} for i in ids}
        state = {'a': ('listed', None, 'single', '2026-10-01'), 'b': ('listed', None, 'single', '2026-10-01'),
                 'c': ('listed', None, 'single', '2026-10-01'), 'd': ('listed', None, None, None),
                 'e': ('listed', None, 'split', '2026-10-01'), 'f': ('off', 'terminated', 'single', '2026-10-01'),
                 'g': ('pending', 'under contract', 'single', '2026-10-01'),
                 'i': ('listed', None, 'single', '2026-10-01'),
                 'j': ('pending', 'under contract', 'single', '2026-10-01')}
        groups = {'a': [rec('1', 'active')], 'b': [rec('2', 'pending')],
                  'e': [rec('50', 'terminated')], 'f': [rec('60', 'terminated'), rec('6', 'active')],
                  'g': [rec('7', 'pending')], 'h': [rec('8', 'active')],
                  'i': [rec('9', 'terminated')], 'j': [rec('10', 'sold', '2026-10-20')]}
        prior = {'a': dict(mls='1'), 'b': dict(mls='2'), 'c': dict(mls='3'), 'e': dict(mls='5'),
                 'f': dict(mls='60'), 'g': dict(mls='7'), 'i': dict(mls='9'), 'j': dict(mls='10')}
        seen = {'1', '2', '3', '5', '50', '60', '7', '9', '10'}
        out = refresh.har_classify(data, state, groups, prior, seen, '2026-10-07')
        dropped = {d['id']: d['disposition'] for d in out['dropped']}
        self.assertEqual(dropped, {'b': 'under contract', 'c': 'unconfirmed', 'e': 'unconfirmed',
                                   'i': 'terminated', 'j': 'sold'})
        self.assertEqual(sorted(out['matchedIds']), ['a', 'g'])
        self.assertEqual(out['pending'], ['g'])
        self.assertEqual([r['id'] for r in out['relisted']], ['f'])
        self.assertEqual([i for i, _ in out['staged']], ['h'])
        self.assertEqual([u['id'] for u in out['unresolved']], ['d'])
        baseline = {'date': '2026-10-01', 'dropped': [
            {'id': 'f', 'ty': 'single', 'disposition': 'terminated'},
            {'id': 'g', 'ty': 'single', 'disposition': 'under contract'},
            {'id': 'j', 'ty': 'single', 'disposition': 'under contract'}],
            'relisted': [{'id': i, 'ty': 'single'} for i in 'abcdei']}
        chg = dict(date='2026-10-25', dropped=out['dropped'], relisted=out['relisted'],
                   dispositionUpdates=out['dispositionUpdates'])
        off, rel, pend, disp, _ = refresh.fold_events([baseline, chg])
        self.assertEqual(sorted(pend), ['b', 'g'])
        self.assertFalse(set(pend) & set(off))
        self.assertEqual(sorted(off), ['c', 'e', 'i', 'j'])
        self.assertEqual(sorted(rel), ['a', 'd', 'f'])


class RollingCompTest(unittest.TestCase):
    def test_incremental_keeps_window_and_retires_aged(self):
        prior = [dict(id='s100', a='100 Kept St', lat=29.8, lng=-95.4, cp=900000.0, sq=3000.0, cd='2026-01-15',
                      psf=300.0, lot=5000.0, yb=2025.0, coh='nc'),
                 dict(id='s200', a='200 Aged St', lat=29.8, lng=-95.4, cp=800000.0, sq=2500.0, cd='2025-10-20',
                      psf=320.0, lot=3000.0, yb=2025.0, coh='nc')]
        policy = dict(kind='new_construction_trailing_365', as_of='2026-10-07', start='2025-10-07',
                      end='2026-10-07', source='September 14 baseline + September 28 and October 7 incremental sales',
                      min_lot_sqft=2200)
        html = ('const SOLD_EVIDENCE=' + json.dumps(prior) + ';\nconst SOLD_COMP_POLICY=' + json.dumps(policy) +
                ';\nconst SOLD_DATA=' + json.dumps(prior) + ';\nconst SOLD_METRICS={};\n')
        with tempfile.TemporaryDirectory() as td:
            path = write(Path(td) / 'sold.csv', [
                row('300', 'Sold', '300 New St', 29.8, -95.4, '10/10/2026', '1100000'),
                row('400', 'Sold', '400 Small St', 29.8, -95.4, '10/11/2026', '700000', lot='1800')])
            records, _, profile = cmi.load(path, html, '2026-10-25', zone=lambda *a: None)
        self.assertEqual(sold_comp_refresh.window_scope(profile['close_min'], '2026-10-25'), 'incremental')
        self.assertEqual(sold_comp_refresh.window_scope('2025-11-01', '2026-10-25'), 'full')
        result = sold_comp_refresh.rolling(html, records, '2026-10-25', prior, 'incremental')
        self.assertEqual(sorted(r['id'] for r in result['comps']), ['s100', 's300'])
        self.assertEqual(result['report']['retired_outside_window'], ['s200'])
        self.assertEqual([r['REASON'] for r in result['ledger']], ['BELOW_COMP_MIN_LOT_SQFT'])
        self.assertEqual(result['policy']['coverage'], sold_comp_refresh.INCREMENTAL_COVERAGE)
        self.assertEqual(result['policy']['source'],
                         'September 14 baseline + September 28, October 7 and October 25 incremental sales')
        self.assertEqual({r['id'] for r in result['evidence']}, {'s100', 's200', 's300'})


class NoSoldMarketDryRunTest(unittest.TestCase):
    def tearDown(self):
        refresh.set_market('heights')

    def args(self, td, market, files):
        return argparse.Namespace(market=market, date='2026-10-25', runtime=None, out=str(Path(td) / 'out'),
                                  apply=False, html=None, **files)

    def test_montrose_dry_run_stages_sold_review_and_writes_nothing(self):
        html_path = ROOT / 'montrose.html'
        before = html_path.read_bytes()
        self.assertNotIn(b'SOLD_DATA', before)
        with tempfile.TemporaryDirectory() as td:
            files = dict(
                active=write(Path(td) / 'a.csv', [
                    row('11', 'Active', '1517 Vermont Street #B', 29.7502339, -95.3985032),
                    row('12', 'Active', '5339 Larkin Street', 29.7480, -95.3950)]),
                pending=write(Path(td) / 'p.csv', [row('13', 'Option Pending', '900 Away St', 29.80, -95.40)]),
                sold=write(Path(td) / 's.csv', [
                    row('14', 'Sold', '4100 Fixture Street', 29.7470, -95.3940, '10/01/2026', '1500000')]),
                terminated=write(Path(td) / 't.csv', [row('15', 'Expired', '901 Away St', 29.80, -95.40)]))
            refresh.set_market('montrose')
            with contextlib.redirect_stdout(io.StringIO()):
                report = refresh.cmd_har(self.args(td, 'montrose', files), str(html_path))
            out = Path(td) / 'out'
            with open(out / 'audit.csv') as f:
                audit = {r['MLS']: r['DECISION'] for r in csv.DictReader(f)}
            candidate = (out / 'candidate' / 'montrose.html').read_text()
            review = json.loads((out / 'candidate' / 'staging' / 'montrose' / 'har_review_2026-10-25.json').read_text())
        self.assertEqual(html_path.read_bytes(), before)
        self.assertFalse((ROOT / 'changes' / 'montrose').exists())
        self.assertNotIn('SOLD_DATA', candidate)
        self.assertIsNone(report['sold'])
        self.assertEqual([r['mls'] for r in review['sold']], ['14'])
        self.assertEqual(audit['11'], 'MATCHED')
        self.assertEqual(audit['12'], 'STAGED_NEW')
        self.assertEqual((audit['13'], audit['15']), ('OOZ_POLY', 'OOZ_POLY'))
        self.assertEqual(report['counts']['dropped'], 0)
        rec = json.loads(re.search(r'const RECONCILE=(\{.*?\});', candidate).group(1))
        self.assertEqual(rec, {'off': {}, 'relist': {}, 'pending': {}})

    def test_refusals(self):
        with tempfile.TemporaryDirectory() as td:
            ok = write(Path(td) / 'ok.csv', [row('1', 'Active', '1 Main St', 29.75, -95.40)])
            empty = Path(td) / 'empty.csv'
            empty.write_bytes(b'')
            files = dict(active=empty, pending=ok, sold=Path(td) / 'missing.csv', terminated=ok)
            refresh.set_market('montrose')
            with self.assertRaisesRegex(SystemExit, 'missing or empty'):
                refresh.cmd_har(self.args(td, 'montrose', files), str(ROOT / 'montrose.html'))
            refresh.set_market('springvalley')
            with self.assertRaisesRegex(SystemExit, 'not an enabled market'):
                refresh.cmd_har(self.args(td, 'springvalley', files), str(ROOT / 'springvalley.html'))


if __name__ == '__main__':
    unittest.main()
