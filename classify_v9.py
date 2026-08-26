import csv, re, sys
from collections import defaultdict
from pathlib import Path
ORIG=["HOUSTON HEIGHTS","SUNSET HEIGHTS","SHADY ACRES","STUDES","WOODLAND TERRACE",
 "WEST HEIGHTS","MILROY PLACE","WOODSON PLACE","GOSTICK","QUENSELL LAWN",
 "BARTHOLOMEW PLACE","HARDING HEIGHTS","WOODLAND HEIGHTS","NORHILL","BROOKE SMITH",
 "RIDGEWOOD","INDEPENDENCE HEIGHTS","J AUSTIN","USENER","BOVA","SHADYWOOD","MILROY","WOODSON"]
RP=re.compile(r'\bR/P\b|\bREPLAT\b',re.I)
TOK=re.compile(r'[\s&,]*(?:(THRU|THROUGH|-)\s*)?(\d+[A-Z]?|[A-Z])(?=[\s&,]|$)')
PFX=re.compile(r'\b(LTS?|TRS?)\s+')
UNI=re.compile(r'\b(?:unit\s*#?\s*)?([a-f])\b\s*$',re.I)
DIRS={"west":"w","east":"e","north":"n","south":"s"}
SFX=re.compile(r'\b(street|st|ave|avenue|dr|drive|rd|road|ln|lane|blvd|way|ct|pl)\b\.?',re.I)
FULL_DEPTH=100
def pa(a):
    s=(a or "").split(",")[0].strip().lower(); s=re.sub(r'\bunit\s*#\s*','unit ',s)
    m=re.match(r'^(\d+)\s+(.*)$',s)
    if not m: return None,"",""
    n,rest=int(m.group(1)),m.group(2); u=""
    um=UNI.search(rest)
    if um: u=um.group(1).upper(); rest=rest[:um.start()].strip()
    return n," ".join(DIRS.get(t,t) for t in SFX.sub(" ",rest).split()).strip(),u
def sub_name(l):
    up=" ".join((l or "").upper().split())
    m=re.search(r'\bBLK\s+\S+\s+(.*)$',up)
    if m: return m.group(1).strip()
    m=re.match(r'^(?:LTS?|TRS?|RES)\s+[\dA-Z\s&,]*?\s+([A-Z].*)$',up)
    return m.group(1).strip() if m else up
def counts(l):
    up=" ".join((l or "").upper().split()); w=p=0
    for pm in PFX.finditer(up):
        isl=pm.group(1).startswith("LT"); pos=pm.end(); prev=None
        while True:
            m=TOK.match(up,pos)
            if not m: break
            rng,tok=m.group(1),m.group(2)
            tk=[str(n) for n in range(prev+1,int(tok)+1)] if (rng and prev is not None and tok.isdigit()) else [tok]
            for t in tk:
                if t.isdigit():
                    if isl: w+=1
                    else: p+=1
                else: p+=1
            prev=int(tok) if tok.isdigit() else None; pos=m.end()
    return w,p
def family(legal):
    if not legal: return None,"no legal"
    up=legal.upper()
    if re.search(r'\bRES\s+[A-Z]\b',up): return "Split","reserve/replat"
    sd=sub_name(legal)
    if not(any(sd.startswith(x) for x in ORIG) and not RP.search(up)): return "Split","replat child"
    w,p=counts(legal)
    # An HCAD legal spanning 2+ WHOLE original lots means the parcel was
    # ASSEMBLED, not subdivided: Heights/Sunset Heights plat lots are ~25 ft,
    # so "LTS 6 & 7 BLK 40" is one 50 ft lot carrying one house. This rule used
    # to return Split and mislabelled 13 full-lot builds (614/629 E 26th among
    # them). Verified against the HCAD parcel diff (refresh/parcel_diff.py):
    # all 13 parcels are geometrically unchanged across 2024/2025/2026.
    # Route to review and let unit-count / geometry signals decide instead.
    if w>=2: return "Review",f"assembled {w} lots -> needs_review"
    if w==1 and p: return "Split","lot + fragment"
    if w==1: return "Single","one whole lot"
    if p: return "Split","fragment only"
    return None,"unparsed"
src=Path(sys.argv[1]); rows=list(csv.DictReader(open(src,newline="",encoding="utf-8-sig")))
P={}; bynum=defaultdict(set); bystreet=defaultdict(set)
for i,r in enumerate(rows,2):
    n,st,u=pa(r.get("address")); P[i]=(n,st,u)
    if n is not None: bynum[(st,n)].add(u or "_"); bystreet[st].add(n)
chains={}
for st,ns in bystreet.items():
    used={}
    for n in sorted(ns):
        grp=[n]; m=n
        while m+2 in ns and (m+2)%2==n%2: m+=2; grp.append(m)
        for g in grp: used.setdefault(g,set()).update(grp)
    chains[st]=used
fn=list(rows[0].keys())
for c in ["v9_label","v9_why","v9_units"]:
    if c not in fn: fn.append(c)
tal=defaultdict(int)
for i,r in enumerate(rows,2):
    n,st,u=P[i]
    units = max(len(bynum[(st,n)]), len(chains.get(st,{}).get(n,{n}))) if n is not None else 1
    try: ms=int(str(r.get("ms_of") or "").strip())
    except: ms=None
    try: depth=float(r.get("depth_ft"))
    except: depth=None
    fam,why=family(r.get("legal_desc"))
    if fam is None and units<2: lab=""
    elif fam=="Review" and units<2: lab=""   # assembled lots != subdivision
    elif units>=3 or (ms and ms>=3): lab="Common Driveway"
    elif units==2 or ms==2:
        lab="Common Driveway" if (depth is not None and depth<FULL_DEPTH) else "Split Lot"
    elif fam=="Split":
        lab="Common Driveway" if (depth is not None and depth<FULL_DEPTH) else "Split Lot"
    else: lab="Single Lot"
    r["v9_label"]=lab; r["v9_why"]=f"{why} | units={units}"; r["v9_units"]=units
    tal[lab or "undecided"]+=1
out=src.with_name("heights_review_v9.csv")
with out.open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows)
for k,v in sorted(tal.items(),key=lambda kv:-kv[1]): print(f"  {k:18s} {v}")
print(f"\n-> {out}")
