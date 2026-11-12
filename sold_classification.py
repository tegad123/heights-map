"""Sold product labels derived solely from the reported lot area, in square feet.

The lot floor is a separate ingest rule. It drops a row. It does not change
Single Lot versus Split Lot: 4,000 sqft or more is Single Lot, and any
positive lot under 4,000 — including 2,200 to 3,999 — is Split Lot.
"""
import math

# Heights new-construction floor. Rows under this, or with a blank or
# nonpositive lot, are dropped at ingest. classify_lot is unchanged.
MIN_LOT_SQFT = 2200
MIN_YEAR_BUILT = 2025


def classify_lot(value):
    try:
        lot = float(str(value).replace(',', '').strip())
    except (TypeError, ValueError):
        return 'Unknown'
    if not math.isfinite(lot) or lot <= 0:
        return 'Unknown'
    if lot >= 4000:
        return 'Single Lot'
    return 'Split Lot'


def lot_floor_reason(value, minimum=None):
    """None when the lot may be ingested. Blank, zero, and sub-minimum are drops."""
    if minimum is None:
        minimum = MIN_LOT_SQFT
    try:
        lot = float(str(value).replace(',', '').replace('$', '').strip())
    except (TypeError, ValueError):
        return 'MISSING_OR_INVALID_LOT_SIZE'
    if not math.isfinite(lot) or lot <= 0:
        return 'MISSING_OR_INVALID_LOT_SIZE'
    if lot < minimum:
        return 'LOT_BELOW_MIN'
    return None
