import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import alerts from '../alerts/worker.js';

test('alert settings preserve an explicit empty selected list, validate IDs and expose API v3',async()=>{
 let cfg={radius_km:45,alert_mode:'all',satellite_ids:'[]',lat:0,lon:0,enabled:0,verified:1};
 const env={ACCESS_KEY:'x'.repeat(32),SITE_ORIGIN:'https://example.test',DB:{prepare(sql){return {first:async()=>cfg,bind(...v){return {run:async()=>{assert.match(sql,/alert_mode=\?,satellite_ids=\?/);cfg={...cfg,lat:v[0],lon:v[1],enabled:v[2],radius_km:v[3],alert_mode:v[4],satellite_ids:v[5]};}};}};}}};
 const call=b=>alerts.fetch(new Request('https://alerts.test/settings',{method:'POST',headers:{Origin:env.SITE_ORIGIN,Authorization:`Bearer ${env.ACCESS_KEY}`,'Content-Type':'application/json'},body:JSON.stringify(b)}),env);
 let response=await call({lat:10,lon:20,radiusKm:100,enabled:false,alertMode:'selected',satelliteIds:[]});assert.equal(response.status,200);let j=await response.json();assert.equal(j.apiVersion,3);assert.equal(j.alertMode,'selected');assert.deepEqual(j.satelliteIds,[]);
 response=await call({lat:10,lon:20,radiusKm:100,enabled:false,alertMode:'selected',satelliteIds:['not-an-id']});assert.equal(response.status,400);
 response=await call({lat:10,lon:20,radiusKm:100,enabled:false,alertMode:'selected',satelliteIds:['25544','25544']});assert.equal(response.status,200);assert.deepEqual((await response.json()).satelliteIds,['25544']);
});

test('tracker loads with an empty catalog and no location without emitting broken frames',()=>{
 let posted;const context={postMessage:x=>posted=x,setInterval:()=>1,clearInterval(){},Date,Math};vm.createContext(context);vm.runInContext(readFileSync(new URL('../public/tracker-worker.js',import.meta.url),'utf8'),context);context.onmessage({data:{data:[]}});assert.equal(posted,undefined);
});
