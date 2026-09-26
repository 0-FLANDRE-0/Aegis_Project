#!/usr/bin/env node
'use strict';
const fs=require('fs');
const assert=require('assert');
const path=require('path');
const vm=require('vm');

const htmlPath=path.resolve(process.argv[2]||'Aegis_SIM_v48_WIP13C17.html');
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
function el(id=''){return {id,style:{setProperty(){}},dataset:{},hidden:false,textContent:'',innerHTML:'',value:'',checked:false,width:1280,height:720,clientWidth:1280,clientHeight:720,parentElement:null,children:[],querySelector(){return null},querySelectorAll(){return []},classList:classList(),addEventListener(){},removeEventListener(){},setAttribute(k,v){this[k]=String(v);},getAttribute(k){return this[k]??null;},appendChild(c){this.children.push(c);c.parentElement=this;return c;},prepend(c){this.children.unshift(c);c.parentElement=this;return c;},remove(){},click(){},focus(){},blur(){},setPointerCapture(){},releasePointerCapture(){},getBoundingClientRect(){return {left:0,top:0,width:1280,height:720,right:1280,bottom:720};},getContext(){return ctx2d;}};}
const elements=new Map(),documentElement=el('html'),body=el('body');documentElement.appendChild(body);
const document={documentElement,body,fullscreenElement:null,webkitFullscreenElement:null,getElementById(id){if(!elements.has(id)){const e=el(id);body.appendChild(e);elements.set(id,e);}return elements.get(id);},querySelectorAll(){return [];},querySelector(){return null;},createElement(tag){return el(tag);},addEventListener(){},removeEventListener(){},exitFullscreen:async()=>{},webkitExitFullscreen:async()=>{}};
const storage=new Map(),localStorage={getItem:k=>storage.has(k)?storage.get(k):null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k),clear:()=>storage.clear()};
const sandbox={console,document,localStorage,navigator:{clipboard:{writeText:async()=>{}},userAgent:'node'},location:{search:'',href:'file://aegis',protocol:'file:'},innerWidth:1280,innerHeight:720,devicePixelRatio:1,addEventListener(){},removeEventListener(){},requestAnimationFrame(){return 1;},cancelAnimationFrame(){},setTimeout(){return 1;},clearTimeout(){},setInterval(){return 1;},clearInterval(){},performance:{now:()=>0},crypto:globalThis.crypto,structuredClone:globalThis.structuredClone,TextEncoder,TextDecoder,URL,URLSearchParams,Map,Set,WeakMap,WeakSet,Date,Math,JSON,Number,String,Boolean,Object,Array,RegExp,Error,TypeError,Promise,Uint8Array,Uint8ClampedArray,Float32Array,Float64Array,Int32Array,ArrayBuffer,alert(){},confirm(){return true;},Image:function(){return el('img');},MutationObserver:class{observe(){} disconnect(){}},ResizeObserver:class{observe(){} disconnect(){}},Blob:globalThis.Blob};
sandbox.window=sandbox;sandbox.self=sandbox;sandbox.globalThis=sandbox;
sandbox.__NAVAL_SIM_SEED__=1350501;
const context=vm.createContext(sandbox);
const zlib=require('zlib');
const tags=[...html.matchAll(/<script type="application\/octet-stream" data-c55-index="(\d+)">([^<]+)<\/script>/g)];
if(tags.length!==14)throw Error('EXPECTED_14_RECORDS_'+tags.length);
const scripts=tags.map(m=>zlib.gunzipSync(Buffer.from(m[2],'base64')).toString('utf8'));
elements.get('c5-offline-three')?.textContent;
document.getElementById('c5-offline-three').textContent=scripts[0];
for(let k=1;k<scripts.length;k++){
 try{new vm.Script(scripts[k],{filename:'decoded-'+k+'.js'}).runInContext(context,{timeout:120000});console.log('INIT',k,'OK');}
 catch(e){console.error('INIT',k,'FAIL',e.stack?.slice(0,1300));process.exit(1);}
}
const core=context.__CORE_SELFTEST_FAILURES__;
assert(Array.isArray(core)&&core.length===0,'CORE SELFTEST: '+JSON.stringify(core));
const snap=context.__NAVAL_SIM_DIAG__?.wip13c17Spg62ServoSnapshot?.();
assert(snap?.mounts?.length===3,'MISSING_SPG62_MOUNT_SNAPSHOT');
const q=context.__NAVAL_SIM_DIAG__.runWip13c5SurfaceSarhFixture();
assert(q.pass,'C5 SURFACE SARH FIXTURE: '+JSON.stringify({checks:q.checks,error:q.error}));
console.log(JSON.stringify({coreFailures:core.length,servoMounts:snap.mounts.length,c5Pass:q.pass,c5Checks:Object.keys(q.checks).length,c5EchoCount:q.rf.echoCount,seed:sandbox.__NAVAL_SIM_SEED__}));
if(process.env.AEGIS_RUN_FLIGHT==='1'){
 const q=context.__NAVAL_SIM_DIAG__.runWip13c5SurfaceSarhLiveFlightFixture({maxTimeS:20});
 console.log('C5_FLIGHT',JSON.stringify({pass:q.pass,checks:q.checks,error:q.error,deathReason:q.deathReason,timeS:q.timeS,maxSarhEchoes:q.maxSarhEchoes,maxSarhMeasurements:q.maxSarhMeasurements}).slice(0,2000));
}
