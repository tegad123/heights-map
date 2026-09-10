"""Regression: a fee/trade row cannot consume a building project's identity."""
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import permit_pull


class PermitRowOrderTest(unittest.TestCase):
    def test_742_allston_reaches_geocoder_in_either_order(self):
        # Actual project identity and description; no dependency on ignored CSVs.
        building = dict(zip(permit_pull.HDR, [
            '26018730', 'Building Pmt', '*ALLSTON @ 8TH STREET LLC',
            '742 ALLSTON ST 77007',
            'S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC',
            '0', '1']))
        fee = dict(building, PERMIT_DESC='Plan Review Fee', PERMIT_TYPE='PX')
        for order in ([fee, building, building], [building, fee, building]):
            with self.subTest(first=order[0]['PERMIT_DESC']), tempfile.TemporaryDirectory() as td:
                path = Path(td) / 'rows.csv'
                html = Path(td) / 'fixture.html'
                html.write_text('const DATA=[{"id":"fixture","a":"1 Fixture St"}];\n'
                                'const OUT_OF_ZONE=/^never$/i;\n')
                before = html.read_bytes()
                with path.open('w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=permit_pull.HDR)
                    writer.writeheader()
                    writer.writerows(order)
                with patch.object(permit_pull, 'hcad_geocode', return_value={'status': 'FAIL'}) as geocode:
                    rows, flagged = permit_pull.ingest([str(path)], str(html), 24, False)
                geocode.assert_called_once_with('742 ALLSTON ST')
                self.assertEqual(flagged[0][:3], ('26018730', '742 ALLSTON ST', 'FAIL'))
                self.assertEqual(rows, [])
                self.assertEqual(html.read_bytes(), before)



class CentroidTest(unittest.TestCase):
    def test_small_parcel_translation_and_orientation(self):
        # Independent known rectangle center; world-coordinate cancellation
        # used to move this centroid outside the parcel.
        x, y, width, height = -95.3703, 29.8117, 0.00008, 0.0002
        ring = [[x,y],[x+width,y],[x+width,y+height],[x,y+height],[x,y]]
        for shape in (ring, list(reversed(ring)), ring[:-1]):
            lat, lng = permit_pull._centroid([shape])
            self.assertAlmostEqual(lat, y+height/2, places=10)
            self.assertAlmostEqual(lng, x+width/2, places=10)
        local = [[a-x,b-y] for a,b in ring]
        lat, lng = permit_pull._centroid([local])
        self.assertAlmostEqual(lat+y, y+height/2, places=10)
        self.assertAlmostEqual(lng+x, x+width/2, places=10)


class AddressNormalizationTest(unittest.TestCase):
    @staticmethod
    def feature(address, account='one'):
        return {'attributes': {'address': address, 'legal_lines': '', 'HCAD_NUM': account},
                'geometry': {'rings': [[[-95.40,29.8],[-95.3999,29.8],[-95.3999,29.8001],[-95.40,29.8001],[-95.40,29.8]]]}}

    def geocode(self, requested, returned):
        with patch.object(permit_pull, '_hcad_query', return_value=returned), patch.object(permit_pull.time, 'sleep'):
            return permit_pull.hcad_geocode(requested)

    def test_equivalent_formats_keep_identity(self):
        pairs = [('4133 KOLB ST A', '4133 A KOLB ST'),
                 ('1034 W 17TH ST E', '1034 E W 17TH ST'),
                 ('1443 W 25TH ST H', '1443 W 25TH ST # H'),
                 ('606 LINK RD G', '606 LINK RD # G'),
                 ('1809 PALMETTO LANDING (PVT) DR 7700', '1809 PALMETTO LANDING DR'),
                 ('6120 COTTAGE GROVE LAKE (PVT) DR 77', '6120 COTTAGE GROVE LAKE DR'),
                 ('100 EAST 7TH ½ STREET UNIT B', '100 E 7TH 1/2 ST # B'),
                 ("100 O’CONNOR STREET", "100 O'CONNOR ST")]
        for requested, actual in pairs:
            with self.subTest(requested=requested):
                self.assertEqual(self.geocode(requested, [self.feature(actual)])['status'], 'OK')

    def test_does_not_guess_unit_direction_fraction_or_suffix(self):
        pairs = [('815 LAWRENCE ST B', '815 LAWRENCE ST # A'),
                 ('2012 SUMMER ST A', '2012 SUMMER ST'),
                 ('2704 MAXROY ST', '2704 MAXROY ST # G'),
                 ('220 W 8TH ST', '220 E 8TH ST'),
                 ('100 E 7TH 1/2 ST', '100 E 7TH ST'),
                 ('100 EXAMPLE RD', '100 EXAMPLE DR'),
                 ("100 O'CONNOR ST", '100 OCONNOR ST'),
                 ('1824 HEIGHTS BLVD BLD A', '1824 HEIGHTS BLVD')]
        for requested, actual in pairs:
            with self.subTest(requested=requested):
                self.assertEqual(self.geocode(requested, [self.feature(actual)])['status'], 'FAIL')
        self.assertEqual(permit_pull.hcad_address('100 FM 77'), '100 FM 77')

    def test_multiple_accounts_are_ambiguous(self):
        result = self.geocode('100 EXAMPLE ST', [self.feature('100 EXAMPLE ST','one'),self.feature('100 EXAMPLE ST','two')])
        self.assertEqual(result['status'], 'AMBIG')

    def test_query_escapes_apostrophe(self):
        with patch.object(permit_pull, '_hcad_query', return_value=[]) as query, patch.object(permit_pull.time, 'sleep'):
            permit_pull.hcad_geocode("100 O'CONNOR ST")
        self.assertIn("O''CONNOR", query.call_args_list[0].args[0])

    def test_approved_heights_exclusions(self):
        regex = permit_pull.out_of_zone_re((Path(__file__).resolve().parents[1] / 'index.html').read_text())
        for address in ['6808 N MAIN ST A', '6808 N Main Street Unit A', '102 SYLVESTER RD A', '102 Sylvester Road E', '102 SYLVESTER RD']:
            self.assertIsNotNone(regex.search(address), address)
        for address in ['6808 N MAIN ST', '6808 N MAIN ST B', '1102 SYLVESTER RD', '1020 SYLVESTER RD']:
            self.assertIsNone(regex.search(address), address)


class HcadQueryTest(unittest.TestCase):
    def test_paginates_without_losing_features(self):
        pages = [io.BytesIO(json.dumps({'features': [{'id': 1}], 'exceededTransferLimit': True}).encode()),
                 io.BytesIO(json.dumps({'features': [{'id': 2}]}).encode())]
        with patch.object(permit_pull.urllib.request, 'urlopen', side_effect=pages) as query:
            self.assertEqual(permit_pull._hcad_query("address LIKE '100 %'"), [{'id': 1}, {'id': 2}])
        self.assertIn('resultOffset=1', query.call_args_list[1].args[0])

    def test_service_error_is_not_a_no_match(self):
        page = io.BytesIO(json.dumps({'error': {'code': 500, 'message': 'query failed'}}).encode())
        with patch.object(permit_pull.urllib.request, 'urlopen', return_value=page):
            with self.assertRaisesRegex(RuntimeError, 'HCAD query failed'):
                permit_pull._hcad_query("address = '100 EXAMPLE ST'")


if __name__ == '__main__':
    unittest.main()
