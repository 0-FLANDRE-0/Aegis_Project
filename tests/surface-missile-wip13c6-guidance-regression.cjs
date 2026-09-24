#!/usr/bin/env node
'use strict';
const fs=require('fs');
const path=require('path');
const vm=require('vm');

const htmlPath=path.resolve(process.argv[2]||'Aegis_SIM_v48_WIP13C6.html');
const reportPath=process.env.AEGIS_REPORT_PATH?path.resolve(process.env.AEGIS_REPORT_PATH):null;
const html=fs.readFileSync(htmlPath,'utf8');
const scriptMatch=html.match(/<script>([\s\S]*?)<\/script>/i);
if(!scriptMatch)throw new Error('INLINE_SCRIPT_NOT_FOUND');

const ctx2d=new Proxy({}, {get(t,p){
  if(p==='measureText')return s=>({width:String(s).length*6});
  if(p==='createLinearGradient'||p==='createRadialGradient')return ()=>({addColorStop(){}});
  if(p==='getImageData')return ()=>({data:new Uint8ClampedArray(4)});
  if(p==='canvas')return {width:1280,height:720};
  if(!(p in t))t[p]=()=>{};return t[p];
},set(t,p,v){t[p]=v;return true;}});
function classList(){const s=new Set();return {add:(...x)=>x.forEach(v=>s.add(v)),remove:(...x)=>x.forEach(v=>s.delete(v)),toggle:(x,v)=>{if(v===undefined)v=!s.has(x);v?s.add(x):s.delete(x);return v;},contains:x=>s.has(x)};}
function el(id=''){return {id,style:{},dataset:{},hidden:false,textContent:'',innerHTML:'',value:'',checked:false,width:1280,height:720,clientWidth:1280,clientHeight:720,parentElement:null,children:[],classList:classList(),addEventListener(){},removeEventListener(){},setAttribute(k,v){this[k]=String(v);},getAttribute(k){return this[k]??null;},appendChild(c){this.children.push(c);c.parentElement=this;return c;},prepend(c){this.children.unshift(c);c.parentElement=this;return c;},remove(){},click(){},focus(){},blur(){},setPointerCapture(){},releasePointerCapture(){},getBoundingClientRect(){return {left:0,top:0,width:1280,height:720,right:1280,bottom:720};},getContext(){return ctx2d;}};}
const elements=new Map(),documentElement=el('html'),body=el('body');documentElement.appendChild(body);
const document={documentElement,body,fullscreenElement:null,webkitFullscreenElement:null,getElementById(id){if(!elements.has(id)){const e=el(id);body.appendChild(e);elements.set(id,e);}return elements.get(id);},querySelectorAll(){return [];},querySelector(){return null;},createElement(tag){return el(tag);},addEventListener(){},removeEventListener(){},exitFullscreen:async()=>{},webkitExitFullscreen:async()=>{}};
const storage=new Map(),localStorage={getItem:k=>storage.has(k)?storage.get(k):null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k),clear:()=>storage.clear()};
const sandbox={console,document,localStorage,navigator:{clipboard:{writeText:async()=>{}},userAgent:'node'},location:{search:'',href:'file://aegis',protocol:'file:'},innerWidth:1280,innerHeight:720,devicePixelRatio:1,addEventListener(){},removeEventListener(){},requestAnimationFrame(){return 1;},cancelAnimationFrame(){},setTimeout(){return 1;},clearTimeout(){},setInterval(){return 1;},clearInterval(){},performance:{now:()=>0},crypto:globalThis.crypto,structuredClone:globalThis.structuredClone,TextEncoder,TextDecoder,URL,URLSearchParams,Map,Set,WeakMap,WeakSet,Date,Math,JSON,Number,String,Boolean,Object,Array,RegExp,Error,TypeError,Promise,Uint8Array,Uint8ClampedArray,Float32Array,Float64Array,Int32Array,ArrayBuffer,alert(){},confirm(){return true;},Image:function(){return el('img');},Blob:globalThis.Blob};
sandbox.window=sandbox;sandbox.self=sandbox;sandbox.globalThis=sandbox;
const context=vm.createContext(sandbox);
new vm.Script(scriptMatch[1],{filename:htmlPath}).runInContext(context,{timeout:30000});

