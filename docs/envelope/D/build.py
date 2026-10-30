"""Append measured table and an explicit read-only integrity accessor only.

The complete pre-existing main JS, including Kappa/B4/termination and the old
diagnostic capsule, is byte-identical after removing the new data block.
The ASM measurement runner remains offline in docs/envelope/D, not in gameplay.
"""
from pathlib import Path
import base64,gzip,hashlib,json,re,subprocess
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'diagnostic'
BASE='Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html'
NAME='Aegis_SIM_v48_WIP_ENV_D.html'
base=R/BASE
if not base.exists():base=R/'archive/v48/WIP_KAPPA_PIP_LOS_A'/BASE
raw=base.read_bytes();assert hashlib.sha256(raw).hexdigest()=='b81e2f3fbf45eeaa750e7d6edea59c2c024ed0128eaf6a0b695c9ea2bd84e58e'
measured=json.loads((H/'results/measurement.json').read_text())
assert len(measured['rows'])==126
determinism=json.loads((H/'evidence/determinism.json').read_text());assert determinism['pass']
pathProof=json.loads((H/'evidence/path.json').read_text());assert pathProof['pass']
deps=json.loads((D/'dependencies.json').read_text());assert not deps['missing']
functionHashes={r['name']:r['runtimeHash']for r in deps['rows']if r.get('runtimeHash')and r['name']!='envNativeAsmDamagePrefixD'}
prefixProof=json.loads((D/'native-asm-prefix-proof.json').read_text())
functionHashes['updateEnemyMissileBaseC52']=prefixProof['originalRuntimeHash']
# Runtime state, chosen ship geometry and operator authorization are deliberately
# excluded. All native flight/fuze/Pk/ASM configuration values are retained.
excluded={'WIP87_PENDING_PK','WIP87_PROX_CONTEXT','WIP87_CASE_META','WIP88_LAST_PK_DETAIL','SELECTED_SHIP_REGISTRATION','IS_BUNKER','ESSM_EMCON_POLICY','SM2_ALLOW_IOG_TEST_FIRE','SM2_EMCON_POLICY'}
models=[r['name']for r in deps['rows']if r['type']=='DETACHED_NATIVE_VALUE'and r['name']not in excluded]
inputData=json.loads((H/'inputs.json').read_text())
settingNames=list(inputData['settings'])
boundaryHash=hashlib.sha256(((D/'boundaries.json').read_text()+(D/'private.js').read_text()).encode()).hexdigest()
seeds=measured['seeds']
conditions={'targetLabel':'Kh-35U','targetKind':'NATIVE_ASM_STRAIGHT_CONSTANT_VELOCITY','guidanceRevision':'KAPPA_PIP_LOS_A','fixedDtS':1/60,'rangeCapKm':500,'minimumRangeKm':5,'outerResolutionKm':1,'effectiveResolutionKm':5,'outerMinimumEffectShots':1,'effectiveMinimumLethalShots':3,'shotsPerDistance':5,'idealSupport':True,'targetAi':False,'nativeSystemDamageObservers':True,'nativeAsmDamagePrefix':True,'outcomePolicy':'NATIVE_RESULT_AND_EXPLICIT_MISSION_FLAGS','interceptPointAveraging':{'outer':'ANY_NATIVE_EFFECT','inner':'KILL_OR_STRUCT_FAIL'},'fuzeSeaStateFactor':1.0649859543133355}
fingerprint={'diagnosticBoundaryHash':boundaryHash,'conditions':conditions,'seeds':seeds,'nativeSourceHashes':functionHashes,'models':{k:inputData['data'][k]for k in models},'settings':inputData['settings']}
# Node serialization is also used by the browser, avoiding Python numeric JSON
# spellings (e.g. 1.0 versus 1) in integrity fingerprints.
profileHash=subprocess.check_output(['node','-e','const c=require("crypto"),fs=require("fs");const q=JSON.parse(fs.readFileSync(0,"utf8"));process.stdout.write(c.createHash("sha256").update(JSON.stringify(q)).digest("hex"));'],input=json.dumps(fingerprint).encode()).decode()
def lethal_points(q,key='interceptPointKm'):
 values=[s[key]for s in q['shots']if s['lethal']]if q else[]
 return {'meanKm':sum(values)/len(values),'minKm':min(values),'maxKm':max(values),'shotCount':len(values)}if values else None
def boundary(q):
 if not q:return None
 return {'rangeKm':q['rangeKm'],'effectCount':q['effectCount'],'lethalCount':q['lethalCount'],'interceptPoint':q['interceptPoint'],'targetInterceptPoint':q['targetInterceptPoint'],'lethalInterceptPoint':lethal_points(q),'lethalTargetInterceptPoint':lethal_points(q,'targetInterceptPointKm'),'shots':[{k:s[k]for k in ['rngSeed','navigationSeed','outcome','samResult','retirementCause','damage','missionKills','reason','success','lethal','closestM','fuzeMissM','interceptPointKm','targetInterceptPointKm']}for s in q['shots']]}
