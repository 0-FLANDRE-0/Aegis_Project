"""Embed an audited, detached native source capsule and explicit diagnostic API."""
import json,hashlib,re
from pathlib import Path
H=Path(__file__).resolve().parent
r=json.loads((H/'dependencies.json').read_text());names=[x['name'] for x in r['rows'] if x['type']=='DETACHED_NATIVE_VALUE'];native=(H/'native-engine.js').read_text();s=native+'\n'+(H/'private.js').read_text();settings=sorted(set(re.findall(r'window\.(WIP\w+)',native))|{'AEGIS_GAME_TERMINATION_ENABLED'})
hashes={x['name']:x['hash'] for x in r['rows'] if x.get('hash')}
runtime_hashes={x['name']:x['runtimeHash']for x in r['rows']if x.get('runtimeHash')}
fingerprint=['SAM_MISSILE_PROFILES','SAM_LOFT_PROFILE_REGISTRY','SAM_LOFT_B4_PROFILES','SAM_6DOF_LITE_REGISTRY','SAM_NAV_B1_PROFILES','WIP14A7_AERO_CURVES','WIP14A5_SM2ER_STAGE_CONTRACT','WIP14A6_SM6_STAGE_CONTRACT','WIP127_MK104_CORRECTED','WIP14A4_MK72_WORKING','WIP136_ESSM_CONTRACT','WIP136_ESSM_GRAIN_GEOMETRY']
table=json.loads((H/'UNMEASURED_ENVELOPE.json').read_text()) if(H/'UNMEASURED_ENVELOPE.json').exists() else {'provenance':'GAME_ENGINE_COMPUTED','profileHash':None,'rows':[]}
code='''// ENV_KAPPA_A: regenerated Kappa PIP-LOS native diagnostic capsule. No simulation runs on startup.
window.__ENV_A__=(()=>{
 const source=SOURCE_LITERAL,table=TABLE_LITERAL;let factory=null;
 function data(){return JSON.parse(JSON.stringify({DATA_NAMES}));}
 function settings(){return Object.fromEntries(SETTINGS_NAMES.map(k=>[k,window[k]]).filter(([,v])=>['number','boolean','string'].includes(typeof v)));}
 function fingerprint(d,s){return {diagnosticBoundaryHash:BOUNDARY_HASH,conditions:{idealRfObservationBoundary:'PER_TICK_RF_EKF_ESTIMATE_V2',navigationSeed:2047861954,fuzeSeaStateFactor:1.0649859543133355,rngSeed:1831565813,target:'NATIVE_AIRCRAFT_POINT_TARGET'},nativeSourceHashes:HASHES_LITERAL,models:Object.fromEntries(FINGERPRINT_NAMES.map(k=>[k,d[k]])),settings:s};}
 function capture(){const d=data(),s=settings();return {data:d,settings:s,profileFingerprintInput:fingerprint(d,s)};}
 function create(){factory??=new Function('DATA','SETTINGS','PROFILE','PRIVATE_SHIP',source);const q=capture();return factory(q.data,q.settings,{}, {entityId:'ENV_PRIVATE',navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}});}
 async function hash(value){const bytes=new TextEncoder().encode(JSON.stringify(value)),d=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(d)].map(n=>n.toString(16).padStart(2,'0')).join('');}
 async function nativeAudit(){const expected=RUNTIME_HASHES,actual=Object.fromEntries(await Promise.all(Object.entries({NATIVE_NAMES}).map(async([name,fn])=>{const bytes=new TextEncoder().encode(fn.toString()),d=await crypto.subtle.digest('SHA-256',bytes);return [name,[...new Uint8Array(d)].map(n=>n.toString(16).padStart(2,'0')).join('')];})));return Object.keys(expected).filter(k=>expected[k]!==actual[k]);}
 async function status(){const current=await hash(capture().profileFingerprintInput),changedNativeFunctions=await nativeAudit();return {guidanceRevision:'KAPPA_PIP_LOS_A',envelopeMeasured:false,historicalResults:table.historicalResults,measurementNotice:table.notice,nativeCapsuleSynchronized:changedNativeFunctions.length===0,provenance:'GAME_ENGINE_COMPUTED',currentProfileHash:current,tableProfileHash:table.profileHash,changedNativeFunctions,recalculationRequired:current!==table.profileHash||changedNativeFunctions.length>0,message:current===table.profileHash&&!changedNativeFunctions.length?'게임 엔진 계산표 일치':'재계산 필요'};}
 async function run(options={}){const mismatch=await nativeAudit();if(mismatch.length)throw Error('재계산 필요 — native capsule 재생성: '+mismatch.join(','));const inputs=capture(),profileHash=await hash(inputs.profileFingerprintInput),workers=[];
  const workerSource='const source='+JSON.stringify(source)+';'+SUITE_LITERAL+`;onmessage=async e=>{try{const {inputs,weapon}=e.data,factory=new Function('DATA','SETTINGS','PROFILE','PRIVATE_SHIP',source),create=()=>factory(structuredClone(inputs.data),structuredClone(inputs.settings),{},{entityId:'ENV_PRIVATE',navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}});const result=await envSuiteA(create,{onlyWeapon:weapon,onProgress:progress=>postMessage({progress})});postMessage({result});}catch(error){postMessage({error:String(error.stack??error)})}};`;
  const url=URL.createObjectURL(new Blob([workerSource],{type:'text/javascript'}));try{const parts=await Promise.all(['SM2','SM2ER','SM6','ESSM'].map(weapon=>new Promise((resolve,reject)=>{const worker=new Worker(url);workers.push(worker);worker.onerror=e=>reject(Error(e.message));worker.onmessage=e=>{if(e.data.progress){options.onProgress?.(e.data.progress);return;}if(e.data.error)reject(Error(e.data.error));else resolve(e.data.result);};worker.postMessage({inputs,weapon});})));return {...parts[0],table:parts.flatMap(q=>q.table),trajectories:parts.flatMap(q=>q.trajectories),calls:parts.reduce((s,q)=>s+q.calls,0),profileHash};}finally{for(const worker of workers)worker.terminate();URL.revokeObjectURL(url);}
 }

 return Object.freeze({create,case:options=>create().runCase(options),run,status,table:()=>JSON.parse(JSON.stringify(table)),capture});
})();
'''
replacements={'BOUNDARY_HASH':json.dumps(hashlib.sha256(((H/'boundaries.json').read_text()+(H/'private.js').read_text()).encode()).hexdigest()),'SOURCE_LITERAL':json.dumps(s,ensure_ascii=False),'TABLE_LITERAL':json.dumps(table,ensure_ascii=False,separators=(',',':')),'DATA_NAMES':','.join(names),'SETTINGS_NAMES':json.dumps(settings),'HASHES_LITERAL':json.dumps(hashes,sort_keys=True),'FINGERPRINT_NAMES':json.dumps(fingerprint),'RUNTIME_HASHES':json.dumps(runtime_hashes,sort_keys=True),'NATIVE_NAMES':','.join(runtime_hashes),'SUITE_LITERAL':json.dumps((H/'suite.js').read_text(),ensure_ascii=False)}
# Single pass prevents matching placeholder words inside quoted native source.
code=re.sub('|'.join(map(re.escape,replacements)),lambda m:replacements[m[0]],code)
(H/'adapter.js').write_text(code+'\nwindow.__ENV_B__=window.__ENV_A__;\nwindow.__ENV_C__=window.__ENV_A__;\nwindow.__ENV_KAPPA_A__=window.__ENV_A__;\n')
print('capsule',len(s),'values',len(names),'settings',len(settings))
