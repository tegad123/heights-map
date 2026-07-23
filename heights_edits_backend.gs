// Heights Map — shared edits backend (Google Apps Script)
// Stores the map's edit overlay (product/stage changes, moved pins, notes, pair overrides)
// in a Drive file so every viewer sees Spencer's edits live. Last write wins.
//
// SETUP (3 minutes, one time):
// 1. Go to script.google.com -> New project. Delete the default code, paste this file.
// 2. Save. Click Deploy -> New deployment -> type: Web app.
//    - Description: heights map edits
//    - Execute as: Me
//    - Who has access: Anyone
// 3. Click Deploy, authorize with the Google account, copy the Web app URL (ends in /exec).
// 4. Give that URL to Claude/Claude Code to paste into index.html's REMOTE_EDITS_URL constant.
//
// The edits live in a Drive file named heights_map_edits.json in this account's My Drive.
// Every write also appends a timestamped backup (last 50 kept) so nothing is ever lost.

const FILE_NAME = 'heights_map_edits.json';
const BACKUP_PREFIX = 'heights_map_edits_backup_';
const MAX_BACKUPS = 50;

function _file() {
  const it = DriveApp.getFilesByName(FILE_NAME);
  return it.hasNext() ? it.next() : DriveApp.createFile(FILE_NAME, '{}', 'application/json');
}

function doGet() {
  return ContentService
    .createTextOutput(_file().getBlob().getDataAsString())
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
  const f = _file();
  // timestamped backup of the previous state
  try {
    const prev = f.getBlob().getDataAsString();
    if (prev && prev !== '{}') {
      DriveApp.createFile(BACKUP_PREFIX + new Date().toISOString().replace(/[:.]/g, '-') + '.json', prev, 'application/json');
      // prune old backups
      const backups = [];
      const it = DriveApp.searchFiles('title contains "' + BACKUP_PREFIX + '"');
      while (it.hasNext()) backups.push(it.next());
      backups.sort(function (a, b) { return b.getDateCreated() - a.getDateCreated(); });
      for (let i = MAX_BACKUPS; i < backups.length; i++) backups[i].setTrashed(true);
    }
  } catch (err) { /* backup failure never blocks a save */ }
  f.setContent(body);
  return ContentService.createTextOutput(JSON.stringify({ ok: true, bytes: body.length, at: new Date().toISOString() }))
    .setMimeType(ContentService.MimeType.JSON);
}
