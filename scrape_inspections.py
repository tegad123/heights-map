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
  Raw status and permit-type grouping are preserved on each inspection.
  The page-level outstanding-final banner is preserved on each project.

  Approved              -> Passed
  Partial Approval      -> Passed (counts for phase) but flips roll-up to Partial
  Action Required       -> Failed (-> roll-up Partial)
  Correction Necessary  -> Failed (-> roll-up Partial)
  (blank date / scheduled) -> Pending
  No Inspections To Date -> permit omitted

NOTE: there is no clean JSON API (the /ilmsapinew/SaveFileX endpoint uses
an encrypted POST body/response), so we must drive the UI with Playwright.

SCHEDULED RUN
  GitHub Actions (.github/workflows/inspection-refresh.yml) is the
  scheduled job: Monday and Thursday, 11:00 UTC (5:00 AM Central
  Standard Time, 6:00 AM Central Daylight Time). SETUP.md is the
  operator doc. The Mac launchd script is a legacy fallback.
  A partial or empty scrape does not write the output file.
=====================================================================
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import date

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

PLAYWRIGHT_INSTALL = (
    "Playwright is not installed.\n"
    "  python3 -m venv ~/insp-venv && source ~/insp-venv/bin/activate\n"
    "  pip install playwright && playwright install chromium"
)

# A run that keeps fewer than this fraction of the permits it attempted
# is a partial scrape (challenge page, timeout, blocked IP). The existing
# file is left untouched. Half is the line for "obviously partial": a
# handful of hits must not replace or freshen a full market file.
MIN_ACCEPTED_FRACTION = 0.5

ILMS_URL = "https://www.pdinet.pd.houstontx.gov/Inspection_Status/"


# ------------------------------------------------------------------ mapping
def normalize_result(raw: str, has_date: bool) -> str:
    s = (raw or "").strip().lower()
    if not s:
        return "Pending"
    if "action required" in s or "correction" in s or "fail" in s or "disapprov" in s:
        return "Failed"
    if s in ("approved", "partial approval"):
        return "Passed"
    if "schedul" in s or "request" in s or "pending" in s or not has_date:
        return "Pending"
    return "Pending"  # Unknown city statuses must never certify a stage.


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
    # domcontentloaded, then an explicit wait for the permit-type step.
    # A fixed 1.5s pause plus networkidle clicked Submit again on the
    # project-number form (ILMS build 2026.10.24) and the grid never opened.
    page.goto(ILMS_URL, wait_until="domcontentloaded", timeout=60000)

    proj_input = None
    try:
        page.locator("input[type='text']").first.wait_for(state="visible", timeout=30000)
    except Exception:
        return False
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
    proj_input.fill(str(proj))

    if not _click_submit(page):
        return False
    # Old UI: a permit-type <select> whose options include "All Types".
    # Current UI (ILMS 2026.10.24): a Kendo dropdown already on "All Types",
    # announced by this heading. Any visible <select> is not enough — the
    # project-number page can host one, and treating it as the second step
    # clicks Submit before the history form exists.
    if not _wait_permit_type_step(page):
        return False
    # The heading renders before project info arrives. Submitting then
    # opens an empty Inspection History shell and the grid never fills.
    if not _wait_project_loaded(page):
        return False

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

    if not _click_submit(page, second=True):
        return False
    # The grid is on the page within a second or two when Submit lands.
    # A 20s wait made a swallowed click cost most of a minute, and a full
    # run is about a thousand permits. Five seconds is enough to tell the
    # click was swallowed; the retry below, and the caller's second pass,
    # load the history.
    if not _wait_for_grid(page, timeout_ms=5000):
        # The permit-type Submit sometimes swallows the first click.
        if not _click_submit(page, second=True):
            return False
        if not _wait_for_grid(page, timeout_ms=5000):
            return False
    _reveal_grid_rows(page)
    return True


