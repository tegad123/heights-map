# 34DEV Market Intelligence — Phase 1 Scope
**From working map to product foundation**
Prepared for Spencer Huck · Thirty Four Ventures · August 2026

---

## Where we are

The maps work. Eight markets, redesigned UI live, classification corrected and geometry-verified, and as of this week every market updates itself: nightly permit pulls across 12 zip codes, weekly ingest with per-market deploys, Discord reporting, and a catch-up guard for missed runs.

What exists today is a very good internal tool. Phase 1 turns its foundation into a product foundation: data that lives in a database instead of inside a webpage, one codebase instead of eight copies, real user accounts, and infrastructure that does not depend on a laptop being awake. It also builds the MLS integration point now, so when Trestle API access clears, sold-comps data drops in without rework.

## What Phase 1 delivers

By the end of Phase 1:

- All property, permit, inspection, sale, and classification data lives in a hosted database with an API, not inside HTML files. Updating data no longer means editing and redeploying a webpage.
- One map application serves all markets. Adding market #9 is a config entry, not a copied file. A bug fix lands once.
- Login exists. Team members get edit access; clients get read-only views scoped to the markets they should see.
- The pull/ingest pipelines run in the cloud on a schedule, with the same Discord reporting — no dependency on any personal machine.
- An MLS adapter is built and running against the current manual HAR export files, so the day Trestle access arrives, it becomes a credential swap plus a field mapping — not a build.

What Phase 1 deliberately does not include: alerts/notifications, saved searches, exports, the Ask analyst, app-store packaging, and billing. Those are Phase 2/3 features that become straightforward once this foundation exists, and premature now.

## The work, in five tracks

### Track 1 — Database and API (the core move)

Stand up a hosted Postgres database (Supabase or equivalent) with tables for properties, permits, inspections, sales, classifications, and markets. Migrate the current DATA arrays from all eight HTML files into it — a one-time, verified migration with record-count and field-level checks against the live pages, using the same assert-the-delta discipline the pipeline already follows.

A thin API serves the map: records by market, filtered by product type, phase, and tags. Classification history is kept per record, so a label change is an auditable event rather than a string edit.

Everything downstream — the single codebase, client scoping, future alerts — reads from this.

### Track 2 — One application, markets as config

Replace the eight near-identical HTML files with one application that loads a market by configuration: name, zip codes, boundary ring, enabled features. The pipeline side already works this way (`market_config.py` is the single source of truth for pulls); this brings the frontend in line. The redesigned UI carries over as-is — this is a re-plumbing, not a re-design.

Sold/comps appears per-market automatically wherever sold data exists in the database, which resolves the current "4 tabs vs 5" inconsistency the right way: through data, not UI special-casing.

### Track 3 — Accounts and access

Authentication with two roles to start: **team** (edit mode, quarantine review, all markets) and **client** (read-only, scoped to assigned markets). The current edit mode and its Google Apps Script shared-edit backend are replaced by authenticated writes to the database. This is what makes it safe to hand a client a URL that is theirs.

### Track 4 — Pipelines to the cloud

Move the nightly pull, weekly ingest, and catch-up jobs from the MacBook's launchd to a cloud runner (the existing DigitalOcean droplet or scheduled GitHub Actions). Same market configs, same failure detection, same Discord reports. Ingest writes to the database instead of committing to HTML — which also ends the current coupling where every data update is a site deploy.

### Track 5 — MLS-ready sold-data adapter (built now, keyed later)

This is the "build around the API key" piece. Sold-comps ingestion becomes a two-layer design:

- **A normalizer** that maps any sold-data source into the database's sales schema (address, close date, price, sqft, DOM, list-vs-sold).
- **Source adapters** that feed it. Adapter #1, built and used immediately: the manual HAR CSV export you run today. Adapter #2, stubbed with its field mapping drafted from Trestle's RESO Web API documentation: the Trestle feed itself.

Until the key arrives, the manual pull stays — but it gets easier (drop the CSV in, the adapter ingests and validates it) and it gets **a built-in reminder**: the Sunday pipeline report flags any market whose newest sale is older than 21 days, so staleness nags you instead of relying on memory. When Trestle access clears (pending the Serhant broker-of-record introduction with HAR), adapter #2 gets credentials and a validation run, and manual pulls end. No rework anywhere else in the system.

## Sequencing and effort

The tracks run in this order, with working checkpoints throughout — the current site stays live and updated the entire time; cutover happens market-by-market only after each passes verification against its live page.

| Step | Work | Rough effort |
|---|---|---|
| 1 | Database schema + migration of all 8 markets, verified | 1–1.5 weeks |
| 2 | API + single-codebase map reading from it, Heights first, then remaining markets | 2–3 weeks |
| 3 | Auth + roles, replace edit backend | 1 week |
| 4 | Pipelines to cloud, writing to DB | 1 week |
| 5 | Sold-data normalizer + HAR-CSV adapter + staleness reminder; Trestle adapter stubbed | 3–4 days |

Total: roughly **6–8 weeks** of focused work at current engagement pace, with the map never going dark. Estimates are for planning, not commitments; steps 1–2 carry the most uncertainty because migration verification is where the care goes.

## Running costs (new)

- Hosted database + auth (Supabase tier or equivalent): ~$25/mo to start
- Cloud pipeline runner: $0–12/mo (existing droplet or GitHub Actions free tier likely covers it)
- Basemap: currently on CARTO's keyless vector tiles — commercial-use terms to be confirmed; budget up to ~$150/mo if a paid basemap plan is required for a commercial product
- Trestle/MLS feed: per HAR's pricing once access clears

## Decisions needed from Spencer

1. **Who is the first customer** — your own clients as a service differentiator, or external agents/investors as a paid product? Phase 1 serves both, but it decides what Phase 2 builds first (alerts and polish vs. multi-tenancy and billing).
2. **Broker-of-record introduction to HAR** under Serhant (contact: Caroline Cervantes, IDX@har.com) — this is the only blocker on Trestle, and Track 5 makes the payoff immediate when it clears.
3. **Entity and IP structure** for the product — which entity owns and sells it, and how the build is engaged. Worth settling before Phase 1 starts rather than after it ships.

## Open items carried from the current system (tracked, not blockers)

Spring Valley pipeline wiring · automatic classification of new permit pins (evidence stack built, not yet wired into ingest) · per-plat classification thresholds (unlocks ~55 held records) · 5 quarantined geocode cases · phase-2 UI screens (Pipeline view, dark mode).