const diag=context.window.__NAVAL_SIM_DIAG__||{};
const core=context.window.__CORE_SELFTEST_FAILURES__??['MISSING_CORE_SELFTEST'];
const c6=context.window.__WIP13C6_LAST_FIXTURE__??null;
const c4Foundation=diag.runWip13c4SurfaceMissileFoundationFixture();
const c4Terminal=diag.runWip13c4SurfaceTerminalAdapterFixture();
const b12=diag.runWip13b12ArhSeaClutterValidationFixture();
const tab=diag.wip13cRunTabInvarianceFixture();
const subtab=diag.wip13c3RunArmSubtabInvarianceFixture();

const forbiddenDecisionTokens=['truthObjectForTrackV27(','surfaceContacts','SURFACE_TARGET_ENTITY_REGISTRY_V48_WIP13A','truthRef','_truthObject','_physicsKind'];
function sourceSlice(start,end){const a=html.indexOf(start),b=end?html.indexOf(end,a+start.length):-1;return a<0?'':html.slice(a,b>0?b:Math.min(html.length,a+24000));}
const decisionSource=[
  sourceSlice('function surfaceEssmLiveReleaseGateWip13C6','function surfaceLaunchVectorAlignedWip13C6'),
  sourceSlice('function surfaceMissileCueTrackWip13C6','function surfaceMissileGuidanceFloorWip13C6'),
  sourceSlice('function surfaceMissileFilterGuidanceStateWip13C6','function resolveSurfaceMissileContactWip13C6'),
  sourceSlice('function spawnESSM(opts={})','// ===== Target behavior =====')
].join('\n');
const truthLeaks=forbiddenDecisionTokens.filter(t=>decisionSource.includes(t));
const checks={
  titleRevision:/AEGIS v48 WIP13C6 — Surface Guidance Stabilization \+ ESSM ARH/.test(html)&&/revision:'V48_WIP13C6'/.test(html),
  coreSelftest:Array.isArray(core)&&core.length===0,
  c6GuidanceFixture:!!c6?.pass,
  c6EssmLiveSpawn:!!c6?.checks?.essmLiveSpawn&&!!c6?.checks?.essmRoundConsumed,
  c6ArbitraryBearing:!!c6?.checks?.arbitraryBearingLaunchCommand,
  c6EssmSurfaceMidcourseFloor:!!c6?.checks?.essmSurfaceMidcourseFloor&&html.includes("!m._v1TerminalActive && !m._surfaceArh"),
  c6SurfaceSm2VectorGate:!!c6?.checks?.sm2SurfaceRejectsBadVelocity&&!!c6?.checks?.sm2SurfaceAcceptsAlignedVelocity,
  c6EstimatorDamping:!!c6?.checks?.surfaceEstimatorFilterDampsJitter,
  c6Sm2SeaGuard:!!c6?.checks?.sm2PredictiveSeaGuard,
  c6EssmPhysicalTerminal:!!c6?.checks?.essmPhysicalHullContact&&!!c6?.checks?.essmWip12fDamage,
  c6TruthRuntime:!!c6?.checks?.essmRuntimeTruthClean&&!!c6?.checks?.truthBoundary,
  c4Foundation:!!c4Foundation?.pass,
  c4Terminal:!!c4Terminal?.pass,
  b12ArhSeaClutter:!!b12?.pass,
  tabInvariant:!!tab?.pass,
  mobileArmSubtabInvariant:!!subtab?.pass,
  noDecisionTruthLeak:truthLeaks.length===0,
  surfaceProximityTruthShortcutDisabled:html.includes('const assignId = surfaceMissileRuntimeWip13C6(m)?null:m.assignedTargetId;'),
  surfaceSeaGuardAppliedToSm2:html.includes("if(m.guidanceCore==='v1' && (m.isESSM||m._surfaceSarh))"),
  legacyAirSm2VectorBehaviorPreserved:!!c6?.checks?.airSm2LegacyGatePreserved
};
const failed=Object.entries(checks).filter(([,v])=>!v).map(([k])=>k);
const report={schema:'AEGIS_WIP13C6_GUIDANCE_REGRESSION_REPORT',html:path.basename(htmlPath),checks,pass:failed.length===0,failed,coreSelftestFailures:core,truthLeaks,c6,c4Foundation:{pass:c4Foundation.pass,checks:c4Foundation.checks},c4Terminal:{pass:c4Terminal.pass,checks:c4Terminal.checks},b12:{pass:b12.pass,checks:b12.checks},tab:{pass:tab.pass,checks:tab.checks},subtab:{pass:subtab.pass,checks:subtab.checks}};
if(reportPath){fs.mkdirSync(path.dirname(reportPath),{recursive:true});fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify(report,null,2));
if(!report.pass)process.exit(1);
