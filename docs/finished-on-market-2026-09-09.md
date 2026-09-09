# Finished on Market — 2026-09-09

Added the explicitly requested row directly after Complete under each construction product. It is an overlapping subset: Complete construction AND current Active market evidence. The existing Other → On the Market (building) filter remains 14. No top-level Market Status block or five-status breakdown under Complete.

| Product | Complete | Finished on Market (included in Complete) |
|---|---:|---:|
| Single Lot | 12 | 4 |
| Split Lot | 28 | 9 |
| Common Driveway | 9 | 0 |
| Total | 49 | 13 |

The 13 named homes exactly match the reconciliation’s Complete-and-Active member set. Counts follow the existing construction product grouping (`typeKeyOf(pin)`). In particular, 122 E 4th remains Split Lot in the construction panel; its HAR lot classification is Single Lot. No product data was changed. Named active members are counted individually, including the active member of a paired pin, without treating unnamed represented homes as active.

## Verified member IDs

| Member ID | Rendered pin ID | Construction product |
|---|---|---|
| act_1520-w-21st-st-unit-a | act_1520-w-21st-st-unit-b | Split Lot |
| act_112-e-27th-street | pmt_112-e-27th-st-a-77008 | Split Lot |
| act_1322-lawrence-street | act_1322-lawrence-street | Split Lot |
| act_409-walton-street-unit-b | pmt_409-walton-st-a-77009 | Split Lot |
| act_902-e-25 | act_902-e-25 | Single Lot |
| act_122-e-4 | act_122-e-4 | Split Lot |
| act_609-e-25 | act_609-e-25 | Single Lot |
| act_212-e-24 | act_212-e-24 | Single Lot |
| act_715-merrill | act_715-merrill | Single Lot |
| act_1303-cordell-street-unit-b | act_1303-cordell-street-unit-b | Split Lot |
| act_835-w-25th-street | act_835-w-25th-street | Split Lot |
| act_609-w-27th-street | act_609-w-27th-street | Split Lot |
| act_335-harvard-street | act_335-harvard-street | Split Lot |

## Commands and evidence

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/market_status_check.py --three
/Users/nemoclaw/insp-venv/bin/python -B tests/full_timeline_check.py
```

Actual command output: [local market checks](finished-local-validation-2026-09-09.txt), [construction checks](finished-construction-validation-2026-09-09.txt). The browser invokes each new row and checkbox and checks the selected pin set. All eight pages are checked. DATA, RECONCILE, and inline construction/timeline scripts are byte-identical to the construction baseline. Market ingest is byte-identical on repeated invocation.

715 Merrill remains Complete + Active (MLS 88557637, 8 DOM), with terminated MLS 50361472 at 174 DOM in its popup history. Snapshot remains 131 construction forecast − 3 terminated = 128. Custom 19, Sold Off Market 1, deeds 139, sold comps 767.

All 213 homes selected by the existing Under Construction filter have exactly one phase. The invoked query is:

```js
const uc=DATA.filter(r=>matchSel(pt(r.id).tags,'G:uc',r.id));
({homes:uc.reduce((n,r)=>n+UW(r.id),0),
missingPhaseIds:uc.filter(r=>!homePhase(r.id)).map(r=>r.id),
invalidPhaseTagIds:uc.filter(r=>CONSTRUCTION_PHASES.filter(ph=>pt(r.id).tags.includes(ph)).length!==1).map(r=>r.id)})
```

Output: `{homes:213, missingPhaseIds:[], invalidPhaseTagIds:[]}`.

Application commit `fdb6009` contains only `market_status.js` and `tests/market_status_check.py`: 43 insertions, 3 deletions. No HTML or DATA files changed. Commit contents verified with `git show --format=fuller --stat HEAD`. Deployment uses `git push origin main`.


Live command:

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/market_status_check.py --three --live https://tangerine-sorbet-eca5f5.netlify.app
```

[Actual live output](finished-live-validation-2026-09-09.txt): three identical runs, each with SHA256 `188f363577612b214dfe81a3d2c8d97dd82ff534d226aa737f5ebab0436266f7`, also identical to all three local runs. Each live run verifies deployed JavaScript and the market snapshot byte-for-byte, all eight pages, new filter membership, the retained 14-home overlap, and four popup fixtures. Construction suite: three identical runs, 20,706/20,706 phase checks, 183/183 browser checks, 7,283 base-timeline pairs, zero violations.
