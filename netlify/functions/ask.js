// Ask-the-Map — Netlify Function proxy to the Anthropic API.
// The API key lives in a Netlify environment variable (ANTHROPIC_API_KEY),
// never in the browser. The client sends {question, context, history};
// context is a compact dump of the live map dataset built client-side.

const SYSTEM = `You are the supply analyst for a Houston Heights new-construction map used by a real-estate developer (infill lot acquisition, lot splits, new builds in the Heights / Shady Acres).

You will receive the map's full dataset. Groups: active_on_market (listed homes — the competition), under_construction (phase = foundation/framing/dried_in/finishing, months_to_market estimates completion), permit_queued (permitted, not started), deed_lot (recently sold lots, pre-construction — the future pipeline).

Rules:
- Answer ONLY from the dataset provided. If it can't answer the question, say so plainly.
- Be concise and direct. Lead with the answer/number, then the supporting addresses or breakdown.
- Cite specific addresses, prices, phases, and months when relevant.
- For competition questions, compare by product type (Single Lot vs Split Lot), price band, and timing.
- For supply-timing questions, use months_to_market (0mo = listed now).
- Phases come from City of Houston inspection records, which can lag the job site by days to a couple of weeks; note this only when it matters to the answer.
- Plain text only — no markdown formatting.`;

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: JSON.stringify({ answer: 'POST only' }) };
  if (!process.env.ANTHROPIC_API_KEY) return { statusCode: 500, body: JSON.stringify({ answer: 'Server not configured: ANTHROPIC_API_KEY is missing in Netlify environment variables.' }) };
  try {
    const { question, context, history } = JSON.parse(event.body || '{}');
    if (!question) return { statusCode: 400, body: JSON.stringify({ answer: 'No question provided.' }) };
    const messages = (Array.isArray(history) ? history.filter(m => m && m.role && m.content) : [])
      .slice(-8)
      .concat([{ role: 'user', content: question }]);
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: 1500,
        system: SYSTEM + '\n\n=== MAP DATASET ===\n' + (context || '(no dataset sent)'),
        messages
      })
    });
    const j = await r.json();
    if (!r.ok) {
      const msg = (j && j.error && j.error.message) || ('API error HTTP ' + r.status);
      return { statusCode: 502, body: JSON.stringify({ answer: 'AI service error: ' + msg }) };
    }
    const text = (j.content || []).map(c => c.text || '').join('').trim();
    return { statusCode: 200, headers: { 'content-type': 'application/json' }, body: JSON.stringify({ answer: text || 'Empty response from model.' }) };
  } catch (e) {
    return { statusCode: 500, body: JSON.stringify({ answer: 'Server error: ' + e.message }) };
  }
};
