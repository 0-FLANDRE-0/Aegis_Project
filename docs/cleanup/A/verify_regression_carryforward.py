"""Attribute prior regressions to their actual HTML; prove table-only equivalence."""
from pathlib import Path
import base64,gzip,hashlib,json,re,subprocess
H=Path(__file__).resolve().parent;R=H.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
previous=subprocess.check_output(['git','show','c3388dec45dd8a80022a756699057adf23f0df36:Aegis_SIM_v48_WIP_CLEAN_A.html'],cwd=R)
current=(R/'Aegis_SIM_v48_WIP_CLEAN_A.html').read_bytes()
def core(b):return re.sub(rb'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',b'',gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',b)[1])))
def shell(b):
 s=re.sub(rb'(data-c55-index="13">)[^<]+',rb'\1<MAIN>',b);m=re.search(rb'const records=(\[.*?\]);',s,re.S);r=json.loads(m[1]);r[13]={**r[13],'rawBytes':None,'gzipBytes':None,'sha256':None}
 return s[:m.start(1)]+json.dumps(r,separators=(',',':')).encode()+s[m.end(1):]
baseline=json.loads((H/'approved-raid-baselines.json').read_text())
checks={'gameCoreByteExact':core(previous)==core(current),'approvedBaselineCoreHashMatch':sha(core(current))==baseline['gameCoreWithoutEnvelopeSha256'],'shellAssetsAndUIByteExact':shell(previous)==shell(current)}
sources=[]
for suite in ['release','common','natural']:
 p=H/'evidence/c2/CLEAN'/(suite+'.json.gz');j=json.loads(gzip.decompress(p.read_bytes()));source=j.get('htmlSha256')or j.get('product',{}).get('htmlSha256')
 checks[suite+'.sourceRecorded']=source==sha(previous)
 sources.append({'suite':suite,'shots':len(j['rows']),'executedHtmlSha256':source,'reuseReason':'No flight, fuze, seeker, guidance, combat, input or UI code changed; only diagnostic envelope data/accessor differs.'})
p=H/'evidence/c2/CLEAN/webgl/observed-world.json';j=json.loads(p.read_text());checks['webgl.sourceRecorded']=j['htmlSha256']==sha(previous)
sources.append({'suite':'natural-detection-formal-VLS-WebGL','shots':len(j['records']),'executedHtmlSha256':j['htmlSha256']})
result={'pass':all(checks.values()),'checks':checks,'previousHtmlSha256':sha(previous),'currentHtmlSha256':sha(current),'gameCoreWithoutEnvelopeSha256':sha(core(current)),'unchangedRegressionResults':sources,'freshChecksThisRevision':['190 extra grid shots','283 native function hashes','UI 88','DDG/CG table status and isolation','120s idle and combat world hashes'],'notRerunThisRevision':['300 release flights','180 common flights','28 natural RF conditions','8 WebGL flights','15 domain suites']}
(H/'evidence/regression-carryforward.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['pass'];print(json.dumps({'pass':result['pass'],'checks':checks}))
