(() => {
  const locationToast = document.querySelector('#status');
  if (locationToast) {
    const clearLocationToast = () => {
      if (locationToast.textContent === 'Your location is shown in blue.') locationToast.textContent = '';
    };
    new MutationObserver(clearLocationToast).observe(locationToast, { childList: true, characterData: true, subtree: true });
    clearLocationToast();
  }
  const WORKER = 'https://mapapp-offline-packs.rabbi-5fc.workers.dev';
  const MAPLIBRE_JS = 'https://unpkg.com/maplibre-gl@5.12.0/dist/maplibre-gl.js';
  const MAPLIBRE_CSS = 'https://unpkg.com/maplibre-gl@5.12.0/dist/maplibre-gl.css';
  const PMTILES_JS = 'https://unpkg.com/pmtiles@4.3.0/dist/pmtiles.js';
  const saved = () => JSON.parse(localStorage.getItem('mapapp-offline-pack') || 'null');
  const save = value => localStorage.setItem('mapapp-offline-pack', JSON.stringify(value));
  const text = value => String(value || '').replace(/[&<>'"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c]));
  const notice = message => { const status = document.querySelector('#status'); if (status) status.textContent = message; };
  const controller = () => navigator.serviceWorker && navigator.serviceWorker.controller;
  let offlineMap, parcelIndex, loadedKeys = new Set(), parcelFeatures = [];

  const panel = document.createElement('div');
  panel.className = 'offline-map-panel';
  panel.innerHTML = '<button class="save-map" type="button">Download this map area</button><button class="open-map" type="button">Open saved offline map</button><button class="clear-map" type="button">Clear saved map</button>';
  const style = document.createElement('style');
  style.textContent = '.offline-map-panel{position:fixed;z-index:4;right:16px;bottom:248px;display:grid;gap:6px;max-width:180px;font:12px Arial}.offline-map-panel button{border:0;border-radius:10px;padding:9px 10px;background:#fff;color:#102a43;box-shadow:0 3px 12px #1235;font-weight:bold}.offline-map-panel .save-map{background:#1a73e8;color:#fff}.offline-map-panel .clear-map{color:#9b1c1c}@media(min-width:700px){.offline-map-panel{right:24px}}#offline-map-view{position:fixed;z-index:20;inset:0;background:#fff;display:none}#offline-map-canvas{position:absolute;inset:0}.offline-map-close{position:absolute;z-index:2;top:15px;right:15px;border:0;border-radius:12px;background:#fff;padding:11px 13px;font:bold 14px Arial;box-shadow:0 2px 10px #1235}.offline-map-label{position:absolute;z-index:2;left:14px;bottom:18px;max-width:70%;padding:8px 11px;border-radius:12px;background:#102a43eE;color:#fff;font:12px Arial}';
  document.head.appendChild(style); document.body.appendChild(panel);
  const view = document.createElement('div');
  view.id = 'offline-map-view';
  view.innerHTML = '<div id="offline-map-canvas"></div><button class="offline-map-close" type="button">Back to regular map</button><div class="offline-map-label">Offline map and saved parcels</div>';
  document.body.appendChild(view);

  const loadScript = url => new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${url}"]`)) return resolve();
    const script = document.createElement('script'); script.src = url; script.onload = resolve; script.onerror = reject; document.head.appendChild(script);
  });
  const loadEngine = async () => {
    if (!document.querySelector(`link[href="${MAPLIBRE_CSS}"]`)) { const link = document.createElement('link'); link.rel = 'stylesheet'; link.href = MAPLIBRE_CSS; document.head.appendChild(link); }
    await loadScript(MAPLIBRE_JS); await loadScript(PMTILES_JS);
    if (!window.maplibregl || !window.pmtiles) throw new Error('Map display components could not be loaded');
  };
  const workerFetch = (path, options = {}) => {
    const code = localStorage.getItem('mapapp-offline-code') || prompt('Enter your offline-map access code. You only need this when downloading a new area.');
    if (!code) throw new Error('Access code needed');
    localStorage.setItem('mapapp-offline-code', code);
    return fetch(WORKER + path, { ...options, headers: { ...(options.headers || {}), 'X-Offline-Access-Code': code } });
  };
  const mapBounds = () => {
    if (!window.map || !map.getBounds()) throw new Error('Wait for the regular map to finish loading, then try again.');
    const b = map.getBounds(), ne = b.getNorthEast(), sw = b.getSouthWest();
    return [sw.lng(), sw.lat(), ne.lng(), ne.lat()];
  };
  const createPack = async () => {
    const control = controller(); if (!control) throw new Error('Refresh this page once, then try again.');
    const bbox = mapBounds();
    if (!confirm('Download the map currently on screen for offline use? Keep the area reasonably small.')) return;
    panel.querySelector('.save-map').disabled = true; notice('Starting your offline map download…');
    const start = await workerFetch('/packs', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ bbox, maxZoom: 14 }) });
    if (!start.ok) throw new Error('Could not start this map area. Zoom in a little and try again.');
    const job = await start.json();
    for (let attempt = 0; attempt < 80; attempt++) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      const check = await workerFetch('/status/' + job.id);
      if (check.status === 202) { notice('Building your map area…'); continue; }
      if (!check.ok) throw new Error('The map package did not finish.');
      const result = await check.json();
      if (result.status === 'ready') {
        const url = WORKER + '/download/' + job.id;
        control.postMessage({ type: 'cache-map-engine', urls: [MAPLIBRE_JS, MAPLIBRE_CSS, PMTILES_JS] });
        control.postMessage({ type: 'cache-map-pack', url, accessCode: localStorage.getItem('mapapp-offline-code') });
        save({ id: job.id, url, bbox, created: Date.now() });
        notice('Saving the map onto this phone…'); return;
      }
    }
    throw new Error('Map build took too long. Try again later.');
  };
  const updateParcels = async () => {
    if (!offlineMap || !parcelIndex) return;
    const b = offlineMap.getBounds(), s = parcelIndex.cellSize, need = [];
    for (let x = Math.floor(b.getWest() / s) - 1; x <= Math.floor(b.getEast() / s) + 1; x++) for (let y = Math.floor(b.getSouth() / s) - 1; y <= Math.floor(b.getNorth() / s) + 1; y++) need.push(`${x}_${y}`);
    const fresh = need.filter(key => !loadedKeys.has(key) && parcelIndex.lookup.has(key));
    if (!fresh.length) return;
    await Promise.all(fresh.map(async key => { const entry = parcelIndex.lookup.get(key); try { const data = await fetch(entry.url.replace(/^\//, '')).then(r => r.json()); parcelFeatures.push(...data.features); loadedKeys.add(key); } catch (_) { /* parcel data was not saved */ } }));
    offlineMap.getSource('parcels').setData({ type: 'FeatureCollection', features: parcelFeatures });
  };
  const showOfflineMap = async () => {
    const pack = saved(); if (!pack) throw new Error('Download a map area first.');
    view.style.display = 'block'; notice('Opening saved offline map…');
    await loadEngine();
    if (offlineMap) { offlineMap.resize(); return; }
    const protocol = new pmtiles.Protocol(); maplibregl.addProtocol('pmtiles', protocol.tile);
    const center = [(pack.bbox[0] + pack.bbox[2]) / 2, (pack.bbox[1] + pack.bbox[3]) / 2];
    offlineMap = new maplibregl.Map({ container: 'offline-map-canvas', center, zoom: 14, style: { version: 8, sources: { basemap: { type: 'vector', url: 'pmtiles://' + pack.url }, parcels: { type: 'geojson', data: { type: 'FeatureCollection', features: [] } } }, layers: [
      { id: 'background', type: 'background', paint: { 'background-color': '#edf2f7' } },
      { id: 'landuse', type: 'fill', source: 'basemap', 'source-layer': 'landuse', paint: { 'fill-color': '#e3ecd6', 'fill-opacity': .7 } },
      { id: 'water', type: 'fill', source: 'basemap', 'source-layer': 'water', paint: { 'fill-color': '#b8d9ed' } },
      { id: 'buildings', type: 'fill', source: 'basemap', 'source-layer': 'buildings', paint: { 'fill-color': '#dedbd2', 'fill-opacity': .75 } },
      { id: 'roads', type: 'line', source: 'basemap', 'source-layer': 'roads', paint: { 'line-color': '#ffffff', 'line-width': ['interpolate', ['linear'], ['zoom'], 8, .5, 14, 3, 18, 8], 'line-outline-color': '#cbd5e0' } },
      { id: 'parcels-fill', type: 'fill', source: 'parcels', paint: { 'fill-color': '#0f766e', 'fill-opacity': .04 } },
      { id: 'parcels-line', type: 'line', source: 'parcels', paint: { 'line-color': '#0f766e', 'line-width': 1, 'line-opacity': .65 } }
    ] } });
    offlineMap.on('load', async () => {
      parcelIndex = await fetch('parcel-data/index.json').then(r => r.json()); parcelIndex.lookup = new Map(parcelIndex.tiles.map(tile => [tile.key, tile])); await updateParcels();
      offlineMap.on('moveend', updateParcels);
      offlineMap.on('click', 'parcels-fill', event => { const p = event.features[0].properties || {}; new maplibregl.Popup().setLngLat(event.lngLat).setHTML(`<b style="color:#0f766e;font-size:11px">OWNER</b><strong style="display:block;margin:4px 0">${text(p.owner_name || 'Owner not listed')}</strong><div>${text(p.property_address || 'Address not listed')}<br>${text(p.property_city || '')} ${text(p.property_zip || '')}</div>`).addTo(offlineMap); });
      if (navigator.geolocation) navigator.geolocation.getCurrentPosition(position => new maplibregl.Marker({ color: '#1a73e8' }).setLngLat([position.coords.longitude, position.coords.latitude]).addTo(offlineMap), () => {});
      notice('Offline map is ready.');
    });
  };
  panel.querySelector('.save-map').onclick = () => createPack().catch(error => { notice(error.message); panel.querySelector('.save-map').disabled = false; });
  panel.querySelector('.open-map').onclick = () => showOfflineMap().catch(error => { view.style.display = 'none'; notice(error.message); });
  panel.querySelector('.clear-map').onclick = () => { if (!confirm('Remove the saved street map from this phone?')) return; controller()?.postMessage({ type: 'clear-map-pack' }); localStorage.removeItem('mapapp-offline-pack'); notice('Saved street map cleared.'); };
  view.querySelector('.offline-map-close').onclick = () => { view.style.display = 'none'; };
  navigator.serviceWorker?.addEventListener('message', event => { const data = event.data || {}; if (data.type === 'map-saved') { panel.querySelector('.save-map').disabled = false; panel.querySelector('.save-map').textContent = 'Map area saved'; notice('Street map saved. You can now open it without service.'); } if (data.type === 'map-error') { panel.querySelector('.save-map').disabled = false; notice('Could not save the offline map. Check your connection and try again.'); } });
})();
