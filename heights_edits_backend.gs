// CQ Houston maps — shared edits backend (Google Apps Script)
// Stores each market map's edit overlay (product/stage changes, moved pins,
// notes, pair overrides, off-market table corrections) in a per-market Drive
// file so every viewer sees Spencer's edits live. Last write wins per market.
//
// MARKET ROUTING: ?market=<name> on GET, and/or a "market" field in the POST
// body. Unknown or missing market falls back to 'heights', which keeps the
// original single-file contract — existing Heights clients that predate
// namespacing keep working unchanged.
//
// SETUP (one time) / REDEPLOY (after edits):
// 1. script.google.com -> open the existing project (or New project), paste this file.
// 2. Deploy -> Manage deployments -> Edit (pencil) -> Version: New version -> Deploy.
//    (Editing the EXISTING deployment keeps the /exec URL stable. Only a brand-new
//    deployment mints a new URL.)
// 3. Execute as: Me. Who has access: Anyone.
// 4. The /exec URL goes into each market html's REMOTE_EDITS_URL constant.
//
// Files live in this account's My Drive: heights_map_edits.json,
// montrose_map_edits.json, ... Every write appends a timestamped backup
// (last 50 kept per market) so nothing is ever lost.

const MARKETS = ['heights', 'montrose', 'springbranch', 'springvalley',
                 'timbergrove', 'westu', 'riveroaks'];
const MAX_BACKUPS = 50;

function _marketOf(e, parsed) {
  const m = (e && e.parameter && e.parameter.market) ||
            (parsed && parsed.market) || 'heights';
  return MARKETS.indexOf(m) >= 0 ? m : 'heights';
}

function _fileFor(market) {
  const name = market + '_map_edits.json';
  const it = DriveApp.getFilesByName(name);
  return it.hasNext() ? it.next() : DriveApp.createFile(name, '{}', 'application/json');
}

function doGet(e) {
  return ContentService
    .createTextOutput(_fileFor(_marketOf(e, null)).getBlob().getDataAsString())
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  const body = e.postData && e.postData.contents ? e.postData.contents : '{}';
  // sanity: must be JSON and under 2MB
  let parsed;
  try { parsed = JSON.parse(body); } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: 'invalid json' }))
      .setMimeType(ContentService.MimeType.JSON);
  }
  if (body.length > 2 * 1024 * 1024) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: 'too large' }))
      .setMimeType(ContentService.MimeType.JSON);
  }
  const market = _marketOf(e, parsed);
  const backupPrefix = market + '_map_edits_backup_';
  const f = _fileFor(market);
  // timestamped backup of the previous state
  try {
    const prev = f.getBlob().getDataAsString();
    if (prev && prev !== '{}') {
      DriveApp.createFile(backupPrefix + new Date().toISOString().replace(/[:.]/g, '-') + '.json', prev, 'application/json');
      // prune old backups (per market)
      const backups = [];
      const it = DriveApp.searchFiles('title contains "' + backupPrefix + '"');
      while (it.hasNext()) backups.push(it.next());
      backups.sort(function (a, b) { return b.getDateCreated() - a.getDateCreated(); });
      for (let i = MAX_BACKUPS; i < backups.length; i++) backups[i].setTrashed(true);
    }
  } catch (err) { /* backup failure never blocks a save */ }
  f.setContent(body);
  return ContentService.createTextOutput(JSON.stringify({ ok: true, market: market, bytes: body.length, at: new Date().toISOString() }))
    .setMimeType(ContentService.MimeType.JSON);
}
