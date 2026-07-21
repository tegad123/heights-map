# heights-map

Supply-timing maps for CQ Houston. Static site, deployed to Netlify
via CI from the GitHub main branch.

## Hard rules — do not violate

- NEVER use `--mode netlify`. It performs an atomic wipe of the site.
  Always use `--mode git`.
- Deployment is `git push` to main only. Netlify CI rebuilds from there.
  Do not deploy by any other path.
- After any commit intended to deploy, verify the files actually landed
  in the commit. Do not assume.
- If a push does not trigger a Netlify rebuild, force it with an empty
  commit. The webhook drops pushes occasionally.
- Never regenerate a market's HTML from empty or missing input files.
  Check inputs are non-empty first.

## Pipeline rules

- Adding a new market requires updating the MARKETS list in
  run_and_deploy.py. Nothing else picks it up automatically.
- Phase classification is monotonic furthest-passed. Failed and pending
  inspections never count toward phase. Phase never moves backwards.
- HAR exports use the address-led no-header-row template. The stats-style
  MLS view lacks an Address column and will not parse.
- Census batch geocoding runs locally, not in any sandbox.

## Live markets

Heights, Montrose, River Oaks, Spring Branch, Spring Valley Village,
Timbergrove/Lazybrook, West University.

## Known issues

- inspections_springvalley.json is `{}` and there is no
  springvalley_permits.json, yet springvalley.html is fully sized.
  Determine how it is built before touching it.
- upperkirby_holdout.json exists with no corresponding HTML. Status unknown.

## Working style

- Verify root cause from actual file contents or logs before writing a fix.
- Overwrite whole files rather than doing in-place string surgery.
- Show me the plan before running anything that writes to committed files.
