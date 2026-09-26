#!/usr/bin/env node
'use strict';
const fs=require('fs'),vm=require('vm'),zlib=require('zlib'),assert=require('assert');
const html=fs.readFileSync(process.argv[2]||'Aegis_SIM_v48_WIP13C22.html','utf8');
const m=html.match(/<script type="application\/octet-stream" data-c55-index="13">([^<]+)<\/script>/);
assert(m,'packed main missing');
const src=zlib.gunzipSync(Buffer.from(m[1],'base64')).toString('utf8');
const start=src.indexOf('function surfaceMissileSweptContactWip13C5(');
const end=src.indexOf('function runWip13c5SurfaceSarhFixture(',start);
assert(start>0&&end>start);
function run({hullT,fromZ,toZ}){
 const captured=[];
 const context={
   surfaceMissileRuntimeWip13C6:()=>true,
   surfaceContacts:[],surfaceMissileFuzeEnvelopeWip13C22:()=>null,
   surfaceTargetFirstAsmContactWip13A:()=>hullT==null?null:{hit:{t:hullT}},
   resolveSurfaceMissileContactWip13C5:(missile,contact)=>{captured.push({contact,position:{x:missile.x,y:missile.y,z:missile.z}});return {kind:'HULL'};},
   clamp:(v,min,max)=>Math.max(min,Math.min(max,v)),
   lerp:(a,b,t)=>a+(b-a)*t,
   Number,Math
 };
 vm.createContext(context);
 vm.runInContext(src.slice(start,end)+'\nthis.check=surfaceMissileSweptContactWip13C5;',context);
 const missile={x:100,y:20,z:toZ,dead:false,_surfaceSarh:{}};
 const result=context.check(missile,{x:0,y:0,z:fromZ});
 return {missile,result,captured};
}
const earlierSea=run({hullT:.75,fromZ:1,toZ:-1});
assert.strictEqual(earlierSea.result,null);
assert.strictEqual(earlierSea.captured.length,0,'ship must not receive damage after earlier sea impact');
assert(Math.abs(earlierSea.missile.x-50)<1e-9&&earlierSea.missile.z<0,'sea impact should occur at first crossing');
const earlierHull=run({hullT:.25,fromZ:1,toZ:-1});
assert.strictEqual(earlierHull.result.kind,'HULL');
assert.strictEqual(earlierHull.captured.length,1);
assert(Math.abs(earlierHull.missile.x-25)<1e-9&&Math.abs(earlierHull.missile.z-.5)<1e-9);
const equal=run({hullT:.5,fromZ:1,toZ:-1});
assert.strictEqual(equal.result.kind,'HULL','contact/sea tie must resolve only once as hull contact');
const seaOnly=run({hullT:null,fromZ:1,toZ:-1});
assert.strictEqual(seaOnly.result,null);
assert(Math.abs(seaOnly.missile.x-50)<1e-9&&seaOnly.missile.z<0);
const noCross=run({hullT:null,fromZ:1,toZ:.5});
assert.strictEqual(noCross.result,null);
assert.strictEqual(noCross.missile.x,100);
console.log(JSON.stringify({pass:true,cases:5,earliestSea:true,earliestHull:true,tieOnlyOnce:true,seaWithoutHull:true,noCollision:true}));
