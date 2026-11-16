"""Lot floor drops a row. It does not relabel Single Lot versus Split Lot.

Run: python3 -B -m unittest tests.test_lot_floor
"""
import unittest

from sold_classification import classify_lot, lot_floor_reason


class LotFloorTest(unittest.TestCase):
    def test_classify_lot_is_unchanged_below_the_floor(self):
        self.assertEqual(classify_lot('1500'), 'Split Lot')
        self.assertEqual(classify_lot('2199'), 'Split Lot')
        self.assertEqual(classify_lot('2200'), 'Split Lot')
        self.assertEqual(classify_lot('3999'), 'Split Lot')
        self.assertEqual(classify_lot('4000'), 'Single Lot')
        self.assertEqual(classify_lot(''), 'Unknown')
        self.assertEqual(classify_lot('0'), 'Unknown')

    def test_floor_reasons(self):
        self.assertEqual(lot_floor_reason(''), 'MISSING_OR_INVALID_LOT_SIZE')
        self.assertEqual(lot_floor_reason(None), 'MISSING_OR_INVALID_LOT_SIZE')
        self.assertEqual(lot_floor_reason('0'), 'MISSING_OR_INVALID_LOT_SIZE')
        self.assertEqual(lot_floor_reason('2199'), 'LOT_BELOW_MIN')
        self.assertIsNone(lot_floor_reason('2200'))
        self.assertIsNone(lot_floor_reason('4000'))


if __name__ == '__main__':
    unittest.main()
