"""Four-file HAR refresh: refusals, status mapping, per-market zone guards,
listing diff rules, rolling comps, a no-SOLD market dry run, identity linking,
and the link-staged / archive-duplicates / apply_staged follow-ups."""
import argparse
import contextlib
import csv
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'refresh'))
import apply_staged
import combined_market_ingest as cmi
import refresh
import sold_comp_refresh
from market_linkage import Matcher

HEADER = ['MLS Number', 'Close Date', 'Status', 'County', 'Subdivision', 'Master Planned Community',
          'Builder Name', 'Lot Size', 'Building SqFt', 'Close Price', 'Price Sq Ft Sold', 'Year Built',
          'DOM', 'Original List Price', 'List Agent Full Name', 'List Office Name', 'Co List Team Name',
          'Selling Agent Full Name', 'Selling Office Name', 'Co Selling Agent Full Name',
          'Co Selling Office Name', 'School District', 'Address', 'Longitude', 'Latitude',
          'School Elementary', 'Current Price']
EMPTY_RECONCILE = 'const RECONCILE={"off":{},"relist":{},"pending":{}};'


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


@contextlib.contextmanager
def market_root(td, market, html_text):
    """A throwaway repo root holding one market page and no changelog, so
    refresh commands run against fixtures instead of the live tree."""
    root = Path(td) / 'root'
    root.mkdir()
    (root / refresh.MARKETS[market]['html']).write_text(html_text)
    with mock.patch.object(refresh, 'ROOT', str(root)), mock.patch.object(apply_staged, 'ROOT', str(root)):
        refresh.set_market(market)
        try:
            yield root
        finally:
            refresh.set_market('heights')


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


class HarLinkTest(unittest.TestCase):
    def setUp(self):
        self.data = {d['id']: d for d in [
            dict(id='act_100-elm-street', a='100 Elm Street', kind='active', lat=29.8, lng=-95.4),
            dict(id='acq_100-elm-st', a='100 Elm St', kind='permit', prod='Deed Transfer', lat=29.8003, lng=-95.4003),
            dict(id='pmt_200-oak-st', a='200 Oak St, Houston, TX 77008', kind='permit', lat=29.801, lng=-95.401),
            dict(id='pmt_200-oak-st-a', a='200 Oak St A', kind='permit', lat=29.8011, lng=-95.4011),
            dict(id='pmt_300-pine-st', a='300 Pine St', kind='permit', lat=29.81, lng=-95.41),
            dict(id='pmt_300-pine-street', a='300 Pine Street', kind='permit', lat=29.8101, lng=-95.4101)]}
        self.matcher = Matcher(list(self.data.values()), {'raw': list(self.data.values())})

    def link(self, address, lat, lng):
        m = refresh.har_link(self.matcher, self.data, dict(mls='1', address=address, lat=lat, lng=lng))
        return m['member'], m['method'] or m['issue']

    def test_deed_twin_yields_to_the_listing_pin(self):
        self.assertEqual(self.link('100 Elm Street', 29.8, -95.4), ('act_100-elm-street', 'address_deed_twin'))
        self.assertEqual(self.link('300 Pine St', 29.81, -95.41), (None, 'AMBIGUOUS_IDENTITY'))

    def test_street_type_optional_within_distance(self):
        self.assertEqual(self.link('200 Oak Road', 29.801, -95.401), ('pmt_200-oak-st', 'address_loose'))
        self.assertEqual(self.link('200 Oak Road', 29.811, -95.411), (None, 'NOT_TRACKED'))
        self.assertEqual(self.link('200 Oak Rd Unit A', 29.801, -95.401), ('pmt_200-oak-st-a', 'address_loose'))
        self.assertEqual(self.link('200 Oak Road Unit B', 29.801, -95.401), (None, 'AMBIGUOUS_COORDINATE'))


