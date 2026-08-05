#!/usr/bin/env python3
"""
gen_acquisitions.py
=====================================================================
Turn a market's *_acquisitions.json into the two literals a market page
needs: the DATA rows (deed-transfer pins) and the paired SEED_POINTS
entries, in the EXACT byte format riveroaks.html uses (DATA line 312,
SEED_POINTS line 331).

Transform (matched field-for-field against riveroaks.html):
  DATA row keys, in order:
    id   = "acq_" + address.lower() with spaces -> hyphens
    a    = address (verbatim)
    llc  = owner (verbatim; "Current Owner" is a literal owner value)
    v    = ""            sd = ""
    kind = "permit"      prod = "Deed Transfer"      (no ty — unclassified;
                         legacy rows carry ty="active_single" from the old
                         hardcode, normalized away by --verify-riveroaks)
    f    = "corporate deed <sale_date>, <lot_sqft:,> sqft lot YB<year_built>"
    c    = ""
    lat, lng = verbatim from the acquisitions record
  SEED_POINTS entry (keyed by the same id):
    notes = "Corporate acquisition <sale_date> by <owner>. "
            "<lot_sqft:,> sqft lot, YB<year_built>. <tail>"
      tail = "Likely teardown-to-spec — pre-permit pipeline watch."  (older homes)
             "Pre-permit pipeline watch."                            (newer homes)
    tags  = ["deed"]

Row filter: keep only in-zone records. riveroaks flags this with
`in_river_oaks`; generally, any record whose `in_<zone>` boolean is False
is dropped. Record order is preserved.

Teardown threshold: riveroaks has teardown up to YB1988 and plain from
YB1990 (no 1989 in the data), so the exact cutoff is undetermined by
riveroaks alone. We use year_built < 1990. If a 1989 acquisition appears
in another market and lands on the wrong side, adjust here.

USAGE
  python3 gen_acquisitions.py --verify-riveroaks     # must be byte-identical
  python3 gen_acquisitions.py montrose_acquisitions.json          # print both literals
  python3 gen_acquisitions.py westu_acquisitions.json --data      # DATA rows only
  python3 gen_acquisitions.py westu_acquisitions.json --seed      # SEED entries only
=====================================================================
"""

import argparse
import json
import sys

TEARDOWN_BEFORE = 1990  # year_built < this -> "Likely teardown-to-spec" note


def slugify(addr):
    return "acq_" + addr.lower().replace(" ", "-")


def record_id(rec):
    # New market files carry an authoritative pre-slugged `id` (handles '#',
    # duplicate addresses, etc). riveroaks has no id field, so derive from the
    # address there — which is what made riveroaks reproduce byte-identical.
    return rec.get("id") or slugify(rec["address"])


def commafmt(n):
    return f"{int(n):,}"


def in_zone(rec):
    """Drop out-of-zone records: any in_<zone> boolean that is explicitly False."""
    for k, v in rec.items():
        if k.startswith("in_") and v is False:
            return False
    return True


def _dumps(obj):
    # Match riveroaks.html: literal unicode (em dash), ", " / ": " separators.
    return json.dumps(obj, separators=(", ", ": "), ensure_ascii=False)


def yb_text(rec):
    # Normal: "YB1950". Missing year_built: "YB unknown" (per operator decision).
    yb = rec.get("year_built")
    return f"YB{yb}" if yb is not None else "YB unknown"


def is_teardown(rec):
    # Only a known pre-1990 build is flagged a likely teardown. A missing
    # year_built is treated as plain (not teardown).
    yb = rec.get("year_built")
    return yb is not None and yb < TEARDOWN_BEFORE


def data_row(rec):
    f = (f"corporate deed {rec['sale_date']}, "
         f"{commafmt(rec['lot_sqft'])} sqft lot {yb_text(rec)}")
    # dict preserves insertion order in py3.7+, so this fixes the key order.
    return {
        "id": record_id(rec),
        "a": rec["address"],
        "llc": rec["owner"],
        "v": "",
        "sd": "",
        "kind": "permit",
        "prod": "Deed Transfer",
        # no "ty": deed pins are unclassified until someone measures the lot.
        # Convention (matches setProd): Single->active_single, Split->active_split,
        # Common Driveway->no ty — so absence here means "not yet classified",
        # and classification is assigned later, never defaulted. The old
        # hardcoded active_single mislabeled every parcel sight-unseen.
        "f": f,
        "c": "",
        "lat": rec["lat"],
        "lng": rec["lng"],
    }