rows=[]
for r in measured['rows']:
 if r.get('auxiliary'):continue
 reference=r['maxBoundary']or r['breakPoint']or r['effectiveBoundary']
 rows.append({k:r.get(k)for k in ['cellId','weapon','targetLabel','altM','motion','targetSpeedMps','crossSpeedMps','maxRangeKm','effectiveRangeKm','maxInterceptPoint','capReached']}|{'profileId':reference['shots'][0]['profileId'],'effectiveInterceptPoint':lethal_points(r['effectiveBoundary']),'effectiveEffectInterceptPoint':r['effectiveInterceptPoint']}|{k:boundary(r[k])for k in ['maxBoundary','nextBoundary','effectiveBoundary','breakPoint']})
table={'schema':'AEGIS_ENVELOPE_TABLE_D_1','provenance':'GAME_ENGINE_COMPUTED','policy':'SIM_TUNED_GAME_MODEL_ONLY','guidanceRevision':'KAPPA_PIP_LOS_A','envelopeMeasured':True,'profileHash':profileHash,'conditions':conditions,'seeds':seeds,'nativeSourceHashes':functionHashes,'diagnosticBoundaryHash':boundaryHash,'nativeCapsuleSha256':hashlib.sha256((D/'native-engine.js').read_bytes()).hexdigest(),'rows':rows,'historicalComparison':{'path':'docs/envelope/C/ENVELOPE_TABLE_C.json','status':'HISTORICAL_AIR_POINT_TARGET_AND_PRE_KAPPA_PIP_LOS_GUIDANCE'},'measurementCalls':measured['calls']}
(H/'ENVELOPE_TABLE_D.json').write_text(json.dumps(table,ensure_ascii=False,indent=2)+'\n')
(H/'fingerprint.json').write_text(json.dumps(fingerprint,indent=2)+'\n')
block='''// ENV_D_DATA_BEGIN — DIAGNOSTIC_ONLY, no gameplay consumer or startup work.
const ENVELOPE_TABLE_D=TABLE;
window.__ENV_D__=(()=>{
 const clone=x=>JSON.parse(JSON.stringify(x));
 async function hash(x){const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(x)));return [...new Uint8Array(d)].map(v=>v.toString(16).padStart(2,'0')).join('');}
 function capture(){return clone({diagnosticBoundaryHash:BOUNDARY,conditions:ENVELOPE_TABLE_D.conditions,seeds:ENVELOPE_TABLE_D.seeds,nativeSourceHashes:HASHES,models:{MODELS},settings:Object.fromEntries(SETTINGS.map(k=>[k,window[k]]).filter(([,v])=>['number','boolean','string'].includes(typeof v)))});}
 async function status(){const input=capture(),current=await hash(input),fn={FUNCTIONS},actual=await Promise.all(Object.entries(fn).map(async([k,f])=>{const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(f.toString()));return [k,[...new Uint8Array(d)].map(v=>v.toString(16).padStart(2,'0')).join('')];})),changedNativeFunctions=actual.filter(([k,v])=>input.nativeSourceHashes[k]!==v).map(([k])=>k),match=current===ENVELOPE_TABLE_D.profileHash&&!changedNativeFunctions.length;return {provenance:'GAME_ENGINE_COMPUTED',guidanceRevision:'KAPPA_PIP_LOS_A',envelopeMeasured:true,rows:ENVELOPE_TABLE_D.rows.length,targetLabel:ENVELOPE_TABLE_D.conditions.targetLabel,currentProfileHash:current,tableProfileHash:ENVELOPE_TABLE_D.profileHash,match,changedNativeFunctions,recalculationRequired:!match,message:match?'게임 엔진 계산표 일치':'재계산 필요'};}
 return Object.freeze({table:()=>clone(ENVELOPE_TABLE_D),capture,status});
})();
// ENV_D_DATA_END
'''
replace={'TABLE':json.dumps(table,ensure_ascii=False,separators=(',',':')),'BOUNDARY':json.dumps(boundaryHash),'HASHES':json.dumps(functionHashes,separators=(',',':')),'MODELS':','.join(models),'SETTINGS':json.dumps(settingNames),'FUNCTIONS':','.join(functionHashes)}
block=re.sub(r'\b(TABLE|BOUNDARY|HASHES|MODELS|SETTINGS|FUNCTIONS)\b',lambda m:replace[m[0]],block)
(H/'data-block.js').write_text(block)
html=raw.decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',html);oldMain=gzip.decompress(base64.b64decode(m[1])).decode()
marker='\n  completeShipStartup();';assert oldMain.count(marker)==1
main=oldMain.replace(marker,'\n'+block+marker,1)
assert main.replace('\n'+block,'',1)==oldMain
packed=gzip.compress(main.encode(),9,mtime=0);html=html[:m.start(1)]+base64.b64encode(packed).decode()+html[m.end(1):]
m=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(main.encode()),gzipBytes=len(packed),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(rs,separators=(',',':'))+html[m.end(1):]
(R/NAME).write_text(html)
receipt={'baselineHtmlSha256':hashlib.sha256(raw).hexdigest(),'output':NAME,'bytes':len(html.encode()),'sha256':hashlib.sha256(html.encode()).hexdigest(),'preexistingMainJsByteIdentical':True,'liveGameFunctionChanges':0,'nativeDiagnosticFunctions':len(functionHashes),'profileHash':profileHash,'rows':len(rows),'noMapOrLaunchConsumer':True,'offlineDiagnosticOnly':True}
(H/'build.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