class NoSoldMarketDryRunTest(unittest.TestCase):
    def args(self, td, market, files):
        return argparse.Namespace(market=market, date='2026-10-25', runtime=None, out=str(Path(td) / 'out'),
                                  apply=False, html=None, **files)

    def test_montrose_dry_run_stages_sold_review_and_writes_nothing(self):
        live = (ROOT / 'montrose.html').read_text()
        self.assertNotIn('SOLD_DATA', live)
        page = re.sub(r'const RECONCILE=\{.*?\};', lambda _: EMPTY_RECONCILE, live, count=1, flags=re.S)
        with tempfile.TemporaryDirectory() as td, market_root(td, 'montrose', page) as root:
            html_path = root / 'montrose.html'
            files = dict(
                active=write(Path(td) / 'a.csv', [
                    row('11', 'Active', '1517 Vermont Street #B', 29.7502339, -95.3985032),
                    row('12', 'Active', '5339 Larkin Street', 29.7480, -95.3950)]),
                pending=write(Path(td) / 'p.csv', [row('13', 'Option Pending', '900 Away St', 29.80, -95.40)]),
                sold=write(Path(td) / 's.csv', [
                    row('14', 'Sold', '4100 Fixture Street', 29.7470, -95.3940, '10/01/2026', '1500000')]),
                terminated=write(Path(td) / 't.csv', [row('15', 'Expired', '901 Away St', 29.80, -95.40)]))
            with contextlib.redirect_stdout(io.StringIO()):
                report = refresh.cmd_har(self.args(td, 'montrose', files), str(html_path))
            out = Path(td) / 'out'
            with open(out / 'audit.csv') as f:
                audit = {r['MLS']: r['DECISION'] for r in csv.DictReader(f)}
            candidate = (out / 'candidate' / 'montrose.html').read_text()
            review = json.loads((out / 'candidate' / 'staging' / 'montrose' / 'har_review_2026-10-25.json').read_text())
            self.assertEqual(html_path.read_text(), page)
            self.assertFalse((root / 'changes').exists())
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
            try:
                refresh.set_market('montrose')
                with self.assertRaisesRegex(SystemExit, 'missing or empty'):
                    refresh.cmd_har(self.args(td, 'montrose', files), str(ROOT / 'montrose.html'))
                refresh.set_market('springvalley')
                with self.assertRaisesRegex(SystemExit, 'not an enabled market'):
                    refresh.cmd_har(self.args(td, 'springvalley', files), str(ROOT / 'springvalley.html'))
            finally:
                refresh.set_market('heights')


class HarSplitTest(unittest.TestCase):
    def tearDown(self):
        refresh.set_market('heights')

    def exports(self, td, active=None):
        active = active if active is not None else [
            row('21', 'Active', '100 Heights Fixture St', 29.80, -95.40),
            row('22', 'Active', '1517 Vermont Street #B', 29.7502339, -95.3985032),
            row('23', 'Active', '200 Shared Fixture St', 29.7845, -95.417),
            row('24', 'Active', '5339 Larkin Street', 29.80, -95.40),
            row('25', 'Active', '300 Nowhere St', 29.60, -95.20),
            row('26', 'Active', '400 Bad Coord St', '', '')]
        return dict(
            active=write(Path(td) / 'zipactive.csv', active),
            pending=write(Path(td) / 'zippending.csv', [row('31', 'Option Pending', '101 Heights Fixture St', 29.80, -95.40)]),
            sold=write(Path(td) / 'zipsold.csv', [
                row('41', 'Sold', '4100 Fixture Street', 29.7470, -95.3940, '10/01/2026', '1500000')]),
            terminated=write(Path(td) / 'zipterm.csv', [row('51', 'Expired', '102 Heights Fixture St', 29.80, -95.40)]))

    def split(self, td, files):
        args = argparse.Namespace(date='2026-11-01', out=str(Path(td) / 'split'), **files)
        with contextlib.redirect_stdout(io.StringIO()):
            return refresh.cmd_har_split(args)

    def slice_mls(self, report, market, role):
        manifest = json.loads((Path(report['out']) / market / refresh.SPLIT_MANIFEST).read_text())
        with open(Path(report['out']) / market / manifest['slices'][role]['file'], newline='') as f:
            return [r['MLS Number'] for r in csv.DictReader(f)]

    def test_routes_by_coordinates_and_ledgers_unplaced(self):
        with tempfile.TemporaryDirectory() as td:
            report = self.split(td, self.exports(td))
            self.assertEqual(self.slice_mls(report, 'heights', 'active'), ['21', '23'])
            self.assertEqual(self.slice_mls(report, 'timbergrove', 'active'), ['23'])
            self.assertEqual(self.slice_mls(report, 'montrose', 'active'), ['22'])
            self.assertEqual(self.slice_mls(report, 'montrose', 'pending'), [])
            self.assertEqual(self.slice_mls(report, 'montrose', 'sold'), ['41'])
            self.assertEqual(self.slice_mls(report, 'heights', 'terminated'), ['51'])
            self.assertEqual(report['shared'], {'heights+timbergrove': 1})
            self.assertEqual(sorted(report['markets']), ['heights', 'montrose', 'timbergrove'])
            self.assertIn('westu', report['held'])
            self.assertEqual(report['unplaced'], {'NO_MARKET': 2, 'INVALID_ADDRESS_OR_COORDINATES': 1})
            larkin = next(r for r in report['unplaced_rows'] if r.startswith('24 '))
            self.assertIn('heights:OOZ_REGEX', larkin)
            with open(Path(report['out']) / 'unplaced.csv', newline='') as f:
                self.assertEqual(sorted(r['MLS'] for r in csv.DictReader(f)), ['24', '25', '26'])

    def test_refuses_header_only_source(self):
        with tempfile.TemporaryDirectory() as td:
            files = self.exports(td)
            files['sold'] = write(Path(td) / 'emptysold.csv', [])
            with self.assertRaisesRegex(SystemExit, 'header but no rows'):
                self.split(td, files)

    def test_har_accepts_its_slices_and_refuses_tampering(self):
        html_path = ROOT / 'montrose.html'
        before = html_path.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            report = self.split(td, self.exports(td))
            mdir = Path(report['out']) / 'montrose'
            manifest = json.loads((mdir / refresh.SPLIT_MANIFEST).read_text())
            files = {role: mdir / manifest['slices'][role]['file'] for role in refresh.HAR_ROLES}
            ns = lambda market, f: argparse.Namespace(market=market, date='2026-11-01', runtime=None,
                                                      out=str(Path(td) / 'out'), apply=False, html=None, **f)
            refresh.set_market('montrose')
            with contextlib.redirect_stdout(io.StringIO()):
                result = refresh.cmd_har(ns('montrose', files), str(html_path))
            self.assertEqual(result['files']['pending']['rows'], 0)
            self.assertEqual(result['files']['active']['in_zone'], 1)
            self.assertEqual(html_path.read_bytes(), before)
            refresh.set_market('timbergrove')
            with self.assertRaisesRegex(SystemExit, 'cut for montrose'):
                refresh.cmd_har(ns('timbergrove', files), str(ROOT / 'timbergrove.html'))
            refresh.set_market('montrose')
            files['sold'].write_text(files['sold'].read_text() + '"99","","Sold"\n')
            with self.assertRaisesRegex(SystemExit, 'does not match the split manifest'):
                refresh.cmd_har(ns('montrose', files), str(html_path))