def _wait_permit_type_step(page, timeout_ms=30000):
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        try:
            if page.get_by_text("Please Select the desired Permit Type").first.is_visible():
                return True
        except Exception:
            pass
        try:
            for sel in page.query_selector_all("select"):
                if not sel.is_visible():
                    continue
                labels = " ".join(_text(opt) for opt in sel.query_selector_all("option"))
                if re.search(r"all\s*types", labels, re.I):
                    return True
        except Exception:
            pass
        page.wait_for_timeout(200)
    return False


def _wait_project_loaded(page, timeout_ms=20000):
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        try:
            text = page.inner_text("body")
        except Exception:
            text = ""
        if re.search(r"Address:\s*[0-9A-Za-z]", text):
            return True
        page.wait_for_timeout(200)
    return False


def _wait_for_grid(page, timeout_ms=20000):
    try:
        page.wait_for_selector("table.k-grid-table, table.k-grid-header-table",
                               timeout=timeout_ms, state="attached")
        return True
    except Exception:
        return _grid_present(page)


def _reveal_grid_rows(page):
    """Scroll the Kendo grid so virtualized rows are in the DOM before parsing."""
    try:
        page.evaluate("""() => {
          const el = document.querySelector('.k-grid-content');
          if (!el) return;
          const step = el.clientHeight || 400;
          for (let y = 0; y <= el.scrollHeight; y += step) el.scrollTop = y;
          el.scrollTop = el.scrollHeight;
        }""")
        page.wait_for_timeout(200)
    except Exception:
        pass


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
    permit_type = ""
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
            permit_type = (c0 or "").strip()
            continue
        if "inspection comments" in (c3 or "").lower():
            permit_type = (c0 or "").strip()
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
            "permit_type": permit_type,
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
def inspection_row_count(data):
    if not isinstance(data, dict):
        return 0
    total = 0
    for rec in data.values():
        if isinstance(rec, dict) and isinstance(rec.get("inspections"), list):
            total += len(rec["inspections"])
    return total


def protect_merge(prev, fresh):
    """Merge this run onto the previous file.

    Returns (merged, accepted, blocked_empty). A project that already
    has inspection rows is kept unchanged when this lookup came back
    with none — an empty grid is not a reason to delete history.
    accepted counts projects from this run that are kept.
    """
    if not isinstance(prev, dict):
        prev = {}
    if not isinstance(fresh, dict):
        fresh = {}
    kept = {}
    blocked_empty = 0
    for proj, rec in fresh.items():
        old = prev.get(proj)
        old_rows = old.get("inspections") if isinstance(old, dict) else None
        new_rows = rec.get("inspections") if isinstance(rec, dict) else None
        if isinstance(old_rows, list) and old_rows and not new_rows:
            blocked_empty += 1
            continue
        kept[proj] = rec
    return {**prev, **kept}, len(kept), blocked_empty


def publish_decision(prev, merged, attempted, accepted):
    """Whether merged is safe to write over prev. Returns (ok, reason)."""
    if attempted <= 0:
        return False, "nothing-attempted"
    if not isinstance(merged, dict):
        return False, "not-an-object"
    if isinstance(prev, dict) and prev and not merged:
        return False, "empty-output"
    if accepted / attempted < MIN_ACCEPTED_FRACTION:
        return False, f"partial-{accepted}-of-{attempted}"
    prev_rows = inspection_row_count(prev if isinstance(prev, dict) else {})
    new_rows = inspection_row_count(merged)
    if prev_rows >= 20 and new_rows < prev_rows * MIN_ACCEPTED_FRACTION:
        return False, f"row-collapse-{new_rows}-of-{prev_rows}"
    return True, "ok"


