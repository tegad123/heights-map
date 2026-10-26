// Site password check shared by the edge gate and the Ask-the-Map function.
// The password lives only in the SITE_PASSWORD Netlify environment variable:
// this repo is public, so it must never be committed. The session cookie holds
// a SHA-256 of the password, so changing SITE_PASSWORD signs everyone out.

export const COOKIE = 'hm_auth';
export const MAX_AGE = 60 * 60 * 24 * 30;

export async function tokenFor(password) {
  const bytes = new TextEncoder().encode('heights-map-session:' + password);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
}

export function same(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export function cookieValue(request, name = COOKIE) {
  for (const part of (request.headers.get('cookie') || '').split(';')) {
    const [k, ...v] = part.trim().split('=');
    if (k === name) return v.join('=');
  }
  return null;
}

function basicPassword(request) {
  const h = request.headers.get('authorization') || '';
  if (!h.startsWith('Basic ')) return null;
  try {
    const decoded = atob(h.slice(6));
    const i = decoded.indexOf(':');
    return i < 0 ? null : decoded.slice(i + 1);
  } catch {
    return null;
  }
}

// Browser sessions carry the cookie; scripts (the weekly ingest's live-page
// check) send HTTP Basic auth with any username.
export async function isAuthorized(request, password) {
  if (!password) return false;
  if (same(cookieValue(request), await tokenFor(password))) return true;
  const basic = basicPassword(request);
  return basic !== null && same(basic, password);
}
