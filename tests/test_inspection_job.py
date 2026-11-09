"""Run: python3 -m unittest tests.test_inspection_job"""
import json
import tempfile
import unittest
from pathlib import Path

import run_and_deploy

PAGES = ['index.html', 'montrose.html', 'riveroaks.html', 'springbranch.html',
         'springvalley.html', 'timbergrove.html', 'westu.html',
         'gardenoaksoakforest.html']


class ClassifyTest(unittest.TestCase):
    def test_spring_valley_skip_is_not_a_failure(self):
        self.assertEqual(
            run_and_deploy.classify_market(False, 0, False, '', '2026-11-09'),
            ('SKIP', 'no-permits-file'))

    def test_stale_unchanged_file_fails(self):
        self.assertEqual(
            run_and_deploy.classify_market(True, 0, False, '2026-09-28', '2026-11-09'),
            ('FAIL', 'unchanged-stale'))

    def test_scraper_crash_fails(self):
        self.assertEqual(
            run_and_deploy.classify_market(True, 1, False, '2026-09-28', '2026-11-09'),
            ('FAIL', 'exit-1'))

    def test_changed_file_is_ok(self):
        self.assertEqual(
            run_and_deploy.classify_market(True, 0, True, '2026-11-09', '2026-11-09'),
            ('OK', 'updated'))

    def test_same_day_rerun_is_ok(self):
        self.assertEqual(
            run_and_deploy.classify_market(True, 0, False, '2026-11-09', '2026-11-09'),
            ('OK', 'already-fresh'))

    def test_missing_permits_file_skips_without_writing(self):
        market = {
            'name': 'springvalley',
            'permits': '/tmp/no-such-springvalley-permits.json',
            'out': '/tmp/no-such-springvalley-inspections.json',
        }
        status, reason, newest = run_and_deploy.run_scraper(market, 0, '2026-11-09')
        self.assertEqual((status, reason), ('SKIP', 'no-permits-file'))
        self.assertEqual(newest, '')
        self.assertFalse(Path(market['out']).exists())

    def test_newest_stamp_reads_updated_or_scraped_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'inspections.json'
            path.write_text(json.dumps({
                '1': {'updated': '2026-09-24', 'scraped_at': '2026-09-24'},
                '2': {'scraped_at': '2026-09-28'},
                '3': {'updated': ''},
            }))
            self.assertEqual(run_and_deploy.newest_stamp(str(path)), '2026-09-28')
            empty = Path(tmp) / 'empty.json'
            empty.write_text('{}')
            self.assertEqual(run_and_deploy.newest_stamp(str(empty)), '')


class OverviewFreshnessTest(unittest.TestCase):
    def test_every_market_page_labels_forecast_and_inspections(self):
        root = Path(__file__).resolve().parents[1]
        for name in PAGES:
            text = (root / name).read_text()
            self.assertIn('function inspectionFeedAsOf()', text, name)
            self.assertIn('const INSP_STALE_DAYS=10;', text, name)
            self.assertIn('FORECAST · AS OF', text, name)
            self.assertIn('INSPECTIONS', text, name)
            self.assertIn('NONE ON FILE', text, name)
            self.assertNotIn('LIVE · UPDATED', text, name)
            self.assertEqual(text.count('function buildOverview()'), 1, name)


if __name__ == '__main__':
    unittest.main()
