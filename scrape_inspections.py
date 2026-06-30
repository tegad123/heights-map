#!/usr/bin/env python3
"""
scrape_inspections.py  (v2 — ILMS Inspection Status)
=====================================================================
Pulls REAL inspection history for Houston building permits and writes
inspections.json that the Heights deal map reads (live, no redeploy).

WHY THIS WAS REWRITTEN
  The original version pointed at houstonpermittingcenter.org/sold-
  permits-search. That WebFOCUS app only holds permit METADATA — it has
  no inspection type/date/result anywhere. That's why it never returned
  inspections.

  Inspections actually live in a SEPARATE app, ILMS Inspection Status:
      https://www.pdinet.pd.houstontx.gov/Inspection_Status/
  This version drives that Angular SPA and parses its Kendo UI grid.
  (Verified live against permits 25098822 and 26010786.)

REAL FLOW (per project number)
  1. Load the ILMS page.
  2. Type the project number into the "Project #" input (only text input).
  3. Click Submit -> page shows project info + a permit-type <select>
     defaulting to "All Types".
  4. Click the second Submit (under the dropdown) -> renders the
     Inspection History Kendo grid.
  5. Parse table.k-grid-table: a FLAT list of tr.k-table-row, each with
     4 td.k-table-td. Rows are one of:
       - permit-header row:  cell0 = permit name (e.g. "Building Pmt"),
                             cell3 = "Display Project / Inspection Comments"
       - inspection row:     cell0 = inspection type, cell2 = date
                             (MM/DD/YYYY), cell3 = status
       - empty group:        cell0 = "No Inspections To Date"

ACTUAL STATUS WORDING (from the live site)
  Approved              -> Passed
  Partial Approval      -> Passed (counts for phase) but flips roll-up to Partial
  Action Required       -> Failed (-> roll-up Partial)
  Correction Necessary  -> Failed (-> roll-up Partial)
  (blank date / scheduled) -> Pending
  No Inspections To Date -> permit omitted

NOTE: there is no clean JSON API (the /ilmsapinew/SaveFileX endpoint uses
an encrypted POST body/response), so we must drive the UI with Playwright.

RUN ON THE MAC MINI (see run_and_deploy.py for the auto-deploy wrapper)
  source ~/insp-venv/bin/activate
  pip install playwright && playwright install chromium
  python3 scrape_inspections.py --permits heights_permits.json \
      --out inspections.json --limit 3 --show     # watch 3 first
=====================================================================
"""

import argparse
import json
import re
import sys
from datetime import date

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit(
        "Playwright is not installed.\n"
        "  python3 -m venv ~/insp-venv && source ~/insp-venv/bin/activate\n"
        "  pip install playwright && playwright install chromium"
    )

ILMS_URL = "https://www.pdinet.pd.houstontx.gov/Inspection_Status/"


# ------------------------------------------------------------------ mapping
def normalize_result(raw: str, has_date: bool) -> str:
    s = (raw or "").strip().lower()
    if not s:
        return "Pending"
    if "approv" in s:           # "Approved" or "Partial Approval"
        return "Passed"
    if "action required" in s or "correction" in s or "fail" in s or "disapprov" in s:
        return "Failed"
    if "schedul" in s or "request" in s or "pending" in s or not has_date:
        return "Pending"
    return "Passed" if has_date else "Pending"


def is_partial(raw: str) -> bool:
    return "partial" in (raw or "").strip().lower()


def roll_up_status(rows):
    if not rows:
        return "Pending"
    results = [r["result"] for r in rows]
    raws = [r.get("raw", "") for r in rows]
    if any(r == "Failed" for r in results):
        return "Partial"
    if any(is_partial(x) for x in raws):
        return "Partial"
    if results and results[-1] == "Pending":
        return "Pending"
    if all(r == "Passed" for r in results):
        return "Passed"
    return "Pending"


def parse_date(raw: str) -> str:
    raw = (raw or "").strip()
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", raw)
    if m:
        mo, da, yr = m.groups()
        yr = ("20" + yr) if len(yr) == 2 else yr
        return f"{yr}-{int(mo):02d}-{int(da):02d}"
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", raw)
    return m.group(0) if m else ""


# ------------------------------------------------- ILMS-specific extraction
def open_inspection_history(page, proj: str) -> bool:
    page.goto(ILMS_URL, wait_until="networkidle", timeout=60000)

    proj_input = None
    for sel in ["input[type='text']", "input:not([type])",
                "input[name*='roject' i]", "input[id*='roject' i]"]:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                proj_input = el
                break
        except Exception:
            continue
    if not proj_input:
        return False
    proj_input.click()
    proj_input.fill("")
    proj_input.type(str(proj), delay=20)

    if not _click_submit(page):
        return False
    page.wait_for_timeout(1500)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass

    try:
        sel_el = page.query_selector("select")
        if sel_el:
            try:
                sel_el.select_option(label=re.compile("All", re.I))
            except Exception:
                try:
                    sel_el.select_option(index=0)
                except Exception:
                    pass
    except Exception:
        pass

    _click_submit(page, second=True)
    page.wait_for_timeout(1500)
    try:
        page.wait_for_selector("table.k-grid-table, table.k-grid-header-table",
                               timeout=20000)
    except Exception:
        return _grid_present(page)
    return True


