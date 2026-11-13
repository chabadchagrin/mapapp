// App files and parcel-data/index.json: network first, so updates arrive as soon as there's signal;
// the cached copy is used when offline. Parcel tiles: cache first — their URLs carry ?v=<data date>,
// so a monthly refresh produces new URLs and phones fetch the new data.
const SHELL_CACHE='map-app-shell-v6';
const PARCEL_CACHE='map-app-parcels-v6';
const CURRENT=[SHELL_CACHE,PARCEL_CACHE];
const APP_SHELL=['./','./index.html','./parcel-data/index.json','./offline-controls.js','./manifest.json','./icon-192.png','./icon-512.png'];

self.addEventListener('install',event=>event.waitUntil(caches.open(SHELL_CACHE).then(cache=>cache.addAll(APP_SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('map-app-')&&!CURRENT.includes(key)).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));

self.addEventListener('fetch',event=>{
  const request=event.request,url=new URL(request.url);
  if(request.method!=='GET'||url.origin!==self.location.origin)return;
  const tile=url.pathname.includes('/parcel-data/')&&url.pathname.endsWith('.geojson');
  if(tile){
    event.respondWith(caches.open(PARCEL_CACHE).then(cache=>cache.match(request,{ignoreSearch:!url.search}).then(cached=>cached||fetch(request).then(response=>{
      if(response.ok)cache.put(request,response.clone());
      return response;
    }))));
    return;
  }
  event.respondWith(caches.open(SHELL_CACHE).then(cache=>fetch(request).then(response=>{
    if(response.ok)cache.put(request,response.clone());
    return response;
  }).catch(()=>cache.match(request,{ignoreSearch:true}))));
});

self.addEventListener('message',event=>{
  const data=event.data||{},client=event.source;
  const send=message=>{if(client&&client.postMessage)client.postMessage(message)};

  if(data.type==='clear-parcels'){
    event.waitUntil(caches.delete(PARCEL_CACHE).then(()=>send({type:'cleared'})));
    return;
  }
  if(data.type!=='download-parcels'||!Array.isArray(data.urls))return;
  // Start from an empty cache so tiles from older data versions don't pile up.
  event.waitUntil(caches.delete(PARCEL_CACHE).then(()=>caches.open(PARCEL_CACHE)).then(async cache=>{
    let saved=0;
    for(const url of data.urls){
      try{
        const response=await fetch(url);
        if(response.ok){await cache.put(url,response);saved++}
      }catch(_){}
      send({type:'progress',saved,total:data.urls.length});
    }
    send({type:'complete',saved,total:data.urls.length});
  }));
});
