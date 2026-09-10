"""Focused Heights split-policy and resilient HTTP tests; no market traversal."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import urllib.error
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from product_classification import classify
from hcad_product_review import request_json, FetchError

class Response:
    status=200
    def __init__(self,payload):self.payload=payload
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self):return json.dumps(self.payload).encode()

class ReviewTests(unittest.TestCase):
    def parcel(self,depth=120):
        return dict(account='child',depth_ft=depth,depth_method='measured',source='HCAD',parcel_history=[dict(event='SPLIT',vintage='2026',children=['child'])])
    def test_scope_and_split(self):
        kwargs=dict(legal='LT 7 BLK 18 SUNSET HEIGHTS',parcel=self.parcel())
        self.assertEqual(classify(**kwargs)['reason_code'],'PARCEL_HISTORY_CONFLICT')
        d=classify(**kwargs,observed_split_override=True)
        self.assertEqual((d['product'],d['reason_code']),('Split Lot','OBSERVED_PARCEL_SPLIT'))
        self.assertEqual(classify(**kwargs,observed_split_override=True,hold='human')['product'],'Unknown')
    def test_boundary_and_invalid(self):
        for depth in (None,99.9999,100,100.0001):
            self.assertEqual(classify(legal='LT 7 BLK 18 SUNSET HEIGHTS',parcel=self.parcel(depth),observed_split_override=True)['product'],'Unknown')
        p=self.parcel();p['geometry_error']='invalid'
        self.assertEqual(classify(legal='LT 7 BLK 18 SUNSET HEIGHTS',parcel=p,observed_split_override=True)['product'],'Unknown')
    def test_later_assembly_blocks_split(self):
        p=self.parcel();p['parcel_history'].append(dict(event='ASSEMBLY',vintage='2027'))
        self.assertNotEqual(classify(legal='LT 7 BLK 18 SUNSET HEIGHTS',parcel=p,observed_split_override=True)['reason_code'],'OBSERVED_PARCEL_SPLIT')
    def test_retry_and_resume(self):
        with tempfile.TemporaryDirectory() as d:
            with patch('urllib.request.urlopen',side_effect=[urllib.error.URLError('DNS'),Response({'features':[]})]) as call,patch('time.sleep') as sleep:
                self.assertEqual(request_json('https://example/query?x',d),{'features':[]})
                self.assertEqual(call.call_count,2);sleep.assert_called_once_with(2)
            with patch('urllib.request.urlopen',side_effect=AssertionError('cache must resume')):
                self.assertEqual(request_json('https://example/query?x',d),{'features':[]})
    def test_errors_never_cached_as_empty(self):
        for response in [urllib.error.URLError('DNS'),Response({'error':{'message':'service failure'}}),Response({})]:
            with tempfile.TemporaryDirectory() as d,patch('urllib.request.urlopen',side_effect=response if isinstance(response,Exception) else None,return_value=response),patch('time.sleep'):
                with self.assertRaises(FetchError):request_json('https://example/query?x',d,attempts=2)
                self.assertEqual(list(Path(d).glob('*.json')),[])
                self.assertEqual(len((Path(d)/'errors.jsonl').read_text().splitlines()),2)

if __name__=='__main__':unittest.main()