def _click_submit(page, second=False):
    btns = []
    for sel in ["button:has-text('Submit')", "input[type='submit']",
                "button[type='submit']", "input[value*='Submit' i]"]:
        try:
            btns += page.query_selector_all(sel)
        except Exception:
            continue
    btns = [b for b in btns if _visible(b)]
    if not btns:
        try:
            page.keyboard.press("Enter")
            return True
        except Exception:
            return False
    target = btns[-1] if (second and len(btns) > 1) else btns[0]
    try:
        target.click()
        return True
    except Exception:
        try:
            page.keyboard.press("Enter")
            return True
        except Exception:
            return False


def _visible(el):
    try:
        return el.is_visible()
    except Exception:
        return False


def _grid_present(page):
    try:
        return bool(page.query_selector("table.k-grid-table"))
    except Exception:
        return False


def parse_inspections(page):
    rows_out = []
    body = page.query_selector("table.k-grid-table")
    if not body:
        return rows_out
    trs = body.query_selector_all("tr.k-table-row, tr.k-master-row, tr")
    for tr in trs:
        tds = tr.query_selector_all("td.k-table-td, td")
        if len(tds) < 4:
            continue
        cells = [_text(td) for td in tds]
        c0, c1, c2, c3 = cells[0], cells[1], cells[2], cells[3]

        if "display project" in (c3 or "").lower():
            continue
        if "inspection comments" in (c3 or "").lower():
            continue
        if "no inspections to date" in (c0 or "").lower():
            continue
        if (c0 or "").strip().lower() in ("description", "inspection") and \
           (c3 or "").strip().lower() in ("status", ""):
            continue

        itype = (c0 or "").strip()
        idate_raw = (c2 or "").strip()
        status_raw = (c3 or "").strip()

        if not itype or not status_raw:
            continue
        if itype.lower() in ("building pmt", "electrical pmt", "plumbing pmt",
                             "mechanical pmt"):
            continue

        has_date = bool(parse_date(idate_raw))
        rows_out.append({
            "type": itype,
            "date": parse_date(idate_raw),
            "result": normalize_result(status_raw, has_date),
            "raw": status_raw,
            "inspector": "",
        })
    return rows_out


def _text(el):
    try:
        return (el.inner_text() or "").strip()
    except Exception:
        return ""


# ------------------------------------------------------------------- driver
def scrape(permits, delay, headless, limit):
    out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.set_default_timeout(30000)

        todo = permits[:limit] if limit else permits
        for i, rec in enumerate(todo, 1):
            proj = str(rec["proj"])
            addr = rec.get("address", "")
            try:
                ok = open_inspection_history(page, proj)
                if not ok:
                    print(f"[{i}/{len(todo)}] {proj}  grid did not render  ({addr})")
                    page.wait_for_timeout(int(delay * 1000))
                    continue
                rows = parse_inspections(page)
                if rows:
                    clean = [{k: v for k, v in r.items() if k != "raw"} for r in rows]
                    out[proj] = {
                        "status": roll_up_status(rows),
                        "updated": date.today().isoformat(),
                        "address": addr,
                        "inspections": clean,
                    }
                    print(f"[{i}/{len(todo)}] {proj}  {out[proj]['status']:8} "
                          f"{len(rows)} insp  ({addr})")
                else:
                    print(f"[{i}/{len(todo)}] {proj}  no inspections yet  ({addr})")
            except Exception as e:
                print(f"[{i}/{len(todo)}] {proj}  ERROR {type(e).__name__}: {e}")
            page.wait_for_timeout(int(delay * 1000))

        browser.close()
    return out


def main():
    ap = argparse.ArgumentParser(description="Scrape Houston ILMS inspections -> inspections.json")
    ap.add_argument("--permits", default="heights_permits.json")
    ap.add_argument("--out", default="inspections.json")
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    try:
        permits = json.load(open(args.permits))
    except Exception as e:
        sys.exit(f"Could not read {args.permits}: {e}")

    print(f"Scraping {len(permits)} permits from ILMS "
          f"(delay {args.delay}s, headless={not args.show})...\n")

    data = scrape(permits, args.delay, headless=not args.show, limit=args.limit)

    try:
        prev = json.load(open(args.out))
    except Exception:
        prev = {}
    merged = {**prev, **data}

    with open(args.out, "w") as f:
        json.dump(merged, f, indent=2)

    print(f"\nWrote {len(merged)} permits with inspection data -> {args.out}")
    print(f"  ({len(data)} updated this run)")
    print("The map picks this up on its next load / 6-hour refresh.")


if __name__ == "__main__":
    main()
