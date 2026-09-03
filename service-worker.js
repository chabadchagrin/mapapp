const SHELL_CACHE='map-app-shell-v4';
const PARCEL_CACHE='map-app-parcels-v4';
const CURRENT=[SHELL_CACHE,PARCEL_CACHE];
const APP_SHELL=['./','./index.html','./parcel-data/index.json','./offline-controls.js','./manifest.json','./icon-192.png','./icon-512.png'];

self.addEventListener('install',event=>event.waitUntil(caches.open(SHELL_CACHE).then(cache=>cache.addAll(APP_SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('map-app-')&&!CURRENT.includes(key)).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));

self.addEventListener('fetch',event=>{
  const request=event.request,url=new URL(request.url);
  if(request.method!=='GET'||url.origin!==self.location.origin)return;
  const parcel=url.pathname.includes('/parcel-data/');
  const cacheName=parcel?PARCEL_CACHE:SHELL_CACHE;
  event.respondWith(caches.open(cacheName).then(cache=>cache.match(request).then(cached=>cached||fetch(request).then(response=>{
    if(response.ok)cache.put(request,response.clone());
    return response;
  }))));
});

self.addEventListener('message',event=>{
  const data=event.data||{},client=event.source;
  const send=message=>{if(client&&client.postMessage)client.postMessage(message)};

  if(data.type==='clear-parcels'){
    event.waitUntil(caches.delete(PARCEL_CACHE).then(()=>send({type:'cleared'})));
    return;
  }
  if(data.type!=='download-parcels'||!Array.isArray(data.urls))return;
  event.waitUntil(caches.open(PARCEL_CACHE).then(async cache=>{
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
