"""Market assignment and the shared HAR year/lot filters."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

import har_markets
import har_refresh
from active_ingest import address_key
from deed_ingest import span
from sold_classification import MIN_LOT_SQFT, classify_lot


HEADER = ['MLS Number', 'Address', 'Latitude', 'Longitude', 'Status', 'List Price',
          'Original List Price', 'Close Price', 'Close Date', 'Building SqFt', 'Lot Size',
          'DOM', 'Year Built', 'Builder Name', 'School Elementary', 'List Agent Full Name',
          'Selling Agent Full Name', 'Subdivision']


def row(**overrides):
    base = {
        'MLS Number': '1', 'Address': '100 Test Street',
        'Latitude': '29.74', 'Longitude': '-95.39', 'Status': 'Active',
        'List Price': '900000', 'Original List Price': '925000', 'Close Price': '',
        'Close Date': '', 'Building SqFt': '2400', 'Lot Size': '5000', 'DOM': '10',
        'Year Built': '2026', 'Builder Name': 'Test Builder',
        'School Elementary': 'Test', 'List Agent Full Name': 'Test Agent',
        'Selling Agent Full Name': '', 'Subdivision': 'Test',
    }
    base.update(overrides)
    return base


def write_csv(path, rows):
    with open(path, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)


class AssignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zones = har_markets.load_zones()

    def assign(self, lat, lng, address='100 Test Street'):
        return har_markets.assign_market(lat, lng, address, self.zones)

    def test_boundary_beats_westu_box(self):
        # Lexington Place sits in the Montrose polygon and inside the West U box.
        market, reason, detail = self.assign(29.731936, -95.409878, '2006 Lexington Street')
        self.assertEqual((market, reason), ('montrose', None))
        self.assertIsNone(detail)

    def test_river_oaks_polygon(self):
        market, reason, _ = self.assign(29.750635, -95.413696, '2217 Pelham Drive')
        self.assertEqual((market, reason), ('riveroaks', None))

    def test_westu_box_when_no_polygon_contains_the_point(self):
        market, reason, _ = self.assign(29.705, -95.430, '4000 University Boulevard')
        self.assertEqual((market, reason), ('westu', None))

    def test_spring_valley_city_limit(self):
        market, reason, _ = self.assign(29.789063, -95.503216, '8725 Burkhart Road')
        self.assertEqual((market, reason), ('springvalley', None))

    def test_point_outside_every_market(self):
        market, reason, _ = self.assign(29.854469, -95.480313, '6328 Sapphire Ocean Drive')
        self.assertEqual((market, reason), (None, 'OUT_OF_MARKET'))

    def test_overlapping_polygons_stay_unassigned(self):
        market, reason, detail = self.assign(29.813551, -95.407322, '519 W 30th Street')
        self.assertIsNone(market)
        self.assertEqual(reason, 'AMBIGUOUS_MARKET')
        self.assertEqual(detail, 'gardenoaksoakforest,heights')

    def test_override_puts_shared_polygon_on_one_market(self):
        from deed_ingest import load_overrides
        market, reason, _ = har_markets.assign_market(
            29.815862, -95.402668, '315 W 32nd Street', self.zones, load_overrides())
        self.assertEqual((market, reason), ('gardenoaksoakforest', None))

    def test_heights_boundary_is_reported_and_not_a_write_target(self):
        market, reason, _ = self.assign(29.8146, -95.39489, '334 E 31st Street')
        self.assertEqual((market, reason), ('heights', 'HEIGHTS_SEPARATE_PIPELINE'))
        self.assertNotIn('heights', har_markets.writable_markets())

    def test_out_of_zone_is_attributed_to_the_market(self):
        market, reason, _ = self.assign(29.793361, -95.413751, '5339 Larkin Street')
        self.assertEqual(market, 'heights')
        self.assertEqual(reason, 'OOZ_REGEX')


class FilterTest(unittest.TestCase):
    def test_lot_and_year_rules(self):
        self.assertIsNone(har_markets.listing_reason(row(), 'active'))
        self.assertEqual(har_markets.listing_reason(row(**{'Lot Size': '2199'}), 'active'), 'LOT_BELOW_MIN')
        self.assertEqual(har_markets.listing_reason(row(**{'Lot Size': ''}), 'active'), 'MISSING_OR_INVALID_LOT_SIZE')
        self.assertEqual(har_markets.listing_reason(row(**{'Lot Size': '0'}), 'active'), 'MISSING_OR_INVALID_LOT_SIZE')
        self.assertEqual(har_markets.listing_reason(row(**{'Year Built': '2024'}), 'active'), 'YEAR_BEFORE_MIN')
        self.assertEqual(har_markets.listing_reason(row(**{'Year Built': ''}), 'active'), 'MISSING_YEAR_BUILT')
        self.assertEqual(classify_lot(MIN_LOT_SQFT), 'Split Lot')
        self.assertEqual(classify_lot(3999), 'Split Lot')
        self.assertEqual(classify_lot(4000), 'Single Lot')

    def test_pending_is_not_active_and_not_a_drop(self):
        pending = row(**{'Status': 'Pending', 'MLS Number': '9'})
        self.assertEqual(har_markets.status_bucket(pending, 'active'), 'pending')
        self.assertIsNone(har_markets.listing_reason(pending, 'active'))

    def test_refresh_keeps_pending_out_of_comps_and_does_not_write(self):
        protected = [
            har_refresh.ROOT / 'index.html',
            har_refresh.ROOT / 'heights_active.data.json',
            har_refresh.ROOT / 'montrose_active.data.json',
        ]
        before = {path: path.read_bytes() if path.exists() else None for path in protected}
        with tempfile.TemporaryDirectory() as tmp:
            active = Path(tmp) / 'active.csv'
            sold = Path(tmp) / 'sold.csv'
            write_csv(active, [
                row(**{'MLS Number': '10', 'Address': '2217 Pelham Drive',
                       'Latitude': '29.750635', 'Longitude': '-95.413696', 'Lot Size': '8000'}),
                row(**{'MLS Number': '11', 'Address': '2218 Pelham Drive',
                       'Latitude': '29.750635', 'Longitude': '-95.413696', 'Lot Size': '1500'}),
                row(**{'MLS Number': '12', 'Address': '2219 Pelham Drive',
                       'Latitude': '29.750635', 'Longitude': '-95.413696', 'Year Built': '2020', 'Lot Size': '5000'}),
                row(**{'MLS Number': '13', 'Address': '3058 Locke Lane',
                       'Latitude': '29.74341', 'Longitude': '-95.421525', 'Status': 'Pending',
                       'Lot Size': '9434', 'List Price': '2000000'}),
                row(**{'MLS Number': '14', 'Address': '6328 Sapphire Ocean Drive',
                       'Latitude': '29.854469', 'Longitude': '-95.480313'}),
            ])
            write_csv(sold, [
                row(**{'MLS Number': '20', 'Address': '2321 Claremont Lane', 'Status': 'Sold',
                       'Latitude': '29.744408', 'Longitude': '-95.429927', 'Lot Size': '10500',
                       'Close Price': '3000000', 'Close Date': '2026-06-01', 'List Price': '3100000',
                       'Original List Price': '3200000'}),
                row(**{'MLS Number': '21', 'Address': '334 E 31st Street', 'Status': 'Sold',
                       'Latitude': '29.8146', 'Longitude': '-95.39489', 'Lot Size': '3000',
                       'Close Price': '700000', 'Close Date': '2026-05-01'}),
            ])
            report = har_refresh.run(active, sold, '2026-11-12', apply=False, markets=['riveroaks'])
        for path, raw in before.items():
            current = path.read_bytes() if path.exists() else None
            self.assertEqual(current, raw)
        oaks = report['markets']['riveroaks']
        self.assertEqual(oaks['active'], {'accepted': 1, 'single': 1, 'split': 0})
        self.assertEqual(oaks['sold']['incoming'], 1)
        self.assertGreaterEqual(oaks['sold']['accepted'], 1)
        self.assertEqual(oaks['pending'], 1)
        self.assertEqual(oaks['dropped'].get('LOT_BELOW_MIN'), 1)
        self.assertEqual(oaks['dropped'].get('YEAR_BEFORE_MIN'), 1)
        self.assertEqual(report['unassigned'].get('OUT_OF_MARKET'), 1)
        self.assertEqual(report['markets']['heights']['dropped'].get('HEIGHTS_SEPARATE_PIPELINE'), 1)
        self.assertNotIn('off_market', json.dumps(oaks))


class RiverOaksListingTest(unittest.TestCase):
    """Accepted River Oaks actives are property pins, and the page uses the Heights panel."""

    def test_every_active_listing_has_a_pin_and_an_active_link(self):
        root = Path(__file__).resolve().parents[1]
        actives = json.loads((root / 'riveroaks_active.data.json').read_text())['listings']
        status = json.loads((root / 'riveroaks_market_status.data.json').read_text())
        data = span((root / 'riveroaks.html').read_text(), 'DATA')[2]
        by_key = {}
        for row in data:
            key = address_key(row.get('a'))
            self.assertNotIn(key, by_key, key)
            by_key[key] = row
        self.assertIn('act_3058-locke-lane', {row['id'] for row in data})
        linked = []
        for listing in actives:
            pin = by_key.get(listing['address_key'])
            self.assertIsNotNone(pin, listing['address'])
            evidence = status['properties'].get(pin['id'])
            self.assertEqual(evidence['status'], 'active', pin['id'])
            self.assertEqual(evidence['current']['mls'], listing['mls'])
            linked.append(pin['id'])
        self.assertEqual(sorted(linked), [
            'act_2217-pelham', 'act_2247-chilton', 'act_3058-locke-lane', 'act_3717-chevy-chase'])
        page = (root / 'riveroaks.html').read_text()
        self.assertIn('data-panel="heights"', page)
        self.assertIn('Overdue — missed target', page)
        script = (root / 'market_status.js').read_text()
        self.assertIn("MARKET_PAGE==='riveroaks'", script)
        layers = (root / 'har_layers.js').read_text()
        self.assertIn('HAR_HEIGHTS_PANEL', layers)
        self.assertIn('function appendHeightsSoldLegend', layers)
        self.assertIn("LOT TYPE", layers)


if __name__ == '__main__':
    unittest.main()
