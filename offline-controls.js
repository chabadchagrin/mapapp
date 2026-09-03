(function(){
"use strict";
const panel=document.querySelector('#offline-panel');
if(!panel)return;
const statusEl=document.querySelector('#status');
const tell=text=>{if(statusEl)statusEl.textContent=text};

panel.innerHTML='<p id="offline-status">Checking offline data…</p>'
  +'<button type="button" class="download" id="offline-download">Save all parcel data</button>'
  +'<button type="button" class="clear" id="offline-clear">Clear parcel download</button>';
const statusLine=panel.querySelector('#offline-status');
const downloadBtn=panel.querySelector('#offline-download');
const clearBtn=panel.querySelector('#offline-clear');

const META_KEY='mapapp-offline-meta';
function readMeta(){try{return JSON.parse(localStorage.getItem(META_KEY)||'null')}catch(_){return null}}
function writeMeta(meta){try{localStorage.setItem(META_KEY,JSON.stringify(meta))}catch(_){}}
function clearMeta(){try{localStorage.removeItem(META_KEY)}catch(_){}}

function renderIdleStatus(){
  const meta=readMeta();
  if(meta&&meta.savedAt){
    const when=new Date(meta.savedAt).toLocaleDateString();
    statusLine.textContent=`Parcel data saved ${when} (about 45 MB). The map picture itself still needs signal to load.`;
  }else{
    statusLine.textContent='Owner names not saved yet. Saves about 45 MB so property lookups work with no signal. The map picture itself still needs signal to load.';
  }
}
renderIdleStatus();

function getController(){
  if(!('serviceWorker'in navigator))return Promise.resolve(null);
  if(navigator.serviceWorker.controller)return Promise.resolve(navigator.serviceWorker.controller);
  return navigator.serviceWorker.ready.catch(()=>{}).then(()=>{
    if(navigator.serviceWorker.controller)return navigator.serviceWorker.controller;
    return new Promise(resolve=>{
      let done=false;
      const onChange=()=>{if(done)return;done=true;navigator.serviceWorker.removeEventListener('controllerchange',onChange);resolve(navigator.serviceWorker.controller)};
      navigator.serviceWorker.addEventListener('controllerchange',onChange);
      setTimeout(()=>{if(done)return;done=true;navigator.serviceWorker.removeEventListener('controllerchange',onChange);resolve(navigator.serviceWorker.controller)},5000);
    });
  });
}

if('serviceWorker'in navigator)navigator.serviceWorker.addEventListener('message',event=>{
  const data=event.data||{};
  if(data.type==='progress'){
    downloadBtn.textContent=`Saving ${data.saved} of ${data.total}…`;
    tell('Saving parcel data for offline use…');
  }
  if(data.type==='complete'){
    downloadBtn.disabled=false;downloadBtn.textContent='Save all parcel data';
    if(navigator.storage&&navigator.storage.persist)navigator.storage.persist().catch(()=>{});
    writeMeta({savedAt:Date.now()});
    renderIdleStatus();
    tell(`${data.saved} of ${data.total} parcel areas are ready offline.`);
  }
  if(data.type==='cleared'){
    downloadBtn.disabled=false;clearBtn.disabled=false;
    clearMeta();renderIdleStatus();
    tell('Saved parcel data was cleared.');
  }
});

downloadBtn.onclick=async()=>{
  if(!confirm('Save the full parcel-owner dataset for offline use? This uses about 45 MB. (The map picture itself still needs signal.)'))return;
  downloadBtn.disabled=true;downloadBtn.textContent='Preparing…';tell('Preparing offline download…');
  const control=await getController();
  if(!control){downloadBtn.disabled=false;downloadBtn.textContent='Save all parcel data';tell('Offline saving is still starting up. Wait a moment and try again.');return}
  let index;
  try{index=await fetch('parcel-data/index.json').then(r=>r.json())}catch(_){downloadBtn.disabled=false;downloadBtn.textContent='Save all parcel data';tell('Could not start the offline download. Check your connection and try again.');return}
  const parcelUrls=index.tiles.map(t=>new URL(t.url.replace(/^\//,''),location.href).href);
  control.postMessage({type:'download-parcels',urls:parcelUrls});
};

clearBtn.onclick=async()=>{
  if(!confirm('Remove the saved parcel data from this device? The map itself will remain.'))return;
  const control=await getController();
  if(!control){tell('Offline saving is still starting up. Wait a moment and try again.');return}
  downloadBtn.disabled=true;clearBtn.disabled=true;
  control.postMessage({type:'clear-parcels'});
};
})();
