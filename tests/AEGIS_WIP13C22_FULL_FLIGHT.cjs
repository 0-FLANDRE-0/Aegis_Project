#!/usr/bin/env node
'use strict';
const fs=require('fs');
const assert=require('assert');
const path=require('path');
const vm=require('vm');

const htmlPath=path.resolve(process.argv[2]||'Aegis_SIM_v48_WIP13C18.html');
const reportPath=process.env.AEGIS_REPORT_PATH?path.resolve(process.env.AEGIS_REPORT_PATH):null;
const html=fs.readFileSync(htmlPath,'utf8');
const ctx2d=new Proxy({}, {get(t,p){
  if(p==='measureText')return s=>({width:String(s).length*6});
  if(p==='createLinearGradient'||p==='createRadialGradient')return ()=>({addColorStop(){}});
  if(p==='getImageData')return ()=>({data:new Uint8ClampedArray(4)});
  if(p==='canvas')return {width:1280,height:720};
  if(!(p in t))t[p]=()=>{};return t[p];
},set(t,p,v){t[p]=v;return true;}});
function classList(){const s=new Set();return {add:(...x)=>x.forEach(v=>s.add(v)),remove:(...x)=>x.forEach(v=>s.delete(v)),toggle:(x,v)=>{if(v===undefined)v=!s.has(x);v?s.add(x):s.delete(x);return v;},contains:x=>s.has(x)};}
const elements=new Map(),dynamicPanels=new Set(['damageControlPanelV1','damageFloodPanelV1','shipSurvivalBannerV1']);
function el(id=''){return {id,style:{setProperty(){},set cssText(v){this._text=v;const match=String(v).match(/(?:^|;)\s*display\s*:\s*([^;]+)/);if(match)this.display=match[1].trim();},get cssText(){return this._text;}},dataset:{},hidden:false,textContent:'',innerHTML:'',value:'',checked:false,width:1280,height:720,clientWidth:1280,clientHeight:720,parentElement:null,children:[],firstChild:{},get lastChild(){return this.children.at(-1)??null;},querySelector(s){return String(s).startsWith('#')?(document.getElementById(String(s).slice(1))??el(s)):el(s)},querySelectorAll(){return []},classList:classList(),addEventListener(){},removeEventListener(){},setAttribute(k,v){this[k]=String(v);},getAttribute(k){return this[k]??null;},appendChild(c){this.children.push(c);c.parentElement=this;if(c.id&&dynamicPanels.has(c.id))elements.set(c.id,c);return c;},prepend(c){this.children.unshift(c);c.parentElement=this;return c;},remove(){if(this.parentElement){const siblings=this.parentElement.children;const index=siblings.indexOf(this);if(index>=0)siblings.splice(index,1);this.parentElement=null;}},click(){},focus(){},blur(){},setPointerCapture(){},releasePointerCapture(){},getBoundingClientRect(){return {left:0,top:0,width:1280,height:720,right:1280,bottom:720};},getContext(){return ctx2d;}};}
const documentElement=el('html'),body=el('body');documentElement.appendChild(body);
const document={documentElement,body,fullscreenElement:null,webkitFullscreenElement:null,getElementById(id){if(!elements.has(id)){if(dynamicPanels.has(id))return null;const e=el(id);body.appendChild(e);elements.set(id,e);}return elements.get(id);},querySelectorAll(){return [];},querySelector(){return null;},createElement(tag){return el(tag);},addEventListener(){},removeEventListener(){},exitFullscreen:async()=>{},webkitExitFullscreen:async()=>{}};
const storage=new Map(),localStorage={getItem:k=>storage.has(k)?storage.get(k):null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k),clear:()=>storage.clear()};
const sandbox={console,document,localStorage,navigator:{clipboard:{writeText:async()=>{}},userAgent:'node'},location:{search:'',href:'file://aegis',protocol:'file:'},innerWidth:1280,innerHeight:720,devicePixelRatio:1,addEventListener(){},removeEventListener(){},requestAnimationFrame(){return 1;},cancelAnimationFrame(){},setTimeout(){return 1;},clearTimeout(){},setInterval(){return 1;},clearInterval(){},performance:{now:()=>0},crypto:globalThis.crypto,structuredClone:globalThis.structuredClone,TextEncoder,TextDecoder,URL,URLSearchParams,Map,Set,WeakMap,WeakSet,Date,Math,JSON,Number,String,Boolean,Object,Array,RegExp,Error,TypeError,Promise,Uint8Array,Uint8ClampedArray,Float32Array,Float64Array,Int32Array,ArrayBuffer,alert(){},confirm(){return true;},Image:function(){return el('img');},MutationObserver:class{observe(){} disconnect(){}},ResizeObserver:class{observe(){} disconnect(){}},Blob:globalThis.Blob};
sandbox.window=sandbox;sandbox.self=sandbox;sandbox.globalThis=sandbox;
sandbox.__NAVAL_SIM_SEED__=1350501;
const context=vm.createContext(sandbox);
const zlib=require('zlib');
const tags=[...html.matchAll(/<script type="application\/octet-stream" data-c55-index="(\d+)">([^<]+)<\/script>/g)];
if(tags.length!==14)throw Error('EXPECTED_14_RECORDS_'+tags.length);
const scripts=tags.map(m=>zlib.gunzipSync(Buffer.from(m[2],'base64')).toString('utf8'));
if(process.env.AEGIS_PHASE_TRACE==='1'){
 const probes=[
   ['const s=_v1UpdateSarhMeasurementCore(m,cueTrack,dt);','SARH_MEASUREMENT_BEGIN'],
   ['const p=SAM_SARH_RF_PROFILE,s=_sarhEnsureTrackState(m);','SARH_CORE_BEGIN'],
   ['packet=_sarhBuildMeasurementSet(m,cueTrack);','SARH_BUILD_BEGIN'],
   ['const tx={x:worldToMeters(txW.x),y:worldToMeters(txW.y),z:txW.z,vx:txW.vx,vy:txW.vy,vz:0},rx=_sarhReceiverState(m),echoes=buildNavalSarhEchoPool(m,cueTrack),clusters=_sarhClusterEchoes(echoes),measurements=[];','SARH_ECHO_AND_CLUSTER'],
 ];
 for(const [needle,label] of probes){
   assert(scripts[13].includes(needle),'MISSING_PROBE_'+label);
   scripts[13]=scripts[13].replace(needle,`if(simStepCounter>=1450&&simStepCounter<=1460)console.log('${label}',simStepCounter,m.id);`+needle);
 }
 const clusterNeedle='const seen=new Array(echoes.length).fill(false),clusters=[];';
 assert(scripts[13].includes(clusterNeedle));
 scripts[13]=scripts[13].replace(clusterNeedle,`if(simStepCounter>=1450&&simStepCounter<=1460)console.log('SARH_CLUSTER_SIZE',simStepCounter,echoes.length);`+clusterNeedle);
 const endCluster='clusters=_sarhClusterEchoes(echoes),measurements=[];';
 assert(scripts[13].includes(endCluster));
 scripts[13]=scripts[13].replace(endCluster,endCluster+`if(simStepCounter>=1450&&simStepCounter<=1460)console.log('SARH_CLUSTERS_READY',simStepCounter,clusters.length,m._sarhRxRngState);`);
 const mono='for(const c of clusters){const mm=_sarhMonopulseMeasurement(m,c);if(mm)measurements.push(mm);}';
 assert(scripts[13].includes(mono));
 scripts[13]=scripts[13].replace(mono,'for(const c of clusters){if(simStepCounter===1453)console.log("MONO_START",clusters.indexOf(c),c.length,m._sarhRxRngState);const mm=_sarhMonopulseMeasurement(m,c);if(simStepCounter===1453)console.log("MONO_END",clusters.indexOf(c),m._sarhRxRngState);if(mm)measurements.push(mm);}');
 const association='selected=_sarhAssociateMeasurements(m,s,packet.measurements,packet.tx,packet.rx,cueTrack);';
 assert(scripts[13].includes(association));
 scripts[13]=scripts[13].replace(association,`if(simStepCounter===1453)console.log('ASSOC_START',packet.measurements.length,!!s._kfX);`+association+`if(simStepCounter===1453)console.log('ASSOC_END',!!selected);`);
 const assocLoop='for(const mm of measurements){const st=_sarhInnovationStats(s,mm,tx,rx);';
 assert(scripts[13].includes(assocLoop));
 scripts[13]=scripts[13].replace(assocLoop,'for(const mm of measurements){if(simStepCounter===1453)console.log("ASSOC_MEAS",measurements.indexOf(mm));const st=_sarhInnovationStats(s,mm,tx,rx);');
 const update='if(selected)accepted=_sarhEkfUpdate(s,selected,m,packet.tx,packet.rx,cueTrack);';
 assert(scripts[13].includes(update));
 scripts[13]=scripts[13].replace(update,`if(simStepCounter===1453)console.log('EKF_START',!!selected);`+update+`if(simStepCounter===1453)console.log('EKF_END',accepted);`);
 const sm='_sarhUpdateStateMachine(s,accepted,period,hasIll);_sarhStoreDiagnostics(m,s,packet,selected);';
 assert(scripts[13].includes(sm));
 scripts[13]=scripts[13].replace(sm,`if(simStepCounter===1453)console.log('SARH_STORE_START');`+sm+`if(simStepCounter===1453)console.log('SARH_STORE_END');`);
 for(const [needle,label] of [
   ['    // ===== Speed update (forces): thrust + drag + gravity =====','MISSILE_SPEED_STAGE'],
   ['// DL/IOG/SARH 상태 갱신','MISSILE_TRACK_STAGE'],
   ['    // ===== PHASE 1: CELL CLEAR → ADAPTIVE 3-D LAUNCH TRANSITION =====','MISSILE_GUIDANCE_STAGE'],
   ['    // ===== PHASE 1b: FORWARD-COMMIT — BODY ALIGNED, VELOCITY VECTOR CATCHES UP =====','MISSILE_FORWARD_COMMIT'],
   ['    // ===== PHASE 2: MIDCOURSE (fly toward intercept point) =====','MISSILE_MIDCOURSE'],
   ['    // ===== ZEM-based CPA correction (XY + Z, wider activation) =====','MISSILE_ZEM'],
   ['    // ===== Desired direction =====','MISSILE_DIRECTION'],
   ['    // ===== WIP40 physical TVC/body-thrust normal acceleration =====','MISSILE_TVC'],
   ['  // ===== Speed-fuse: Mach 0.5 이하로 떨어지면 자폭 (부스트 후에만) =====','MISSILE_SPEED_FUSE'],
   ['    // ===== PROXIMITY FUZE (Radar_v6_12 style) =====','MISSILE_PROXIMITY']
 ]){
   assert(scripts[13].includes(needle),'MISSING_MISSILE_STAGE_'+label);
   scripts[13]=scripts[13].replace(needle,`if(simStepCounter===1453)console.log('${label}');\n`+needle);
 }
 const phases=['damage_flood','scenario_ai','navigation_input','sensors_tracks_ew','world_entities','ordnance_guidance','close_in_terrain','cleanup','engagement_control'];
 for(const phase of phases){
   const needle=`SIM_SUBSYSTEM_PROFILER_V48_WIP11A.phase(_wip11aProfileTick,'${phase}');`;
   assert(scripts[13].includes(needle),'MISSING_PHASE_'+phase);
   scripts[13]=scripts[13].replace(needle,needle+`if(simStepCounter>=1450&&simStepCounter<=1460)console.log('PHASE',simStepCounter,'${phase}');`);
 }
 const missileNeedle='        updateMissile(m, dt);';
 assert(scripts[13].includes(missileNeedle));
 scripts[13]=scripts[13].replace(missileNeedle,"        if(simStepCounter>=1450&&simStepCounter<=1460)console.log('MISSILE_UPDATE_START',simStepCounter,m.id);\n"+missileNeedle+"\n        if(simStepCounter>=1450&&simStepCounter<=1460)console.log('MISSILE_UPDATE_END',simStepCounter,m.id);");
 const enemyNeedle='      if(em.alive) updateEnemyMissile(em, dt);';
 assert(scripts[13].includes(enemyNeedle));
 scripts[13]=scripts[13].replace(enemyNeedle,"      if(simStepCounter>=1450&&simStepCounter<=1460)console.log('ENEMY_UPDATE_START',simStepCounter,em.id);\n"+enemyNeedle+"\n      if(simStepCounter>=1450&&simStepCounter<=1460)console.log('ENEMY_UPDATE_END',simStepCounter,em.id);");
}
const hook=fs.readFileSync(path.join(__dirname,'AEGIS_WIP13C22_DIAGNOSTIC_HOOK.js'),'utf8');
const closing=scripts[13].lastIndexOf('})();');
assert(closing>0,'MAIN_CLOSURE_NOT_FOUND');
scripts[13]=scripts[13].slice(0,closing)+'\n'+hook+'\n'+scripts[13].slice(closing);
elements.get('c5-offline-three')?.textContent;
document.getElementById('c5-offline-three').textContent=scripts[0];
for(let k=1;k<scripts.length;k++){
 try{new vm.Script(scripts[k],{filename:'decoded-'+k+'.js'}).runInContext(context,{timeout:120000});console.log('INIT',k,'OK');}
 catch(e){console.error('INIT',k,'FAIL',e.stack?.slice(0,1300));process.exit(1);}
}
const core=context.__CORE_SELFTEST_FAILURES__;
assert(Array.isArray(core)&&core.length===0,'CORE SELFTEST: '+JSON.stringify(core));
if(process.env.AEGIS_CARD_ONLY==='1'){
 const lines=context.__C18_TEST__.surfaceCard();
 assert(lines.some(line=>line.includes('SM-2 FCS')),'SM-2 FCS omitted');
 assert(lines.some(line=>line.includes('ESSM FCS')),'ESSM FCS omitted');
 assert(lines.some(line=>line.includes('ARH 인계')),'ARH handoff omitted');
 assert(lines.some(line=>line.includes('SPG')),'SPG reservation omitted');
 const guarded=context.__C18_TEST__.surfaceCard({identity:'NEUTRAL'});
 assert(guarded.some(line=>line.includes('보호 표적')),'protected-identity inhibit omitted');
 assert(context.__C18_TEST__.surfaceCardPure(),'rendering mutated simulation/FCS state');
 console.log(JSON.stringify({pass:true,reasons:context.__C18_TEST__.surfaceReasons(),lines,guarded}));
 process.exit(0);
}
const cases=process.argv[3]?[JSON.parse(process.argv[3])]:[
 ...['SM2','ESSM'].flatMap(weapon=>[0,45,90,135,180,225,270,315].map(bearingDeg=>({weapon,bearingDeg,ownSpeedKt:25}))),
 {weapon:'ESSM',bearingDeg:90,ownSpeedKt:25,spgDisabled:true}
];
const rows=[];
for(const options of cases){
 const started=Date.now();
 const flight=context.__W14_TEST__.fullFlight(options);
 const row={options,deathReason:flight.deathReason??null,error:flight.error??null,lifeS:flight.lifeS??null,coreFailures:core.length,fault:flight.fault??null,lastError:flight.lastError??null,seconds:(Date.now()-started)/1000,assessmentReason:flight.assessment?.reason??null,damageImpacts:flight.damage?.impacts?.length??0,damageHits:flight.damage?.impacts?.filter(q=>q.hit)?.length??0,scarCount:flight.damage?.scars?.length??0,breachCount:flight.damage?.breaches?.length??0,explosiveMassKg:flight.damage?.impacts?.[0]?.explosiveMassKg??0,impact:flight.impact??null,terminal:flight.terminalEvent?{fuzePath:flight.terminalEvent.fuzePath,integrationMode:flight.terminalEvent.integrationMode,damageSummary:flight.terminalEvent.damageSummary}:null};
 rows.push(row);
 console.log('FLIGHT',JSON.stringify(row));
 if(reportPath)fs.writeFileSync(reportPath,JSON.stringify({htmlPath,rows},null,2)+'\n');
}
if(rows.some(q=>q.fault||q.error||q.coreFailures||(q.deathReason==='SEA_IMPACT'?q.damageHits!==0||q.explosiveMassKg!==0:(q.deathReason==='SURFACE_TARGET_CONTACT'?q.damageHits!==1||q.explosiveMassKg<=0||q.terminal?.fuzePath!=='CONTACT_DIRECT_ACTION':q.deathReason==='SURFACE_TARGET_PROXIMITY'?q.damageHits!==1||q.explosiveMassKg<=0||q.terminal?.fuzePath!=='PROXIMITY':true))))process.exitCode=1;
