// Native function bodies in isolated VMs. Dependency controls are not sensor acquisition.
const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const sources=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
function make(src){
 const s={TAU:Math.PI*2,aircraft:{x:()=>3,y:()=>-2,_vx:.01,_vy:-.005},OWN_ALT_M:22,ALT_MIN_M:0,TRACK_ALT_MAX_M:50000,TRACK_FILTER_MODEL:{nisGateNormal:36,nisManeuverStart:6,nisManeuverFull:22},matrixCalls:0,
 worldToMeters:x=>x/.0038,metersToWorld:x=>x*.0038,worldSpeedToMps:x=>x/.0038,mpsToWorldSpeed:x=>x*.0038,clamp:(v,a,b)=>Math.max(a,Math.min(b,v)),lerp:(a,b,t)=>a+(b-a)*t,
 trackRefreshDerivedQuality:()=>{},trackSyncLegacyFromEkf:()=>{}};
 vm.createContext(s);let code='';for(const [n,rows]of Object.entries(src))code+='\n'+rows.at(-1);
 vm.runInContext('const trackRadarAssociationCachePerfC=new WeakMap();'+code+';const mulNative=_matMul;_matMul=(...a)=>{matrixCalls++;return mulNative(...a)};this.score=trackRadarAssociationNisV31;this.update=trackEkfUpdateRadar;'+(src.trackRadarAssociationKernelPerfC?'this.kernel=trackRadarAssociationKernelPerfC;this.inverse=trackRadarAssociationInversePerfC;this.self=performanceCSelfTest;':''),s);
 return s;
}
const a=make(sources.baseline),b=make(sources.candidate),checks={},rows=[];
const track=()=>({_kfX:new Float64Array([24000,4000,9000,-240,20,-1]),_kfP:new Float64Array(Array.from({length:36},(_,i)=>i%7===0?500:0)),_maneuverProbability:0});
const measurement=()=>({sensorXWorld:0,sensorYWorld:0,sensorZM:22,sensorVxMps:4,sensorVyMps:1,sensorVzMps:0,rangeM:25896,azRad:.165,elRad:.355,radialMps:-217,rangeSigmaM:45,azSigmaDeg:.08,elSigmaDeg:.1,radialVelSigmaMps:6});
const clone=tr=>{const c={...tr};for(const k of ['_kfX','_kfP'])if(tr[k])c[k]=new Float64Array(tr[k]);return c};
const state=tr=>JSON.stringify(tr,(k,v)=>v instanceof Float64Array?Array.from(v):v);
function score(label,ta,tb,m){const before=state(ta),old=a.score(ta,m),next=b.score(tb,m),exact=Object.is(old,next),sameState=state(ta)===state(tb);rows.push({label,exact,sameState,baseline:Number.isFinite(old)?old:String(old),candidate:Number.isFinite(next)?next:String(next)});return exact&&sameState;}
let ta=track(),tb=clone(ta),m=measurement();checks.initialAndRepeatExact=score('initial',ta,tb,m)&&score('repeat',ta,tb,m);
const initial=b.kernel(tb,m);checks.kernelActuallyReused=initial===b.kernel(tb,{...m,rangeM:m.rangeM+20,azRad:m.azRad+.001});
let all=true;
for(const [key,n]of [['_kfX',6],['_kfP',36]])for(let i=0;i<n;i++){ta[key][i]+=.125;tb[key][i]+=.125;const prior=b.kernel(tb,m);tb[key][i]+=.25;ta[key][i]+=.25;all=score(key+'-'+i,ta,tb,m)&&all;checks['invalidates-'+key+'-'+i]=prior!==b.kernel(tb,m);}
checks.allInPlaceFilterMutationsExact=all;
for(const key of ['sensorXWorld','sensorYWorld','sensorZM','sensorVxMps','sensorVyMps','sensorVzMps']){const prior=b.kernel(tb,m);m={...m,[key]:m[key]+.25};checks['origin-'+key]=score(key,ta,tb,m)&&prior!==b.kernel(tb,m);}
const kernel=b.kernel(tb,m);all=true;for(const key of ['rangeM','azRad','elRad','radialMps']){m={...m,[key]:m[key]+.1};all=score(key,ta,tb,m)&&all;}checks.measurementChangesReuseOnlyGeometry=all&&kernel===b.kernel(tb,m);
for(const key of ['rangeSigmaM','azSigmaDeg','elSigmaDeg','radialVelSigmaMps']){const prior=kernel.Sinv;m={...m,[key]:m[key]+.02};checks['noise-'+key]=score(key,ta,tb,m)&&prior!==kernel.Sinv;}
checks.distinctTrackObjectsDoNotShare=b.kernel(track(),m)!==b.kernel(track(),m);
ta=track();tb=clone(ta);m=measurement();const beforeZero=b.kernel(tb,m);m.sensorXWorld=-0;checks.signedZeroInputInvalidates=score('signed-zero',ta,tb,m)&&beforeZero!==b.kernel(tb,m);
const detached=b.kernel(tb,m);checks.detachedFilterInputCopies=detached.x!==tb._kfX&&detached.P!==tb._kfP;
// Values near clamp floors, missing origins, NaN and infinity retain native failure behavior.
let seed=1831565813;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
all=true;for(let i=0;i<128;i++){
 const t=track();for(let j=0;j<6;j++)t._kfX[j]+=(random()-.5)*1000;for(let j=0;j<36;j++)if(j%7===0)t._kfP[j]=1+random()*2000;
 const p=measurement();p.rangeM+=(random()-.5)*100;p.azRad+=(random()-.5)*.02;p.elRad+=(random()-.5)*.02;p.radialMps+=(random()-.5)*10;
 for(const k of ['rangeSigmaM','azSigmaDeg','elSigmaDeg','radialVelSigmaMps'])p[k]*=.5+random();
 if(i%4===0)for(const k of ['sensorXWorld','sensorYWorld','sensorZM','sensorVxMps','sensorVyMps','sensorVzMps'])delete p[k];
 if(i%8===1)Object.assign(p,{rangeSigmaM:0,azSigmaDeg:0,elSigmaDeg:0,radialVelSigmaMps:0});
 if(i%16===2)p.azRad+=Math.PI*2;if(i%16===3)p.elRad-=Math.PI*2;
 if(i%16===4)p.rangeM=NaN;if(i%16===5)p.azRad=Infinity;if(i%16===6)p.rangeSigmaM=NaN;
 all=score('varied-'+i,t,clone(t),p)&&all;
}checks.variedAndInvalidMeasurementsExact=all;
ta={x:4,y:2,z:7000,vx:-.8,vy:0,vz:1};tb=clone(ta);checks.uninitializedNativeFilterExact=score('initialization',ta,tb,measurement());
ta=track();tb=clone(ta);m=measurement();const before=state(tb);score('before-update',ta,tb,m);const ra=a.update(ta,m,{nisGate:1e9}),rb=b.update(tb,m,{nisGate:1e9});checks.correctionDoesNotConsumeCachedKernel=ra===rb&&ra===true&&state(ta)===state(tb)&&state(tb)!==before&&score('after-update',ta,tb,m);
const ra2=a.update(ta,{...m,rangeM:1e6},{nisGate:0}),rb2=b.update(tb,{...m,rangeM:1e6},{nisGate:0});checks.rejectedUpdateAndNextAssociationExact=ra2===rb2&&ra2===false&&state(ta)===state(tb)&&score('after-rejection',ta,tb,m);
ta=track();tb=clone(ta);m=measurement();a.matrixCalls=b.matrixCalls=0;all=true;for(let i=0;i<32;i++)all=score('reuse-'+i,ta,tb,{...m,rangeM:m.rangeM+i})&&all;
checks.repeatedBatchNisExact=all;checks.nativeMatrixWorkRetained=b.matrixCalls===a.matrixCalls;const matrixCalls={baseline:a.matrixCalls,candidate:b.matrixCalls};
all=true;for(const gate of [36,64,96,180])for(const side of [-1,1]){
 ta=track();tb=clone(ta);m=measurement();const k=b.kernel(tb,m);Object.assign(m,{rangeM:k.pr.h[0],azRad:k.pr.h[1],elRad:k.pr.h[2],radialMps:k.pr.h[3]});b.score(tb,m);
 m.rangeM+=Math.sqrt(gate/k.Sinv[0])*(1+side*1e-7);const exact=score('gate-'+gate+'-'+side,ta,tb,m),old=a.score(ta,m),next=b.score(tb,m);all=all&&exact&&(old<=gate)===(side<0)&&(next<=gate)===(side<0);
}checks.allNativeGateBoundariesExact=all;
const self=b.self();checks.isolatedCoreSelftest=self.pass;
assert(rows.length>200);process.stdout.write(JSON.stringify({checks,rows,matrixCalls,self,pass:Object.values(checks).every(Boolean)}));
