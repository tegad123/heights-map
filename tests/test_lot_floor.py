"""Lot floor drops a row. It does not relabel Single Lot versus Split Lot."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import active_ingest
from sold_classification import MIN_LOT_SQFT, MIN_YEAR_BUILT, classify_lot, lot_floor_reason


HEADER = ['MLS Number', 'Address', 'Latitude', 'Longitude', 'Status', 'List Price',
          'Original List Price', 'Close Price', 'Close Date', 'Building SqFt', 'Lot Size',
          'DOM', 'Year Built', 'Builder Name', 'School Elementary', 'List Agent Full Name',
          'Selling Agent Full Name', 'Subdivision']


def row(**overrides):
    base = {
        'MLS Number': '1', 'Address': '999 Floor Test Street',
        'Latitude': '29.81157', 'Longitude': '-95.39426', 'Status': 'Active',
        'List Price': '900000', 'Original List Price': '925000', 'Close Price': '',
        'Close Date': '', 'Building SqFt': '2400', 'Lot Size': '5000', 'DOM': '10',
        'Year Built': '2026', 'Builder Name': 'Test Builder',
        'School Elementary': 'Test Elementary', 'List Agent Full Name': 'Test Agent',
        'Selling Agent Full Name': '', 'Subdivision': 'Test',
    }
    base.update(overrides)
    return base


def write_csv(path, rows):
    with open(path, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)


class LotFloorTest(unittest.TestCase):
    def test_classification_thresholds_stay_put(self):
        self.assertEqual(classify_lot(4000), 'Single Lot')
        self.assertEqual(classify_lot(3999), 'Split Lot')
        self.assertEqual(classify_lot(MIN_LOT_SQFT), 'Split Lot')
        self.assertEqual(classify_lot(MIN_LOT_SQFT - 1), 'Split Lot')
        self.assertEqual(classify_lot(1500), 'Split Lot')
        self.assertEqual(classify_lot(''), 'Unknown')
        self.assertEqual(classify_lot(0), 'Unknown')
        self.assertEqual(classify_lot(None), 'Unknown')

    def test_floor_reasons(self):
        self.assertIsNone(lot_floor_reason(MIN_LOT_SQFT))
        self.assertIsNone(lot_floor_reason(4000))
        self.assertIsNone(lot_floor_reason('2,200'))
        self.assertEqual(lot_floor_reason(MIN_LOT_SQFT - 1), 'LOT_BELOW_MIN')
        self.assertEqual(lot_floor_reason(1460), 'LOT_BELOW_MIN')
        self.assertEqual(lot_floor_reason(''), 'MISSING_OR_INVALID_LOT_SIZE')
        self.assertEqual(lot_floor_reason(0), 'MISSING_OR_INVALID_LOT_SIZE')
        self.assertEqual(lot_floor_reason(-5), 'MISSING_OR_INVALID_LOT_SIZE')
        self.assertEqual(lot_floor_reason('n/a'), 'MISSING_OR_INVALID_LOT_SIZE')

    def test_active_ingest_drops_floor_and_keeps_current_price(self):
        snapshot = active_ingest.ROOT / 'heights_active.data.json'
        before = snapshot.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            single = Path(tmp) / 'single.csv'
            split = Path(tmp) / 'split.csv'
            write_csv(single, [row(**{'MLS Number': '100', 'Lot Size': '5000', 'Address': '999 Floor Single Street'})])
            write_csv(split, [
                row(**{'MLS Number': '200', 'Lot Size': '3000', 'Address': '999 Floor Split Street',
                       'List Price': '800000'}),
                row(**{'MLS Number': '300', 'Lot Size': '1460', 'Address': '999 Floor Townhome Street'}),
                row(**{'MLS Number': '400', 'Lot Size': '', 'Address': '999 Floor Blank Street'}),
                row(**{'MLS Number': '500', 'Lot Size': '2500', 'Year Built': str(MIN_YEAR_BUILT - 1),
                       'Address': '999 Floor Old Street'}),
            ])
            report = active_ingest.run('2026-11-12', single, split, apply=False)
        self.assertEqual(snapshot.read_bytes(), before)
        reasons = {}
        for summary in report['files']:
            for reason, count in summary['excluded'].items():
                reasons[reason] = reasons.get(reason, 0) + count
        self.assertEqual(reasons.get('LOT_BELOW_MIN'), 1)
        self.assertEqual(reasons.get('MISSING_OR_INVALID_LOT_SIZE'), 1)
        self.assertEqual(reasons.get('YEAR_BEFORE_MIN'), 1)
        self.assertEqual(report['crosscheck_mismatches'], [])
        self.assertEqual(report['total'], 2)
        self.assertEqual(report['products'], {'Single Lot': 1, 'Split Lot': 1})
        accepted = {row['mls']: row for row in report['accepted']}
        self.assertEqual(set(accepted), {'100', '200'})
        self.assertEqual(accepted['100']['product'], 'Single Lot')
        self.assertEqual(accepted['200']['product'], 'Split Lot')
        self.assertEqual(accepted['200']['current_list_price'], 800000)
        self.assertEqual(accepted['100']['lot_sqft'], 5000)

    def test_misfiled_single_still_refuses(self):
        snapshot = active_ingest.ROOT / 'heights_active.data.json'
        before = snapshot.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            single = Path(tmp) / 'single.csv'
            split = Path(tmp) / 'split.csv'
            write_csv(single, [row(**{'MLS Number': '100', 'Lot Size': '5000'})])
            write_csv(split, [row(**{'MLS Number': '600', 'Lot Size': '5000', 'Address': '999 Floor Misfile Street'})])
            with self.assertRaises(ValueError):
                active_ingest.run('2026-11-12', single, split, apply=False)
        self.assertEqual(snapshot.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
