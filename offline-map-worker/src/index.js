const cors = {
  'Access-Control-Allow-Origin': 'https://chabadchagrin.github.io',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Offline-Access-Code',
};
const reply = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
const allowedArea = (box) => Array.isArray(box) && box.length === 4 && box.every(Number.isFinite) && box[0] < box[2] && box[1] < box[3] && box[0] >= -82 && box[2] <= -80 && box[1] >= 40.5 && box[3] <= 42 && (box[2] - box[0]) * (box[3] - box[1]) <= 0.04;
export default { async fetch(request, env) {
  if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
  const url = new URL(request.url);
  if (request.headers.get('X-Offline-Access-Code') !== env.OFFLINE_ACCESS_CODE) return reply({ error: 'Access code required.' }, 401);
  if (request.method === 'GET' && url.pathname.startsWith('/status/')) {
    const id = url.pathname.split('/').pop(); const object = await env.PACKS.get('status/' + id + '.json');
    return object ? new Response(object.body, { headers: { ...cors, 'Content-Type': 'application/json' } }) : reply({ status: 'building' }, 202);
  }
  if (request.method === 'GET' && url.pathname.startsWith('/download/')) {
    const id = url.pathname.split('/').pop(); const object = await env.PACKS.get('packs/' + id + '.pmtiles');
    return object ? new Response(object.body, { headers: { ...cors, 'Content-Type': 'application/octet-stream', 'Content-Disposition': 'attachment; filename="offline-map-' + id + '.pmtiles"' } }) : reply({ error: 'Package not ready.' }, 404);
  }
  if (request.method !== 'POST' || url.pathname !== '/packs') return reply({ error: 'Not found.' }, 404);
  const { bbox, maxZoom = 14 } = await request.json();
  if (!allowedArea(bbox) || !Number.isInteger(maxZoom) || maxZoom < 10 || maxZoom > 14) return reply({ error: 'Choose a smaller area inside northeast Ohio.' }, 400);
  const id = crypto.randomUUID();
  const response = await fetch('https://api.github.com/repos/' + env.GITHUB_REPOSITORY + '/actions/workflows/build-offline-map.yml/dispatches', { method: 'POST', headers: { Authorization: 'Bearer ' + env.GITHUB_TOKEN, Accept: 'application/vnd.github+json', 'Content-Type': 'application/json', 'User-Agent': 'mapapp-offline-packs' }, body: JSON.stringify({ ref: 'main', inputs: { pack_id: id, bbox: bbox.join(','), max_zoom: String(maxZoom) } }) });
  if (!response.ok) return reply({ error: 'Could not start the map package.' }, 502);
  return reply({ id, status: 'building' }, 202);
}};
