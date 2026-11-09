"""Run: python3 -m unittest tests.test_inspection_job"""
import json
import tempfile
import unittest
from pathlib import Path

import run_and_deploy
import scrape_inspections as scraper

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


class PublishGuardTest(unittest.TestCase):
    def test_empty_lookup_does_not_replace_history(self):
        prev = {"1": {"inspections": [{"type": "WINDSTORM", "result": "Passed"}]}}
        fresh = {"1": {"inspections": [], "updated": "2026-11-09"}}
        merged, accepted, blocked = scraper.protect_merge(prev, fresh)
        self.assertEqual(blocked, 1)
        self.assertEqual(accepted, 0)
        self.assertEqual(merged["1"]["inspections"][0]["type"], "WINDSTORM")

    def test_new_rows_replace_the_project(self):
        prev = {"1": {"inspections": [{"type": "OLD", "result": "Passed"}]}}
        fresh = {"1": {"inspections": [{"type": "WINDSTORM", "result": "Passed"}]}}
        merged, accepted, blocked = scraper.protect_merge(prev, fresh)
        self.assertEqual((accepted, blocked), (1, 0))
        self.assertEqual(merged["1"]["inspections"][0]["type"], "WINDSTORM")

    def test_partial_run_is_not_published(self):
        prev = {"1": {"inspections": [{"type": "WINDSTORM", "result": "Passed"}]}}
        ok, reason = scraper.publish_decision(prev, prev, attempted=10, accepted=1)
        self.assertFalse(ok)
        self.assertIn("partial-1-of-10", reason)

    def test_majority_run_is_published(self):
        prev = {str(i): {"inspections": [{"type": "WINDSTORM"}]} for i in range(30)}
        ok, reason = scraper.publish_decision(prev, prev, attempted=10, accepted=8)
        self.assertTrue(ok, reason)

    def test_row_collapse_is_not_published(self):
        prev = {str(i): {"inspections": [{"type": "A"}, {"type": "B"}]} for i in range(20)}
        merged = {str(i): {"inspections": [{"type": "A"}]} for i in range(10)}
        ok, reason = scraper.publish_decision(prev, merged, attempted=20, accepted=20)
        self.assertFalse(ok)
        self.assertIn("row-collapse", reason)

    def test_empty_output_is_not_published(self):
        prev = {"1": {"inspections": [{"type": "WINDSTORM"}]}}
        ok, reason = scraper.publish_decision(prev, {}, attempted=4, accepted=4)
        self.assertFalse(ok)
        self.assertEqual(reason, "empty-output")

    def test_first_empty_project_can_be_recorded(self):
        fresh = {"9": {"inspections": [], "status": "None"}}
        merged, accepted, blocked = scraper.protect_merge({}, fresh)
        self.assertEqual((accepted, blocked), (1, 0))
        ok, reason = scraper.publish_decision({}, merged, attempted=1, accepted=1)
        self.assertTrue(ok, reason)
        self.assertEqual(merged["9"]["inspections"], [])


class WorkflowContractTest(unittest.TestCase):
    def test_actions_is_the_scheduled_path(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/inspection-refresh.yml").read_text()
        self.assertIn("cron: '0 11 * * 1,4'", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("group: inspection-refresh", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("timeout-minutes: 360", workflow)
        self.assertIn("workflow_dispatch", workflow)
        self.assertIn("--no-push", workflow)
        commit = (root / ".github/commit-inspection-data.sh").read_text()
        self.assertIn("github-actions[bot]", commit)
        self.assertIn("data: refresh inspections (GitHub Actions)", commit)
        self.assertIn('LIMIT" != "0"', commit)
        catchup = (root / "catchup_check.sh").read_text()
        self.assertIn("INSPECTION_LEGACY_MAC", catchup)
        self.assertIn("inspection_refresh.sh", catchup)
        scraper_text = (root / "scrape_inspections.py").read_text()
        self.assertEqual(scraper_text.count("_wait_for_grid(page, timeout_ms=5000)"), 2)


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
