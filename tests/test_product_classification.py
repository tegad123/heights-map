"""Product parity, conservative evidence, and importer integration regressions."""
import contextlib
import csv
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import product_classification as product
import permit_pull


class ProductTest(unittest.TestCase):
    def test_legacy_csv_byte_parity(self):
        cases = []
        for legal in ('', 'LTS 6 & 7 BLK 40 SUNSET HEIGHTS',
                      'LT 7 BLK 18 SUNSET HEIGHTS', 'TR 7A BLK 18 SUNSET HEIGHTS',
                      'LT 1 BLK 1 EXAMPLE REPLAT', 'RES A EXAMPLE'):
            for depth in ('', '99.999', '100', '100.001'):
                for size in ('','2','3'):
                    # Separate streets prevent accidental cross-case chains;
                    # each case includes letters and adjacent numbers.
                    street = f'Case{len(cases)}'
                    for number,unit in ((100,'A'),(100,'B'),(102,''),(104,'')):
                        cases.append(dict(address=f'{number} {street} Street {unit}',
                                          legal_desc=legal,depth_ft=depth,ms_of=size))
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)/'input.csv'
            with src.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
            subprocess.run([sys.executable,'-B',str(ROOT/'classify_v9.py'),str(src)],check=True,capture_output=True)
            out=Path(td)/'extracted.csv'
            subprocess.run([sys.executable,'-B',str(ROOT/'product_classification.py'),str(src),'--out',str(out)],check=True,capture_output=True)
            self.assertEqual((Path(td)/'heights_review_v9.csv').read_bytes(),out.read_bytes())

    def test_guards_and_depth_boundary(self):
        parcel=dict(account='one',source='exact test polygon',depth_ft=100)
        for depth,label in ((99.999,'Common Driveway'),(100,'Split Lot'),(100.001,'Split Lot')):
            decision=product.classify('TR 7A BLK 18 SUNSET HEIGHTS',parcel=dict(parcel,depth_ft=depth))
            self.assertEqual(decision['product'],label)
        self.assertEqual(product.classify('TR 7A BLK 18 SUNSET HEIGHTS')['product'],'Unknown')
        self.assertEqual(product.classify('',master_size=7)['product'],'Unknown')
        self.assertEqual(product.classify('LTS 6 & 7 BLK 40 SUNSET HEIGHTS',master_size=7)['product'],'Unknown')
        self.assertEqual(product.classify('LT 1 EXAMPLE',units=3)['product'],'Common Driveway')
        self.assertEqual(product.classify('LT 7 BLK 18|SUNSET HEIGHTS',parcel=parcel)['product'],'Single Lot')
        self.assertEqual(product.classify('LT 1 BLK 1 UNKNOWN SUBDIVISION',parcel=parcel)['product'],'Unknown')
        self.assertEqual(product.classify('LT 7 BLK 18 SUNSET HEIGHTS',parcel=parcel,hold='plat risk')['reason_code'],'HELD_TRIAGE')

    def test_rotated_projected_depth_not_area_or_centroid(self):
        from pyproj import Transformer
        to_ll=Transformer.from_crs(2278,4326,always_xy=True)
        x,y=3110000,13850000
        def point(a,b):
            angle=math.radians(31)
            return list(to_ll.transform(x+a*math.cos(angle)-b*math.sin(angle),y+a*math.sin(angle)+b*math.cos(angle)))
        ring=[point(a,b) for a,b in ((0,0),(30,0),(30,120),(0,120),(0,0))]
        f={'attributes':{'HCAD_NUM':'one'},'geometry':{'rings':[ring]}}
        e=product.parcel_evidence(f)
        self.assertAlmostEqual(e['depth_ft'],120,places=3)
        self.assertAlmostEqual(e['width_ft'],30,places=3)
        self.assertAlmostEqual(e['area_sf'],3600,places=2)
        f['geometry']['rings'].append([point(a+200,b) for a,b in ((0,0),(30,0),(30,120),(0,120),(0,0))])
        self.assertIsNone(product.parcel_evidence(f)['depth_ft'])


    def test_parcel_history_can_withhold_but_not_relabel_whole_lot(self):
        parcel=dict(account='one',source='exact polygon',depth_ft=120,
                    parcel_history=[dict(event='SPLIT',vintage='2025_Oct->2026_Jul')])
        d=product.classify('LT 7 BLK 18 SUNSET HEIGHTS',parcel=parcel)
        self.assertEqual(d['candidate'],'Single Lot')
        self.assertEqual(d['product'],'Unknown')
        self.assertEqual(d['reason_code'],'PARCEL_HISTORY_CONFLICT')
        self.assertEqual(product.classify('LT 1 BLK 1 NEW SUBDIVISION',parcel=parcel)['product'],'Split Lot')

    def test_importer_records_unknown_and_protects_existing(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);html=td/'index.html';src=td/'input.csv'
            before={'id':'existing','a':'1 Existing St','prod':'Single Lot','permits':[]}
            html.write_text('const DATA=['+json.dumps(before)+'];\nconst OUT_OF_ZONE=/^never$/i;\n')
            permit=dict(zip(permit_pull.HDR,['26018730','Building Pmt','OWNER','742 ALLSTON ST 77007','S.F. RES W/ATT GARAGE','0','13']))
            with src.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=permit_pull.HDR);w.writeheader();w.writerow(permit)
            with patch.object(permit_pull,'hcad_geocode',return_value=dict(status='OK',lat=29.784,lng=-95.400)),patch.object(permit_pull,'in_zone_poly',return_value=True),contextlib.redirect_stdout(io.StringIO()):
                rows,_=permit_pull.ingest([str(src)],str(html),24,True)
                first=html.read_bytes()
                again,_=permit_pull.ingest([str(src)],str(html),24,True)
            self.assertEqual(rows[0]['prod'],'Unknown')
            self.assertTrue(rows[0]['product_classification']['reason'])
            self.assertEqual(permit_pull.extract_data(html.read_text())[2][0],before)
            self.assertEqual(html.read_bytes(),first)
            self.assertEqual(again,[])
            ledger=list((td/'pulls').glob('product_*.jsonl'))
            self.assertEqual(len(ledger),1)
            self.assertEqual(len(ledger[0].read_text().splitlines()),1)


if __name__=='__main__':
    unittest.main()