FIXTURE_DATA = [
    '{"id": "act_100-elm-street", "a": "100 Elm Street", "kind": "active", "v": "$1", "lat": 29.8, "lng": -95.4, "ty": "active_single"}',
    '{"id": "acq_100-elm-st", "a": "100 Elm St", "kind": "permit", "prod": "Deed Transfer", "lat": 29.8003, "lng": -95.4003}',
    '{"id": "pmt_200-oak-st", "a": "200 Oak St, Houston, TX 77006", "kind": "permit", "lat": 29.801, "lng": -95.401}',
    '{"id": "pmt_300-pine-st", "a": "300 Pine St", "kind": "permit", "prod": "Split Lot", "lat": 29.81, "lng": -95.41}']
FIXTURE_PAGE = ('<script>\nlet DATA = [' + ',\n'.join(FIXTURE_DATA) + '];\nconst OUT_OF_ZONE=/$^/i;\n'
                'SEED_POINTS={"act_100-elm-street":{"tags":["active_single"]},"acq_100-elm-st":{"tags":["deed"]}};\n'
                'if(Object.keys(SEED_POINTS)){}\nconst LIFE={};\n' + refresh.MARK_BEGIN + '\n' + EMPTY_RECONCILE +
                '\n' + refresh.MARK_END + '\napplyReconcile(state.points);applyReconcile(state.points);\n</script>\n')


def staged_row(sid, address, pin, status, mls, prod, lat, lng):
    tag = 'pending' if status != 'Active' else ('active_split' if prod == 'Split Lot' else 'active_single')
    return dict(id=sid, a=address, geocode='HAR', mergeCandidate=pin, mls=mls, har_status=status,
                data=dict(id=sid, a=address, llc='', v='$1', sd='', lot='3000', kind='active', bb='', prod=prod,
                          f=prod, u='', lat=lat, lng=lng, c=[], ty='active_single'),
                seed=dict(notes='fixture', tags=[tag]))