def seed_entry(rec):
    tail = ("Likely teardown-to-spec — pre-permit pipeline watch."
            if is_teardown(rec) else "Pre-permit pipeline watch.")
    notes = (f"Corporate acquisition {rec['sale_date']} by {rec['owner']}. "
             f"{commafmt(rec['lot_sqft'])} sqft lot, {yb_text(rec)}. {tail}")
    return record_id(rec), {"notes": notes, "tags": ["deed"]}


def generate(path):
    recs = [r for r in json.load(open(path)) if in_zone(r)]
    rows = [_dumps(data_row(r)) for r in recs]
    seeds = []
    for r in recs:
        sid, sval = seed_entry(r)
        seeds.append(f"{_dumps(sid)}: {_dumps(sval)}")
    return recs, rows, seeds


def verify_riveroaks():
    """Regenerate the acq rows/seeds and diff against riveroaks.html, byte for byte."""
    dec = json.JSONDecoder()
    src = open("riveroaks.html", encoding="utf-8").read()
    recs, rows, seeds = generate("riveroaks_acquisitions.json")

    mism = []
    for rec, gen in zip(recs, rows):
        sid = record_id(rec)
        anchor = '{"id": "' + sid + '"'
        idx = src.find(anchor)
        if idx < 0:
            mism.append((sid, "DATA", "(row not found in riveroaks.html)", gen))
            continue
        obj, end = dec.raw_decode(src, idx)
        raw = src[idx:end]
        # Legacy rows carry the retired ty="active_single" hardcode; rows
        # classified since then carry a real prod/ty. Normalize both away so
        # verify keeps guarding every OTHER byte of the transform.
        raw_n = raw.replace(', "ty": "active_single"', '')
        if raw_n != gen and raw != gen:
            mism.append((sid, "DATA", raw, gen))

    for rec in recs:
        sid, sval = seed_entry(rec)
        key = _dumps(sid) + ": "
        p = src.find(key)
        if p < 0:
            mism.append((sid, "SEED", "(entry not found in riveroaks.html)", key + _dumps(sval)))
            continue
        vstart = p + len(key)
        obj, end = dec.raw_decode(src, vstart)
        raw = _dumps(sid) + ": " + src[vstart:end]
        gen = _dumps(sid) + ": " + _dumps(sval)
        if raw != gen:
            mism.append((sid, "SEED", raw, gen))

    if not mism:
        print(f"VERIFY OK — {len(rows)} DATA rows + {len(seeds)} SEED entries "
              f"reproduce riveroaks.html byte-identical.")
        return True

    print(f"VERIFY FAILED — {len(mism)} mismatch(es):\n")
    for sid, kind, raw, gen in mism:
        print(f"--- {kind} {sid} ---")
        print(f"  file: {raw}")
        print(f"  gen : {gen}")
        # first differing char
        for i, (a, b) in enumerate(zip(raw, gen)):
            if a != b:
                print(f"  first diff at char {i}: file={a!r} gen={b!r}")
                break
        else:
            if len(raw) != len(gen):
                print(f"  length differs: file={len(raw)} gen={len(gen)}")
        print()
    return False


def main():
    ap = argparse.ArgumentParser(description="Emit DATA rows + SEED_POINTS entries from an acquisitions JSON")
    ap.add_argument("acq", nargs="?", help="path to *_acquisitions.json")
    ap.add_argument("--verify-riveroaks", action="store_true",
                    help="regenerate riveroaks acq rows and diff against riveroaks.html")
    ap.add_argument("--data", action="store_true", help="print only the DATA rows literal")
    ap.add_argument("--seed", action="store_true", help="print only the SEED_POINTS entries literal")
    args = ap.parse_args()

    if args.verify_riveroaks:
        sys.exit(0 if verify_riveroaks() else 1)

    if not args.acq:
        ap.error("provide an acquisitions JSON path, or use --verify-riveroaks")

    recs, rows, seeds = generate(args.acq)
    data_lit = ", ".join(rows)
    seed_lit = ", ".join(seeds)
    if args.data:
        print(data_lit)
    elif args.seed:
        print(seed_lit)
    else:
        print(f"# {len(rows)} DATA rows ({args.acq}):")
        print(data_lit)
        print()
        print(f"# {len(seeds)} SEED_POINTS entries ({args.acq}):")
        print(seed_lit)


if __name__ == "__main__":
    main()
