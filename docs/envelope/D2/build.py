"""Replace only the historical ENV_D data/accessor block in the latest HTML."""
from pathlib import Path
import base64,gzip,hashlib,json,re,subprocess
H=Path(__file__).resolve().parent;R=H.parents[2]
sha=lambda x:hashlib.sha256(x).hexdigest()
raw=(R/'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html').read_bytes();assert sha(raw)=='eb1f5cebbfe991732b2855df625030b0691ff7cdd8047e9a01cc2711010b6e5f'
m=json.loads((H/'results/measurement.json').read_text());repeat=json.loads((H/'evidence/determinism.json').read_text());assert repeat['pass']
proof=json.loads((H/'evidence/path.json').read_text());assert proof['pass']
p=json.loads((H/'provenance.json').read_text());fixture=json.loads((H/'path-fixture.json').read_text());inp=json.loads((H/'inputs.json').read_text())
hashes=fixture['functionHashes'];extra=json.loads((H/'extra-models.json').read_text())
excluded={'WIP87_PENDING_PK','WIP87_PROX_CONTEXT','WIP87_CASE_META','WIP88_LAST_PK_DETAIL','SELECTED_SHIP_REGISTRATION','IS_BUNKER','ESSM_EMCON_POLICY','SM2_ALLOW_IOG_TEST_FIRE','SM2_EMCON_POLICY'}
modelValues={k:v for k,v in (inp['data']|extra).items()if k not in excluded};models=list(modelValues)
# Playwright serializes function-valued port members as null; JSON.stringify
# used by the live read-only capture omits them. These are transport API
# methods, not model coefficients. Keep the frozen measurement input unchanged.
portMethods=['suspend','expire','step','create','covarianceAt','rebind','advisedTgo','targetState','returnState','advisory','accept','snapshot','profile']
assert all(modelValues['WEAPON_LINK_B3'][k]is None for k in portMethods)
modelValues['WEAPON_LINK_B3']={k:v for k,v in modelValues['WEAPON_LINK_B3'].items()if k not in portMethods}
conditions={'targetLabel':'Kh-35U','targetKind':'NATIVE_ASM_STRAIGHT_CONSTANT_VELOCITY','guidanceRevision':'NEAR_VERTICAL_PATH_FIX_A','fixedDtS':1/60,'rangeCapKm':500,'minimumRangeKm':5,'outerResolutionKm':1,'effectiveResolutionKm':5,'outerMinimumEffectShots':1,'effectiveMinimumLethalShots':3,'shotsPerDistance':5,'idealSupport':True,'targetAi':False,'nativeSystemDamageObservers':True,'nativeAsmDamagePrefix':True,'outcomePolicy':'NATIVE_RESULT_AND_EXPLICIT_MISSION_FLAGS','fuzeSeaStateFactor':1.0649859543133355}
boundaryHash=sha((H/'private.js').read_bytes()+(R/'docs/envelope/D/diagnostic/boundaries.json').read_bytes())
fingerprint={'diagnosticBoundaryHash':boundaryHash,'conditions':conditions,'seeds':m['seeds'],'nativeSourceHashes':hashes,'models':modelValues,'settings':inp['settings']}
profileHash=subprocess.check_output(['node','-e','const f=require("fs"),c=require("crypto");const q=JSON.parse(f.readFileSync(0,"utf8"));process.stdout.write(c.createHash("sha256").update(JSON.stringify(q)).digest("hex"))'],input=json.dumps(fingerprint).encode()).decode()
def points(q,lethal=False):
 v=[s['interceptPointKm']for s in q['shots']if s['lethal'if lethal else'success']]if q else[]
 return {'meanKm':sum(v)/len(v),'minKm':min(v),'maxKm':max(v),'shotCount':len(v)}if v else None
rows=[]
for r in m['rows']:
 if r.get('auxiliary'):continue
 rows.append({k:r.get(k)for k in ['cellId','weapon','targetLabel','altM','motion','targetSpeedMps','crossSpeedMps','maxRangeKm','effectiveRangeKm','capReached','maxBoundary','nextBoundary','effectiveBoundary','breakPoint']}|{'maxInterceptPoint':points(r['maxBoundary']),'effectiveInterceptPoint':points(r['effectiveBoundary'],True)})
