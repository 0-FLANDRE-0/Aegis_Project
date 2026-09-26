#!/usr/bin/env node
// Offline presentation checks. Does not claim a browser/WebGL or live combat run.
'use strict';
const fs=require('fs'),vm=require('vm'),zlib=require('zlib'),crypto=require('crypto'),assert=require('assert');
function unpack(file){const html=fs.readFileSync(file,'utf8'),meta=[...html.matchAll(/\{"id":"[^"]+","type":"[^"]+","rawBytes":\d+,"gzipBytes":\d+,"sha256":"[a-f0-9]{64}"\}/g)].map(x=>JSON.parse(x[0]));const raw=[...html.matchAll(/<script type="application\/octet-stream" data-c55-index="(\d+)">([^<]+)<\/script>/g)].map((m,i)=>{assert.equal(+m[1],i);const packed=Buffer.from(m[2],'base64'),b=zlib.gunzipSync(packed);assert.equal(b.length,meta[i].rawBytes);assert.equal(packed.length,meta[i].gzipBytes);assert.equal(crypto.createHash('sha256').update(b).digest('hex'),meta[i].sha256);new vm.Script(b.toString());return b.toString();});assert.equal(raw.length,14);return raw;}
const baseline='Aegis_SIM_v48_WIP13C18.html';
const before=fs.existsSync(baseline)?unpack(baseline):null,after=unpack(process.argv[2]||'Aegis_SIM_v48_WIP13C19.html');
if(before){
  assert.deepEqual(after.map((s,i)=>s===before[i]?null:i).filter(x=>x!==null),[11,12,13]);
  // Only presentation code differs in main: renderer palette and C15 display containment.
  const prefix=s=>s.slice(0,s.indexOf('function wip13c51InstallRenderer('));assert.equal(prefix(before[13]),prefix(after[13]));
}
const c={console,atob,btoa,TextDecoder,TextEncoder,setTimeout:()=>0,clearTimeout:()=>{}};c.window=c;c.self=c;vm.createContext(c);
for(const i of [0,2,4,5,6,7,8,9,10,11,12])vm.runInContext(after[i],c);
const T=c.THREE,asset=c.BurkeSimStyle.create(T,{noInterior:true,noAutoSupports:true});const counts=JSON.parse(JSON.stringify(asset.buildAudit.c19Exterior.faceCounts));assert.equal(counts.REMOVE,726);assert.equal(counts.safetyOrange,1330);assert.equal(counts.rescueRope,946);assert.equal(counts.doorPanel,112);assert.equal(counts.boatRubber,151);assert.equal(counts.boatHull,418);
let tris=0;const styles=new Map();asset.root.traverse(m=>{if(!m.isMesh)return;tris+=(m.geometry.index?.count||m.geometry.attributes.position.count)/3;assert(m.geometry.boundingBox);for(const x of m.geometry.attributes.position.array)assert(Number.isFinite(x));styles.set(m.material.userData.styleKey,m.material);});assert.equal(tris,224404);
const session=c.BurkePaintC56.attach(T,asset.root);for(const on of [true,false,true]){session.setEnabled(on);for(const r of session.records){assert(Number.isFinite(r.material.roughness));if(r.style==='safetyOrange')assert.equal(r.material.color.getHex(),0xe76d24);}}
const src=after[13],start=src.indexOf('const C15_ENVELOPE_DATA='),end=src.indexOf('function c15SelectShipLod(',start);assert(start>0&&end>start);vm.runInContext(src.slice(start,end)+'\nthis.contains=c15EnvelopeContainsLocal;this.sync=c15SyncOwnContainment;',c);
let oldContext=null;
if(before){oldContext={atob};vm.createContext(oldContext);const a0=before[13].indexOf('const C15_ENVELOPE_DATA='),a1=before[13].indexOf('function c15OwnInteriorLayers',a0);vm.runInContext(before[13].slice(a0,a1)+'\nthis.contains=c15EnvelopeContainsLocal;',oldContext);}
for(const p of [{x:27.2,y:15.7,z:6},{x:20,y:18.25,z:0},{x:35,y:12.85,z:0},{x:28.25,y:15.4,z:5.5}]){if(oldContext)assert(oldContext.contains(p),'regression must reproduce the old filled gap');assert(!c.contains(p),'air gap not clipped: '+JSON.stringify(p));}
for(const p of [{x:27.2,y:15.7,z:0},{x:28,y:12,z:0},{x:0,y:0,z:0},{x:20,y:18.25,z:4.2}])assert(c.contains(p),'valid interior incorrectly lost: '+JSON.stringify(p));
const world=new T.Group();world.add(asset.root);asset.root.userData.wip13c51=true;asset.root.position.set(1700,3,-920);asset.root.rotation.set(.025,1.7,-.03);
const inner=new T.Group();inner.add(new T.Mesh(new T.BoxGeometry(3,3,3),new T.MeshStandardMaterial()));asset.root.add(inner);
const view={THREE:T,shipRoot:asset.root,worldRoot:world,_c5Asset:asset,compartmentInteriorV8:inner,eventParticles:[],renderer:{getContext:()=>({getContextAttributes:()=>({stencil:false})}),getRenderTarget:()=>null}};c.sync(view);assert(view._c15Containment.active);assert.equal(view._c15Containment.map.image.height,1560);
const local=new T.Vector3(27.2,15.7,6),back=asset.root.localToWorld(local.clone()).applyMatrix4(view._c15Containment.uniforms.c15ToShip.value);assert(back.distanceTo(local)<1e-9);
const m=inner.children[0].material,shader={uniforms:{},vertexShader:T.ShaderLib.standard.vertexShader,fragmentShader:T.ShaderLib.standard.fragmentShader};m.onBeforeCompile(shader,view.renderer);assert(shader.fragmentShader.includes('slot<5'));assert(shader.fragmentShader.includes('if(c15Contain>.5&&!c15Inside(vC15Body))discard;'));assert(shader.vertexShader.includes('c15ToShip*modelMatrix*c15P'));assert.equal(shader.uniforms.c15ShellMap.value.image.data.length,6477120);
inner.visible=false;c.sync(view);assert(!view._c15Containment.active);inner.visible=true;c.sync(view);assert(view._c15Containment.active);view.c15ContainmentEnabled=false;c.sync(view);assert.equal(view._c15Containment.uniforms.c15Contain.value,0);
console.log(JSON.stringify({pass:true,recordsParsedAndHashed:14,unchangedRecords:before?11:'BASELINE_NOT_PRESENT',sourceAuthorityUnchanged:before?true:'BASELINE_NOT_PRESENT',trianglesBefore:before?225130:'BASELINE_NOT_PRESENT',trianglesAfter:tris,faceCounts:counts,airGapProbesRejected:4,validInteriorProbesRetained:4,shaderInjection:'PASS',shipTransform:'PASS',coatingToggle:'PASS',browserWebGL:'NOT_RUN'},null,2));
