# Off-Market Editing & Multi-Market Rollout — Design

Status: DRAFT 2026-07-29 — awaiting Spencer/Tega ruling on the open decisions
marked **OPEN DECISION** below. No code until approved. One commit per stage
(§ Implementation order).

## Problem

Four asks, one theme: the off-market machinery built for Heights needs to become
editable (manual disposition/note corrections that survive refresh runs) and then
portable (the other 6 markets get the same machinery, empty of data, ready for
Tega's per-market review).

Investigation findings that reshape the ask are called out inline as
**Finding** blocks — two of them contradict the brief's premises.

## Part 1 — Off Market table becomes editable

### What exists today (verified)

- `renderSolds()` at index.html:1243–1258. Full innerHTML rebuild per call.
  Column-agnostic: iterates the CSV header, renders cells verbatim; only
  `notes` gets `class="nte"`. Read-only — the only interactions are
  column-sort (re-renders the whole table) and Download CSV.
- **CLOSE button finding**: `soldsClose` (index.html:1258) hides the entire
  overlay — it is a modal close, not per-row. "Needs a close affordance beyond
  CLOSE?" — answer: **no new button needed**. Inline autosave means there is no
  edit "mode" to exit; blur ends a cell edit. Two real gaps CLOSE doesn't cover,
  both fixed by flushing, not by a new button:
  1. Edit → click CLOSE inside the 250 ms debounce window loses the save.
     CLOSE handler must flush any pending edit timer before hiding.
  2. Edit → click a sort header: the full re-render destroys the in-progress
     textarea. Sort handler must flush pending edits before re-rendering.
- Notes autosave pattern to clone: index.html:1065–1066 — 250 ms debounced
  `input` handler → persist → `.saved` indicator flashes 900 ms.
- Remote sync: `_sharedSlice()` (index.html:483–484) posts
  `{v, updated, points, fieldEdits, posEdits, pairOverrides}` to
  REMOTE_EDITS_URL (Apps Script), 900 ms debounce, `pagehide` flush with
  keepalive. Merge-on-load IIFE at 854–890: `points` server-wins per id,
  `fieldEdits`/`posEdits` shallow `Object.assign`. `exportEdits` (825) mirrors
  the same buckets.

### Finding — `st` vs disposition: no second vocabulary needed, and none introduced

`"st"` on DATA records has exactly two values in the wild: `"pending"` (12) and
`"sold"` (21). It is a thin generator-baked seed flag, read at 6 sites
(373, 586, 600, 606, 720, 734) solely to: exclude sold records from twin
pairing, seed the `pending` tag into LIFE, and short-circuit inspection phase
promotion. It is never rendered and never carries terminated/unconfirmed.

The real disposition vocabulary — `sold` / `under contract` / `terminated` /
`unconfirmed` — already exists exactly once, in `changes/*.json
dispositionUpdates` → refresh.py `fold_events()` → the CSV `disposition`
column. **The new control uses those four values verbatim and never touches
`st`.** `st` remains an upstream DATA input; a disposition correction does not
rewrite DATA.

### The overlay: `offMarketEdits`

Fifth bucket in the shared state, exact shape:

```js
offMarketEdits: {
  "<id>": {
    "disposition": "sold" | "under contract" | "terminated" | "unconfirmed",  // optional
    "note": "free text",                                                      // optional
    "updated": "2026-07-29T18:04:11.000Z"                                     // required, ISO, set on every edit
  }
}
```

- Lives in `state.offMarketEdits`. Wire-in points (all anchored edits):
  `_sharedSlice()` return at :484, a merge line beside :868 in the load IIFE
  (per-id newest-wins on `updated`, not blind Object.assign — two browsers can
  edit the same row), `exportEdits` at :825, and localStorage via the existing
  `save()`.
- `renderSolds()` merges the overlay onto parsed CSV rows by id before
  rendering: overlay disposition/note replace the CSV cell values, with a
  visible "edited" marker (dot or tinted cell) so manual overrides are
  distinguishable from generated values.
- Per-row controls: `<select>` with the four disposition values; notes as a
  small textarea — both wired with the 250 ms autosave + `.saved` flash,
  writing into `state.offMarketEdits[id]` and stamping `updated`.
- Choosing **under contract** in the table: per the business rule the id must
  leave Off Market entirely (pending, excluded from CSV) — but that transition
  is refresh.py's job, not the browser's (never hand-mutate RECONCILE). Interim
  behavior: the row stays visible showing "under contract" with a hint that it
  moves to pending on next refresh. The overlay does **not** repaint pins or
  retag points — table display only. Pins keep being driven by RECONCILE.

### Generator round-trip — one source of truth

**Finding**: refresh.py reads zero remote data today; REMOTE_EDITS_URL exists
only client-side. So the overlay is invisible to `csv` and `life-sync` until we
build a bridge.

The conflict to resolve: dispositionUpdates (changelog) already drive the CSV
disposition column and the LIFE mapping (REFRESH_DESIGN amendment 4). The
overlay would be a second writer to the same fields.

**Recommendation — changelog stays canonical; the overlay is an inbox, not a
layer.** New refresh.py step `pull-edits` (run first in the cycle, before
`generate`):

1. GET REMOTE_EDITS_URL, extract `offMarketEdits`.
2. For each id: compare `updated` against the date of the newest changelog
   ruling for that id. Overlay newer → materialize it as a new dated
   `changes/changes_<today>.json` entry (`dispositionUpdates` for the
   disposition; see notes below). Changelog newer → overlay entry is stale,
   ignore it.
3. From there the existing pipeline is untouched: `generate` → `csv` →
   `life-sync` fold the changelog exactly as they do now. One writer per field:
   whoever is newest, and the ruling always lands in changes/ so "history lives
   only in changes/" stays true. After a cycle, overlay and CSV agree; the
   overlay entry becomes redundant but harmless (client still renders it on
   top, values identical).

Notes column: `cmd_csv` already carries prior-CSV enrichment (incl. notes)
forward by row. Overlay notes get applied at the `cmd_csv` write step — overlay
note wins over the carried note when its `updated` is newer. Notes do not go
through the changelog (changes/ records state transitions, not prose).

**OPEN DECISION 1 (the big one)**: approve the inbox model above, or prefer the
overlay as a permanent read-time layer that both the client and refresh.py
apply last (no changelog materialization)? The layer model is less code but
creates a second permanent source of truth and violates "history lives only in
changes/". Recommendation stands: inbox model.

**OPEN DECISION 2**: `pull-edits` disposition materialization also implies
refresh.py gains network access to the Apps Script URL (currently the script
touches only git + local files). Acceptable, or should pull-edits write its
proposed changelog to staging/ for human review before it lands in changes/?
(Staging is more consistent with the existing human-gated design; recommend
staging + explicit accept, matching the existing runbook culture.)

## Part 2 — External links

Two static links, `target="_blank" rel="noopener"`:

1. Property-criteria Google Sheet (Tega's, has pull-date column):
   `https://docs.google.com/spreadsheets/d/1TESOz13kZEEh2ql56KQrIyjKPpxJFHLeqHU2P2yVVSg/edit?usp=sharing`
2. Houston sold-permits lookup:
   `https://cohtora.houstontx.gov/approot/soldpermits/online_permit.htm`

**Placement proposal**: the sidebar `.btns` bar (index.html:307–313, where
`soldsBtn` lives) gets two link-styled anchors after the Off Market button:
`SHEET ↗` and `PERMITS ↗`. Same spot in each market file once ported.

**Recommendation**: both shared (1 link each). The sheet is one workbook and the
permit site is citywide. **OPEN DECISION 3**: confirm the sheet doesn't need
per-market tab anchors (`#gid=…`) — if it does, the sheet URL becomes a
per-market constant in each file; trivial either way, just say which.

**Recommendation on the per-pin permit link**: yes — in addition to the toolbar
link, permit-pin popups (`popupHTML`) get a "look up on COH ↗" line. The lookup
site takes a project number the user would otherwise re-type; cheap and
genuinely useful. Flagged for confirmation but recommended.

## Part 3 — Port to the other 6 markets

### Finding — the brief's premise is wrong; the 6 have far less than stated

Verified by grep across montrose / springbranch / springvalley / timbergrove /
westu / riveroaks: they have **zero** occurrences of `editbtn`, `fieldEdits`,
`posEdits`, `pairOverrides`, `REMOTE_EDITS_URL`, `_sharedSlice`. What they do
share with Heights: the `.note-in` notes textarea + autosave, `SEED_TAGS`
(without off_market entries), a **stub** `LIFE={}` (Heights' is populated), and
— surprise — **TY2K already exists in all 7 files** (7 hits each), so the
"port TY2K labels" item is likely a verify-only no-op (confirm the 6's map
includes the off_market keys at implementation).

Also confirmed absent from the 6: `off_market_single`, `RECONCILE`, `soldsBtn`,
`applyReconcile`, `renderSolds`, any twin/pair mechanism (`twin` = 0 hits), any
CSV fetch. The 6 are near-clones of *each other* (26–32 line diffs, all
data/labels) but ~486 changed lines vs Heights; shared blocks are line-shifted
(~+270 in Heights), not drifted.

Consequences:

- The `offMarketEdits` overlay **requires** remote sync, which the 6 don't
  have. Porting Part 1 to them means porting REMOTE_EDITS_URL, `_sharedSlice`,
  `remoteSave`, the merge IIFE, pagehide flush, and sync dot — a much bigger
  anchored-edit than the brief assumed.
- **Finding — the remote blob is a single unnamespaced global.** One Apps
  Script URL, one blob, shape `{v, updated, points, fieldEdits, …}`. Pointing a
  second market at it would have markets clobbering each other. Namespacing is
  required first: either (a) one blob keyed by market
  (`{heights:{…}, montrose:{…}}` — backend `heights_edits_backend.gs` must
  route on a market param), or (b) one Apps Script deployment per market
  (zero backend code change, 7 URLs to manage). Recommend (a).
- `validate_spliced` in refresh.py requires `applyReconcile(state.points)`
  referenced **≥2 times** (seed pass + post-merge pass). The second call site
  lives inside the remote-merge IIFE — so a market without the sync port would
  fail validation unless it gets a second call site anyway or validation is
  parameterized. Cleanest: port the sync stack, both call sites come naturally.

**OPEN DECISION 4**: scope of the port. Options:
  (a) Full stack — off-market machinery + edit/sync infrastructure
      (REMOTE_EDITS_URL namespaced, _sharedSlice, merge IIFE, offMarketEdits).
      Biggest edit, but the 6 end up genuinely identical to Heights and Part 1
      works everywhere. Recommended.
  (b) Off-market machinery only, localStorage-only overlay, sync deferred.
      Smaller, but offMarketEdits corrections on the 6 would be per-browser
      and invisible to refresh.py — half the feature.
  Note (a) still excludes `editbtn`/edit-mode/fieldEdits/posEdits/pairOverrides
  UI unless ruled otherwise — the brief said off-market feature set, and sync
  can carry empty buckets for those. Say if you want full edit-mode parity too.

**OPEN DECISION 5**: the twin divergent-status badge (index.html:952–962)
depends on `_twin` pairing (index.html:397) which none of the 6 have. Port the
pairing machinery too (needed for split-lot markets eventually), or drop the
badge from the port list until pairing is ported? Recommend porting pairing +
badge together only for markets that have split-lot products; otherwise defer.

### Per-market port list (once scope is ruled)

Each market file gets, via anchored edits on the same unique code strings,
applied identically:

- SEED_TAGS: `off_market_single` `#8a8f98`, `off_market_split` `#5f636b`
  (exact Heights colors/names, index.html:433).
- `pinColor` precedence: pending > needs_clarification > off_market > phase >
  listed/market (index.html:620–628 incl. the 1e224df comment block).
- The two pending-guards: `tagCount` (index.html:1090) and `matchSel`
  (index.html:1117) — pending never counts/filters as Off Market.
- TY2K: verify-only (already present).
- Toolbar: `soldsBtn`, `renderSolds()` + CSV parser + sort + download +
  editable cells, fetching `<market>_off_market.csv`.
- New repo files: `montrose_off_market.csv` … `riveroaks_off_market.csv`,
  header row only (the 14-column Heights header), zero data rows.
- RECONCILE markers + `applyReconcile` + both call sites, seeded
  `{"off":{},"relist":{},"pending":{}}`.
- The two Part 2 links.
- Per OPEN DECISION 4: the sync stack (namespaced), `offMarketEdits` bucket.
- **springvalley caution**: CLAUDE.md flags springvalley.html's build as
  not-understood (empty inspections, no permits json, yet fully sized).
  Resolve that known-issue *before* its port commit, per the standing rule.

Explicitly NOT in scope: any DATA/SEED_POINTS content, any real off-market
entries, any OUT_OF_ZONE lists for other markets. Machinery only.

**OPEN DECISION 6 (flagged, not decided — per your instruction)**: 6 separate
anchored-edit passes (CLAUDE.md's standing convention) vs factoring the shared
JS into one included `shared.js` to stop 7-way drift. Considerations, no
verdict: factoring ends the drift problem permanently and makes future features
1-file changes; but it is a large refactor of ALL 7 hand-authored files
(Heights included, and Heights has 486 lines of divergence to untangle), it
changes what "anchored edits" even means going forward, and it adds a runtime
file the RECONCILE/validation tooling doesn't currently know about. The
anchored-pass route is 6 mechanical passes now and drift risk forever. Your
call.

## Part 4 — Generalize refresh.py

Heights assumptions found: docstring line 2, `CSV_NAME='heights_off_market.csv'`
(:295), help text (:529), hardcoded `index.html` defaults (:524/527/530/532),
single `changes/` + `staging/` dirs (:21/:411). Geocode's hardwired
`Houston,TX` (:426) is fine citywide — untouched.

Proposal — mirror run_and_deploy.py's shape (MARKETS dicts + `--market`
filter, run_and_deploy.py:58–80, 129–138):

```py
MARKETS = {
  'heights':    {'html': 'index.html',     'csv': 'heights_off_market.csv',    'changes': 'changes'},
  'montrose':   {'html': 'montrose.html',  'csv': 'montrose_off_market.csv',   'changes': 'changes/montrose'},
  # … 5 more
}
```

- `--market heights` default (back-compat: Heights keeps `changes/` at root so
  existing history and index.json don't move; other markets get
  `changes/<market>/` with their own index.json). **OPEN DECISION 7**: accept
  the asymmetric layout, or migrate Heights history to `changes/heights/` in
  one commit for symmetry? Recommend asymmetric (no history churn).
- All of `diff` / `generate` / `csv` / `life-sync` / `pull-edits` take the
  market config; `validate_spliced` runs unchanged against the chosen html.
- `staging/` becomes `staging/<market>/` for non-Heights.
- Guardrails unchanged and universal: `git pull --ff-only` gate, full re-parse
  refusal, human-invoked only, never from cron.
- OUT_OF_ZONE stays Heights-only data; generalization adds no multi-market
  OUT_OF_ZONE handling.

## Implementation order — one commit per stage

Each commit: verify files landed in the commit, cache-busted curl of the live
site after Netlify rebuild, empty-commit nudge if the webhook drops.

1. **Links (Heights only)** — toolbar anchors + permit-popup link. Smallest,
   zero data risk, proves placement.
2. **Editable table, client side (Heights)** — offMarketEdits bucket in
   _sharedSlice/merge/export/save, editable cells in renderSolds, flush-on-
   close and flush-on-sort. Backend .gs change only if it doesn't already
   store the blob verbatim (verify first).
3. **Generator round-trip** — refresh.py `pull-edits` (per OPEN DECISIONS 1–2)
   + overlay-aware `cmd_csv` notes handling. Dry-run against current live
   overlay before committing.
4. **refresh.py generalization (Part 4)** — MARKETS table + `--market`;
   Heights behavior byte-identical when run with defaults (diff the outputs to
   prove it).
5.–10. **Market ports, one commit per market** (order: montrose, springbranch,
   timbergrove, westu, riveroaks, springvalley — springvalley last, after its
   build mystery is resolved). Each commit: anchored edits + header-only CSV +
   empty RECONCILE, then refresh.py `--market <m>` validation pass against the
   spliced file as the commit gate. If OPEN DECISION 6 lands on shared-JS
   instead, stages 5–10 collapse into a refactor plan that needs its own
   design pass first.
11. (final) **Parity sweep across all 7** — verify with a 7-file grep matrix
   (the same one used in this investigation) showing identical hit counts for
   every ported token.

## What this plan does not do

No DATA edits anywhere. No real off-market entries for the 6. No OUT_OF_ZONE
work. No hand-edits inside RECONCILE markers. No cron. No Netlify API path.
