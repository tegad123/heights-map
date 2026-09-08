"""Run: /Users/nemoclaw/insp-venv/bin/python -B -m unittest discover -s tests."""
import unittest
from unittest.mock import patch
import scrape_inspections as scraper

class Cell:
    def __init__(self, text='', children=()): self.text, self.children = text, children
    def inner_text(self): return self.text
    def query_selector_all(self, selector): return self.children

class Page:
    def __init__(self, outstanding=True): self.outstanding = outstanding
    def query_selector(self, selector):
        rows = [('Building Pmt','','','Display Project / Inspection Comments'),
                ('1031-FDN PM','','06/01/2026','Partial Approval'),
                ('WINDSTORM','','06/23/2026','Disapproved'),
                ('Plumbing Pmt','','','Display Project / Inspection Comments'),
                ('ROUGH IN','','07/08/2026','Approved')]
        return Cell(children=[Cell(children=[Cell(x) for x in row]) for row in rows])
    def inner_text(self, selector):
        return 'Final Project Inspection is Outstanding' if self.outstanding else 'Inspection History'
    def wait_for_timeout(self, ms): pass
    def set_default_timeout(self, ms): pass

class ScraperTest(unittest.TestCase):
    def test_statuses(self):
        for status, expected in [('Disapproved','Failed'),('Failed','Failed'),
                ('Action Required','Failed'),('Correction Necessary','Failed'),
                ('Approved','Passed'),('Partial Approval','Passed'),
                ('Scheduled','Pending'),('','Pending'),('Unrecognized','Pending')]:
            self.assertEqual(scraper.normalize_result(status, True), expected, status)
    def test_parser_and_serialization(self):
        page=Page()
        rows=scraper.parse_inspections(page)
        self.assertEqual(rows[0]['raw'], 'Partial Approval')
        self.assertEqual(rows[0]['permit_type'], 'Building Pmt')
        self.assertEqual(rows[1]['result'], 'Failed')
        self.assertEqual(rows[2]['permit_type'], 'Plumbing Pmt')
        self.assertEqual(scraper.roll_up_status(rows), 'Partial')
        # Exercise the production scrape driver, including its output construction.
        with patch.object(scraper,'sync_playwright') as playwright, patch.object(scraper,'open_inspection_history',return_value=True):
            browser=playwright.return_value.__enter__.return_value.chromium.launch.return_value
            browser.new_context.return_value.new_page.return_value=page
            result=scraper.scrape([{'proj':'fixture'}],0,True,None)['fixture']
            self.assertEqual(result['inspections'][0]['raw'],'Partial Approval')
            self.assertTrue(result['final_project_inspection_outstanding'])
            page.outstanding=False
            self.assertFalse(scraper.scrape([{'proj':'fixture'}],0,True,None)['fixture']['final_project_inspection_outstanding'])
if __name__ == '__main__': unittest.main()
