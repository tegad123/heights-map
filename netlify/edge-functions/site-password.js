// Password gate for the whole site. Every request needs the hm_auth session
// cookie (set by the sign-in form) or HTTP Basic auth carrying SITE_PASSWORD.
// With SITE_PASSWORD unset the site fails closed: nothing is served.
import { COOKIE, MAX_AGE, isAuthorized, same, tokenFor } from '../lib/site-auth.mjs';

const LOGIN = '/__login';
const LOGOUT = '/__logout';

function sitePassword() {
  return globalThis.Netlify?.env?.get('SITE_PASSWORD') || '';
}

function safeNext(value) {
  const next = typeof value === 'string' ? value : '/';
  return next.startsWith('/') && !next.startsWith('//') && !next.startsWith('/\\') ? next : '/';
}

function esc(s) {
  return s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const HEADERS = {
  'content-type': 'text/html; charset=utf-8',
  'cache-control': 'no-store',
  'x-robots-tag': 'noindex, nofollow',
};

function page(next, { error = '', status = 401 } = {}) {
  const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Sign in</title>
<style>
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
    background:#f4f1ea;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#1d1d1b}
  form{width:min(340px,90vw);background:#fff;border-radius:14px;padding:28px;box-shadow:0 8px 30px rgba(0,0,0,.08)}
  h1{margin:0 0 4px;font-size:20px}
  p{margin:0 0 18px;color:#6b6b66;font-size:14px}
  input{width:100%;padding:11px 12px;font-size:15px;border:1px solid #d6d2c8;border-radius:9px;outline:none}
  input:focus{border-color:#cf2230;box-shadow:0 0 0 3px rgba(207,34,48,.12)}
  button{margin-top:12px;width:100%;padding:11px;font-size:15px;font-weight:600;border:0;border-radius:9px;
    background:#1d1d1b;color:#fff;cursor:pointer}
  .err{margin:10px 0 0;color:#cf2230;font-size:13px}
</style></head>
<body><form method="post" action="${LOGIN}">
  <h1>CQ Houston supply maps</h1>
  <p>Enter the password to continue.</p>
  <input type="password" name="password" autocomplete="current-password" placeholder="Password" autofocus required>
  <input type="hidden" name="next" value="${esc(next)}">
  <button type="submit">Sign in</button>
  ${error ? `<div class="err">${esc(error)}</div>` : ''}
</form></body></html>`;
  return new Response(html, { status, headers: HEADERS });
}

function cookie(value, maxAge) {
  return `${COOKIE}=${value}; Path=/; Max-Age=${maxAge}; HttpOnly; Secure; SameSite=Lax`;
}

export default async (request, context) => {
  const url = new URL(request.url);
  const password = sitePassword();
  if (!password) {
    return new Response('Site password is not configured (set SITE_PASSWORD in Netlify).',
      { status: 503, headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' } });
  }

  if (url.pathname === LOGOUT) {
    return new Response(null, { status: 303, headers: { location: LOGIN, 'set-cookie': cookie('', 0), 'cache-control': 'no-store' } });
  }

  if (url.pathname === LOGIN) {
    if (request.method !== 'POST') return page(safeNext(url.searchParams.get('next')), { status: 200 });
    const form = await request.formData().catch(() => null);
    const next = safeNext(form?.get('next'));
    if (!same(String(form?.get('password') ?? ''), password)) {
      return page(next, { error: 'Wrong password.' });
    }
    return new Response(null, {
      status: 303,
      headers: { location: next, 'set-cookie': cookie(await tokenFor(password), MAX_AGE), 'cache-control': 'no-store' },
    });
  }

  if (await isAuthorized(request, password)) return context.next();

  if (request.method === 'GET' && (request.headers.get('accept') || '').includes('text/html')) {
    return page(url.pathname + url.search);
  }
  return new Response('Unauthorized', {
    status: 401,
    headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' },
  });
};

export const config = { path: '/*' };
