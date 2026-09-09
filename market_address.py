"""Market-only address normalization; preserve fractions before ordinal folding."""
import re
from active_ingest import address_key as legacy_address_key


def address_key(address):
    fractions = []
    def protect(match):
        fractions.append(match.group())
        return 'fractiontoken' + chr(103 + len(fractions))
    protected = re.sub(r'\b\d+/\d+\b', protect, str(address).replace('½', '1/2'))
    key = legacy_address_key(protected)
    for i, value in enumerate(fractions, 1):
        key = key.replace('fractiontoken' + chr(103+i), value)
    return key
