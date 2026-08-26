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
def classify(legal):
    if not legal: return None,"no legal"
    up=legal.upper()
    if re.search(r'\bRES\s+[A-Z]\b',up): return "Split","reserve/replat"
    sd=sub_name(legal)
    if not(any(sd.startswith(x) for x in ORIG) and not RP.search(up)):
        return "Split","replat child"
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
def nm(v):
    v=(v or "").strip().lower()
    if "split" in v or "common" in v or "driveway" in v: return "Split"
    if "single" in v: return "Single"
    return ""
src=Path(sys.argv[1]); rows=list(csv.DictReader(open(src,newline="",encoding="utf-8-sig")))
fn=list(rows[0].keys())
for c in ["v6_label","v6_why","v6_product"]:
    if c not in fn: fn.append(c)
dec=und=0; agree=disagree=0; byw=defaultdict(int); flips=defaultdict(list)
for i,r in enumerate(rows,2):
    pred,why=classify(r.get("legal_desc"))
    if pred=="Review":
        # undecided on purpose - do NOT fall through to the Single Lot default
        r["v6_label"]=""; r["v6_why"]=why; r["v6_product"]=""
        und+=1; byw[why]+=1
        continue
    prod="Single Lot"   # PRODFIX
    if pred=="Split":
        if why.startswith("spans"):
            prod="Split Lot"          # follows original lot lines -> frontloaders
        elif "fragment" in why:
            prod="Common Driveway"    # lettered A/B halves -> front/back division
        else:
            try: w,d=float(r.get("width_ft")),float(r.get("depth_ft")); ratio=d/w
            except: ratio=None
            u=UNI.search((r.get("address") or "").split(",")[0].strip())
            prod="Common Driveway" if (u or (ratio and ratio<2.5)) else "Split Lot"
    r["v6_label"]=prod if pred else ""; r["v6_why"]=why; r["v6_product"]=prod
    if pred: dec+=1; byw[why]+=1
    else: und+=1
    cur=nm(r.get("prod"))
    if cur and pred:
        if cur==pred: agree+=1
        else: disagree+=1; flips[why].append((i,r,cur,pred))
out=src.with_name("heights_review_v6.csv")
with out.open("w",newline="",encoding="utf-8") as f:
    w_=csv.DictWriter(f,fieldnames=fn); w_.writeheader(); w_.writerows(rows)
print(f"DECIDED: {dec}/{len(rows)}   undecidable: {und}")
print(f"vs old labels -- agree {agree}, differ {disagree}\n")
print("decisions by reason:")
for k,v in sorted(byw.items(),key=lambda kv:-kv[1]): print(f"  {k:22s} {v}")
print(f"\nlabel changes by reason:")
for k,g in sorted(flips.items(),key=lambda kv:-len(kv[1])):
    print(f"  {k:22s} {len(g)} rows  (e.g. row {g[0][0]} {(g[0][1].get('address') or '')[:30]} {g[0][2]}->{g[0][3]})")
print(f"\n-> {out}")