class IdentityFollowUpTest(unittest.TestCase):
    """link-staged and archive-duplicates against a fixture page + changelog."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.ctx = market_root(self.td.name, 'montrose', FIXTURE_PAGE)
        self.root = self.ctx.__enter__()
        self.staged = [
            staged_row('act_200-oak-street', '200 Oak Street', 'pmt_200-oak-st', 'Active', 'm2', 'Single Lot', 29.8028, -95.401),
            staged_row('act_300-pine-road', '300 Pine Road', 'pmt_300-pine-st', 'Active', 'm8', '', 29.8118, -95.41),
            staged_row('act_300-pine-street', '300 Pine Street', 'pmt_300-pine-st', 'Option Pending', 'm3', '', 29.8101, -95.4101),
            staged_row('act_100-elm-street', '100 Elm Street', 'act_100-elm-street', 'Active', 'm1', 'Single Lot', 29.8, -95.4),
            staged_row('act_301-pine-street', '301 Pine Street', 'pmt_300-pine-st', 'Active', 'm4', '', 29.8101, -95.4101),
            staged_row('act_400-ash-street', '400 Ash Street', None, 'Active', 'm5', 'Single Lot', 29.82, -95.42),
            staged_row('act_200-oak-st-b', '200 Oak St Unit B', None, 'Active', 'm6', 'Split Lot', 29.801, -95.401),
            staged_row('act_200-oak-road', '200 Oak Road', None, 'Active', 'm7', 'Single Lot', 29.83, -95.43)]
        Path(self.root, 'staging', 'montrose').mkdir(parents=True)
        self.staged_path = Path(self.root, 'staging', 'montrose', 'proposed_2026-10-26.json')
        self.staged_path.write_text(json.dumps(self.staged))
        chg = dict(date='2026-10-26', kind='har_incremental_refresh', sources=[], source_hashes={},
                   counts=dict(matched=1, dropped=0, relisted=0, new=len(self.staged), excluded=0),
                   matchedIds=['act_100-elm-street'], dropped=[], relisted=[],
                   new=[dict(a=s['a'], prod=s['data']['prod'], mls=s['mls'], har_status=s['har_status'],
                             staged=True, mergeCandidate=s['mergeCandidate']) for s in self.staged],
                   excluded=[], dispositionUpdates={}, unresolved=[], transitions=[], observed={})
        cdir = Path(self.root, 'changes', 'montrose')
        cdir.mkdir(parents=True)
        (cdir / 'changes_2026-10-26.json').write_text(refresh._as_json(chg))
        (cdir / 'index.json').write_text(refresh._as_json(dict(
            files=[dict(file='changes_2026-10-26.json', date='2026-10-26', counts=chg['counts'])],
            updated='2026-10-26')))

    def tearDown(self):
        self.ctx.__exit__(None, None, None)
        self.td.cleanup()

    def page(self):
        return (self.root / 'montrose.html').read_text()

    def changelog(self):
        return json.loads((self.root / 'changes' / 'montrose' / 'changes_2026-10-26.json').read_text())

    def link(self, approve, apply=True):
        args = argparse.Namespace(market='montrose', date='2026-10-26', file=str(self.staged_path),
                                  approve=approve, apply=apply, skip_pull=True)
        with contextlib.redirect_stdout(io.StringIO()):
            return refresh.cmd_link_staged(args, str(self.root / 'montrose.html'))

    def archive(self, pairs, apply=True):
        args = argparse.Namespace(market='montrose', date='2026-10-26', archive=pairs,
                                  reason='fixture duplicate', apply=apply, skip_pull=True)
        with contextlib.redirect_stdout(io.StringIO()):
            return refresh.cmd_archive_duplicates(args, str(self.root / 'montrose.html'))

    def test_link_staged_records_relist_and_pending_without_touching_data(self):
        before = self.page()
        data_before = before[before.index('let DATA'):before.index('];') + 2]
        self.link(['act_200-oak-street', 'act_300-pine-street'], apply=False)
        self.assertEqual(self.page(), before)
        self.link(['act_200-oak-street', 'act_300-pine-street'])
        after = self.page()
        self.assertEqual(after[after.index('let DATA'):after.index('];') + 2], data_before)
        rec = json.loads(re.search(r'const RECONCILE=(\{.*?\});', after).group(1))
        self.assertEqual(rec['relist'], {'pmt_200-oak-st': {'t': 'single', 'd': '2026-10-26'}})
        self.assertEqual(rec['pending'], {'pmt_300-pine-st': {'t': 'split', 'd': '2026-10-26'}})
        self.assertEqual(rec['off'], {})
        chg = self.changelog()
        self.assertEqual(chg['counts']['relisted'], 1)
        self.assertEqual(chg['counts']['dropped'], 1)
        self.assertEqual(chg['dropped'][0]['disposition'], 'under contract')
        linked = {n['mls']: n for n in chg['new'] if n.get('linked')}
        self.assertEqual(sorted(linked), ['m2', 'm3'])
        self.assertTrue(all(n['applied'] and not n['staged'] for n in linked.values()))
        index = json.loads((self.root / 'changes' / 'montrose' / 'index.json').read_text())
        self.assertEqual(index['files'][0]['counts'], chg['counts'])
        with open(self.root / 'montrose_off_market.csv') as f:
            self.assertEqual(list(csv.DictReader(f)), [])

    def test_link_staged_refusals(self):
        for approve, message in ((['act_100-elm-street'], 'already carries listing state'),
                                 (['act_301-pine-street'], 'is not the address of'),
                                 (['act_300-pine-road'], 'sits 200 m from'),
                                 (['act_400-ash-street'], 'no mergeCandidate'),
                                 (['act_300-pine-street', 'act_300-pine-street'], 'already linked')):
            with self.subTest(approve=approve), self.assertRaisesRegex(SystemExit, message):
                self.link(approve)
        self.assertEqual(self.page(), FIXTURE_PAGE)

    def test_archive_removes_only_the_duplicate_record(self):
        self.archive([['acq_100-elm-st', 'act_100-elm-street']])
        after = self.page()
        kept = [FIXTURE_DATA[0], FIXTURE_DATA[2], FIXTURE_DATA[3]]
        self.assertEqual(after, FIXTURE_PAGE.replace(',\n'.join(FIXTURE_DATA), ',\n'.join(kept)))
        entry = self.changelog()['archived_duplicates'][0]
        self.assertEqual((entry['record']['id'], entry['canonical']), ('acq_100-elm-st', 'act_100-elm-street'))
        with self.assertRaisesRegex(SystemExit, 'already archived'):
            self.archive([['acq_100-elm-st', 'act_100-elm-street']])

    def test_archive_refusals(self):
        for pairs, message in (([['pmt_200-oak-st', 'act_100-elm-street']], 'different addresses'),
                               ([['act_100-elm-street', 'acq_100-elm-st']], 'carries listing state'),
                               ([['acq_100-elm-st', 'acq_100-elm-st']], 'cannot be archived onto'),
                               ([['acq_100-elm-st', 'westu:ACT99']], 'canonical westu:ACT99')):
            if pairs[0][1].startswith('westu:'):
                (self.root / 'westu.html').write_text(FIXTURE_PAGE)
            with self.subTest(pairs=pairs), self.assertRaisesRegex(SystemExit, message):
                self.archive(pairs)
        self.assertEqual(self.page(), FIXTURE_PAGE)

    def run_apply_staged(self, approve):
        argv = ['apply_staged.py', '--file', str(self.staged_path), '--approve', *approve,
                '--html', str(self.root / 'montrose.html')]
        with mock.patch.object(sys, 'argv', argv), contextlib.redirect_stdout(io.StringIO()):
            apply_staged.main()

    def test_apply_staged_refuses_duplicates_and_allows_split_siblings(self):
        for approve, message in ((['act_200-oak-street'], 'link-staged'),
                                 (['act_200-oak-road'], 'already DATA record')):
            with self.subTest(approve=approve), self.assertRaisesRegex(SystemExit, message):
                self.run_apply_staged(approve)
        self.assertEqual(self.page(), FIXTURE_PAGE)
        self.run_apply_staged(['act_400-ash-street', 'act_200-oak-st-b'])
        ids = [d['id'] for d in refresh.extract_data(self.page())]
        self.assertEqual(ids[-2:], ['act_400-ash-street', 'act_200-oak-st-b'])
        applied = {n['mls']: n.get('id') for n in self.changelog()['new'] if n.get('applied')}
        self.assertEqual(applied, {'m5': 'act_400-ash-street', 'm6': 'act_200-oak-st-b'})

    def test_split_siblings(self):
        self.assertTrue(apply_staged.split_siblings('1006 Golden Nectar', '1008 Golden Nectar'))
        self.assertTrue(apply_staged.split_siblings('1208 E 26th Unit A', '1208 E 26th St Unit B'))
        self.assertFalse(apply_staged.split_siblings('1006 Golden Nectar', '1007 Golden Nectar'))
        self.assertFalse(apply_staged.split_siblings('1006 Golden Nectar', '1006 Golden Nectar'))
        self.assertFalse(apply_staged.split_siblings('1006 Golden Nectar', '1008 Silver Nectar'))


if __name__ == '__main__':
    unittest.main()