assert len(rows)==120
table={'schema':'AEGIS_ENVELOPE_TABLE_D_REMEASURE_A_1','provenance':'GAME_ENGINE_COMPUTED','policy':'SIM_TUNED_GAME_MODEL_ONLY','guidanceRevision':'NEAR_VERTICAL_PATH_FIX_A','envelopeMeasured':True,'profileHash':profileHash,'conditions':conditions,'seeds':m['seeds'],'rows':rows,'nativeSourceHashes':hashes,'baseHtmlSha256':sha(raw),'measurementCalls':m['calls'],'historicalComparison':{'ENV_D':'HISTORICAL_KAPPA_PIP_LOS_A','ENV_C':'HISTORICAL_AIR_POINT_PRE_KAPPA_PIP_LOS'}}
(H/'ENVELOPE_TABLE_D.json').write_text(json.dumps(table,ensure_ascii=False,indent=2)+'\n');(H/'fingerprint.json').write_text(json.dumps(fingerprint,indent=2)+'\n')
block='''// ENV_D_DATA_BEGIN — DIAGNOSTIC_ONLY, no gameplay consumer or startup work.
const ENVELOPE_TABLE_D=TABLE;
window.__ENV_D__=(()=>{
 const clone=x=>JSON.parse(JSON.stringify(x));
 async function hash(x){const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(x)));return [...new Uint8Array(d)].map(v=>v.toString(16).padStart(2,'0')).join('');}
 function capture(){return clone({diagnosticBoundaryHash:BOUNDARY,conditions:ENVELOPE_TABLE_D.conditions,seeds:ENVELOPE_TABLE_D.seeds,nativeSourceHashes:HASHES,models:{MODELS},settings:Object.fromEntries(SETTINGS.map(k=>[k,window[k]]).filter(([,v])=>['number','boolean','string'].includes(typeof v)))});}
 async function status(){const input=capture(),current=await hash(input),fn={FUNCTIONS},actual=await Promise.all(Object.entries(fn).map(async([k,f])=>[k,await hashText(f.toString())])),changedNativeFunctions=actual.filter(([k,v])=>input.nativeSourceHashes[k]!==v).map(([k])=>k),match=current===ENVELOPE_TABLE_D.profileHash&&!changedNativeFunctions.length;return {provenance:'GAME_ENGINE_COMPUTED',guidanceRevision:'NEAR_VERTICAL_PATH_FIX_A',envelopeMeasured:true,rows:ENVELOPE_TABLE_D.rows.length,targetLabel:'Kh-35U',currentProfileHash:current,tableProfileHash:ENVELOPE_TABLE_D.profileHash,match,changedNativeFunctions,recalculationRequired:!match,message:match?'게임 엔진 계산표 일치':'재계산 필요'};}
 async function hashText(s){const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return [...new Uint8Array(d)].map(v=>v.toString(16).padStart(2,'0')).join('');}
 return Object.freeze({table:()=>clone(ENVELOPE_TABLE_D),capture,status});
})();
// ENV_D_DATA_END'''
replacement={'TABLE':json.dumps(table,ensure_ascii=False,separators=(',',':')),'BOUNDARY':json.dumps(boundaryHash),'HASHES':json.dumps(hashes,separators=(',',':')),'MODELS':','.join(models),'SETTINGS':json.dumps(list(inp['settings'])),'FUNCTIONS':','.join(hashes)}
block=re.sub(r'\b(TABLE|BOUNDARY|HASHES|MODELS|SETTINGS|FUNCTIONS)\b',lambda x:replacement[x[0]],block)
html=raw.decode();payload=re.search(r'data-c55-index="13">([^<]+)</script>',html);old=gzip.decompress(base64.b64decode(payload[1])).decode();pattern=r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END';assert len(re.findall(pattern,old))==1
main=re.sub(pattern,lambda _:block,old);assert re.sub(pattern,'',main)==re.sub(pattern,'',old)
packed=gzip.compress(main.encode(),9,mtime=0);html=html[:payload.start(1)]+base64.b64encode(packed).decode()+html[payload.end(1):]
manifest=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(manifest[1]);rs[13].update(rawBytes=len(main.encode()),gzipBytes=len(packed),sha256=sha(main.encode()));html=html[:manifest.start(1)]+json.dumps(rs,separators=(',',':'))+html[manifest.end(1):]
out=R/'Aegis_SIM_v48_WIP_ENV_D_REMEASURE_A.html';out.write_text(html)
receipt={'output':out.name,'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'baseSha256':sha(raw),'profileHash':profileHash,'rows':len(rows),'gameFunctionChanges':0,'outsideDataBlockByteExact':True}
(H/'build.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