def scrape(permits, delay, headless, limit):
    if sync_playwright is None:
        sys.exit(PLAYWRIGHT_INSTALL)
    out = {}
    grid_miss = 0
    errors = 0
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
                    page.wait_for_timeout(1000)
                    ok = open_inspection_history(page, proj)
                if not ok:
                    grid_miss += 1
                    print(f"[{i}/{len(todo)}] {proj}  grid did not render  ({addr})")
                    page.wait_for_timeout(int(delay * 1000))
                    continue
                rows = parse_inspections(page)
                outstanding = bool(re.search(r"Final\s+Project\s+Inspection\s+is\s+Outstanding", page.inner_text("body"), re.I))
                if rows:
                    out[proj] = {
                        "status": roll_up_status(rows),
                        "updated": date.today().isoformat(),
                        "scraped_at": date.today().isoformat(),
                        "address": addr,
                        "final_project_inspection_outstanding": outstanding,
                        "inspections": rows,
                    }
                    print(f"[{i}/{len(todo)}] {proj}  {out[proj]['status']:8} "
                          f"{len(rows)} insp  ({addr})")
                else:
                    # grid rendered but held no inspection rows: record the lookup
                    # so "scraped, none found" is distinguishable from "never scraped".
                    # Empty inspections list -> map shows the section, promotes nothing.
                    out[proj] = {
                        "status": "None",
                        "updated": date.today().isoformat(),
                        "scraped_at": date.today().isoformat(),
                        "address": addr,
                        "final_project_inspection_outstanding": outstanding,
                        "inspections": [],
                    }
                    print(f"[{i}/{len(todo)}] {proj}  no inspections yet  ({addr})")
            except Exception as e:
                errors += 1
                print(f"[{i}/{len(todo)}] {proj}  ERROR {type(e).__name__}: {e}")
            page.wait_for_timeout(int(delay * 1000))

        browser.close()
    scrape.last_stats = {
        "attempted": len(todo),
        "updated": len(out),
        "grid_miss": grid_miss,
        "errors": errors,
    }
    print(f"SCRAPE_SUMMARY attempted={len(todo)} updated={len(out)} "
          f"grid_miss={grid_miss} errors={errors}")
    return out


def main():
    ap = argparse.ArgumentParser(description="Scrape Houston ILMS inspections -> inspections.json")
    ap.add_argument("--permits", default="heights_permits.json")
    ap.add_argument("--out", default="inspections.json")
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--projects", default="",
                    help="comma-separated project numbers: scrape ONLY these "
                         "(addresses looked up from --permits when present)")
    args = ap.parse_args()

    try:
        permits = json.load(open(args.permits))
    except Exception as e:
        sys.exit(f"Could not read {args.permits}: {e}")

    if args.projects:
        by_proj = {str(r.get("proj")): r for r in permits}
        wanted = [p.strip() for p in args.projects.split(",") if p.strip()]
        permits = [by_proj.get(p, {"proj": p, "address": ""}) for p in wanted]

    print(f"Scraping {len(permits)} permits from ILMS "
          f"(delay {args.delay}s, headless={not args.show})...\n")

    data = scrape(permits, args.delay, headless=not args.show, limit=args.limit)
    stats = getattr(scrape, "last_stats", {})
    attempted = int(stats.get("attempted") or 0)

    try:
        prev = json.load(open(args.out))
    except Exception:
        prev = {}
    if not isinstance(prev, dict):
        prev = {}
    merged, accepted, blocked_empty = protect_merge(prev, data)
    ok, reason = publish_decision(prev, merged, attempted, accepted)
    print(f"PUBLISH_CHECK ok={str(ok).lower()} reason={reason} "
          f"accepted={accepted} blocked_empty={blocked_empty} "
          f"attempted={attempted} grid_miss={stats.get('grid_miss', 0)} "
          f"errors={stats.get('errors', 0)}")
    if not ok:
        print(f"REFUSING to write {args.out}: {reason}. "
              f"Existing file left untouched.")
        sys.exit(3)

    tmp = args.out + ".partial"
    try:
        with open(tmp, "w") as f:
            json.dump(merged, f, indent=2)
        os.replace(tmp, args.out)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

    print(f"\nWrote {len(merged)} permits with inspection data -> {args.out}")
    print(f"  ({accepted} accepted this run, {blocked_empty} empty overwrites blocked)")
    print("The map picks this up on its next load / 6-hour refresh.")


if __name__ == "__main__":
    main()
