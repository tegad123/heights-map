"""Address normalization for the actives refresh pipeline.

One normalizer used on both sides of the diff (HAR export rows and DATA
records). Handles the variants hit in practice: case, Street/St, directional
words, "Unit#A" vs trailing/leading unit letters, "845-A" number-letter,
HAR's "27 th" ordinal split, and trailing ", Houston, TX 77008"."""
import re

ST_TYPES = r'(?:st|street|ave|avenue|blvd|boulevard|ln|lane|dr|drive|ct|court|rd|road|pl|place)'
DIRS = {'west': 'w', 'east': 'e', 'north': 'n', 'south': 's'}


def norm(a):
    """Return (number, unit, street_core) for an address string."""
    s = str(a).lower().split(',')[0]
    s = re.sub(r'\bunit\s*#?\s*([a-z0-9]+)\b', r' \1 ', s)   # Unit#A / unit a -> bare token
    s = re.sub(r'^(\d+)\s*-\s*([a-f])\b', r'\1 \2', s)        # 845-A -> 845 a
    s = re.sub(r'\b(\d+)\s+th\b', r'\1th', s)                 # "27 th" -> "27th"
    s = re.sub(r'\(.*?\)', ' ', s)                            # "(est)" etc.
    s = re.sub(r'\s+', ' ', s).strip()
    m = re.match(r'^(\d+)\s+(.*)$', s)
    if not m:
        return ('', '', s)
    num, rest = m.group(1), m.group(2)
    unit = ''
    mm = re.match(r'^([a-f])\s+(.*)$', rest)                  # leading unit: "a larkin st"
    if mm:
        unit, rest = mm.group(1), mm.group(2)
    mt = re.match(r'^(.*?)\s+([a-f])$', rest)                 # trailing unit: "... st b"
    if mt:
        rest, unit = mt.group(1), mt.group(2)
    words = [DIRS.get(w, w) for w in rest.split()]
    if words and re.fullmatch(ST_TYPES, words[-1]):
        words = words[:-1]
    return (num, unit, ' '.join(words))


def key(a):
    n, u, c = norm(a)
    return f'{n}|{u}|{c}'
