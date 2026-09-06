import {records,position,groundDistance,bearing} from '../lib/orbit/core.js';
let sats=[],skipped=0,loc=null,timer;
function tick(){if(!loc||!sats.length)return;const now=Date.now(),near=[];let valid=0,inside=0;for(const s of sats){if(Math.abs(now-s.epoch)>7*86400000)continue;const p=position(s,now);if(!p)continue;valid++;const distance=groundDistance(loc,p);if(distance<=45)inside++;if(distance<2500)near.push({id:s.id,name:s.name,...p,distance,bearing:bearing(loc,p)});}near.sort((a,b)=>a.distance-b.distance);postMessage({now,valid,inside,skipped,near:near.slice(0,150)});}
onmessage=e=>{if(e.data.data){const r=records(e.data.data);sats=r.sats;skipped=r.skipped;}if(e.data.loc)loc=e.data.loc;clearInterval(timer);tick();timer=setInterval(tick,2000);};
