const SHELL_CACHE = 'map-app-shell-v3';
const PARCEL_CACHE = 'map-app-parcels-v3';
const PACK_CACHE = 'map-app-offline-packs-v1';
const EXTERNAL_CACHE = 'map-app-map-engine-v1';
const WORKER_ORIGIN = 'https://mapapp-offline-packs.rabbi-5fc.workers.dev';
const APP_SHELL = ['./', './index.html', './parcel-data/index.json', './offline-controls.js', './offline-map.js'];

self.addEventListener('install', event => event.waitUntil(caches.open(SHELL_CACHE).then(cache => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('map-app-') && ![SHELL_CACHE, PARCEL_CACHE, PACK_CACHE, EXTERNAL_CACHE].includes(key)).map(key => caches.delete(key)))).then(() => self.clients.claim())));

const send = (client, message) => client && client.postMessage && client.postMessage(message);
const decoratePage = response => response.text().then(html => new Response(html.replace('</body>', '<script src="offline-controls.js"></script><script src="offline-map.js"></script></body>'), { headers: { 'Content-Type': 'text/html; charset=utf-8' } }));
const rangeFromCachedPack = async (request, cached) => {
  const range = request.headers.get('range');
  if (!range) return cached;
  const match = /bytes=(\d+)-(\d*)/.exec(range);
  if (!match) return cached;
  const bytes = await cached.arrayBuffer(), start = Number(match[1]), end = Math.min(match[2] ? Number(match[2]) : bytes.byteLength - 1, bytes.byteLength - 1);
  if (start > end) return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${bytes.byteLength}` } });
  return new Response(bytes.slice(start, end + 1), { status: 206, headers: { 'Content-Type': 'application/octet-stream', 'Content-Range': `bytes ${start}-${end}/${bytes.byteLength}`, 'Content-Length': String(end - start + 1), 'Accept-Ranges': 'bytes' } });
};

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin === WORKER_ORIGIN && url.pathname.startsWith('/download/')) {
    event.respondWith(caches.open(PACK_CACHE).then(async cache => { const cached = await cache.match(url.href); return cached ? rangeFromCachedPack(request, cached) : fetch(request); }));
    return;
  }
  if (url.origin === 'https://unpkg.com' || url.origin === 'https://cdn.jsdelivr.net') {
    event.respondWith(caches.open(EXTERNAL_CACHE).then(async cache => (await cache.match(request)) || fetch(request).then(response => { if (response.ok) cache.put(request, response.clone()); return response; })));
    return;
  }
  if (url.origin !== self.location.origin) return;
  const isPage = request.mode === 'navigate' || url.pathname.endsWith('/index.html') || url.pathname.endsWith('/mapapp/');
  if (isPage) {
    event.respondWith(caches.open(SHELL_CACHE).then(async cache => {
      const cached = await cache.match(request);
      const response = cached || await fetch(request).then(response => { if (response.ok) cache.put(request, response.clone()); return response; });
      return decoratePage(response);
    }));
    return;
  }
  const parcel = url.pathname.includes('/parcel-data/');
  event.respondWith(caches.open(parcel ? PARCEL_CACHE : SHELL_CACHE).then(async cache => (await cache.match(request)) || fetch(request).then(response => { if (response.ok) cache.put(request, response.clone()); return response; })));
});

self.addEventListener('message', event => {
  const data = event.data || {}, client = event.source;
  if (data.type === 'clear-parcels') { event.waitUntil(caches.delete(PARCEL_CACHE).then(() => send(client, { type: 'cleared' }))); return; }
  if (data.type === 'clear-map-pack') { event.waitUntil(caches.delete(PACK_CACHE).then(() => send(client, { type: 'map-cleared' }))); return; }
  if (data.type === 'cache-map-pack' && data.url && data.accessCode) {
    event.waitUntil(caches.open(PACK_CACHE).then(async cache => { const response = await fetch(data.url, { headers: { 'X-Offline-Access-Code': data.accessCode } }); if (!response.ok) throw new Error('Map package download failed'); await cache.put(data.url, response); send(client, { type: 'map-saved', url: data.url }); }).catch(() => send(client, { type: 'map-error' })));
    return;
  }
  if (data.type === 'cache-map-engine' && Array.isArray(data.urls)) {
    event.waitUntil(caches.open(EXTERNAL_CACHE).then(async cache => { await Promise.all(data.urls.map(async url => { const response = await fetch(url); if (response.ok) await cache.put(url, response); })); send(client, { type: 'engine-saved' }); }).catch(() => send(client, { type: 'map-error' })));
    return;
  }
  if (data.type !== 'download-parcels' || !Array.isArray(data.urls)) return;
  event.waitUntil(caches.open(PARCEL_CACHE).then(async cache => { let saved = 0; for (const url of data.urls) { try { const response = await fetch(url); if (response.ok) { await cache.put(url, response); saved++; } } catch (_) { /* keep going */ } send(client, { type: 'progress', saved, total: data.urls.length }); } send(client, { type: 'complete', saved, total: data.urls.length }); }));
});
