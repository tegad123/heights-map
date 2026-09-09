"""Sold product labels derived solely from the reported lot area, in square feet."""
import math


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
