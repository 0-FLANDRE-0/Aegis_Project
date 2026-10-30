"""Reproduction/provenance checks; expected contract FAIL stays FAIL."""
from pathlib import Path
import ast,base64,gzip,hashlib,json,math,re,subprocess,datetime
from zoneinfo import ZoneInfo
H=Path(__file__).resolve().parent;R=H.parents[3];checks={}
read=lambda n:json.loads((H/n).read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
for f in read('kit/MANIFEST.json')['files']:
 b=(H/'kit'/f['name']).read_bytes();checks['kit.'+f['name']]=len(b)==f['bytes']and sha(b)==f['sha256']
for f in H.glob('*.py'):ast.parse(f.read_text())
checks['pythonSyntax']=True
subprocess.run(['node','--check',str(H/'run_active_contracts.cjs')],check=True)
old=(H/'active/active-contract-results.json').read_bytes();run=subprocess.run(['node',str(H/'run_active_contracts.cjs')],capture_output=True,text=True)
checks['activeContractExit1Expected']=run.returncode==1 and not run.stderr
checks['activeResultBitRepeat']=old==(H/'active/active-contract-results.json').read_bytes()
result=read('active/active-contract-results.json');caps=[read('active/'+v+'-capture.json')for v in ['DZT','HANDOFF']]
checks['realSm6ProfilesSame']=caps[0]['profile']==caps[1]['profile']and all(c['runtime']['isSM6']and c['runtime']['profileId']=='SM6_BLKIA_SIM'and c['rfModel']=='RF_V2'and c['runtime']['lifeS']==0 and c['simStepCounter']==0 for c in caps)
checks['captureErrors0']=not read('active/capture-summary.json')['errors']and all(not c['coreFailures']for c in caps)
checks['suppliedBaselineFourFailures']=read('kit-replay/contract_results.json')['failed']==4
checks['savedArithmeticPass']=read('kit-replay/evidence_results.json')['savedEvidenceArithmeticChecks']=='PASS'
checks['savedOriginExact']=read('active/saved-evidence-origin.json')['pass']
live=read('active/live-point-equivalence.json');checks['native22Exact']=live['pass']and live['points']==22 and live['maxNativeVsVmDifference']==0 and not live['errors']
proof=[]
for cap in caps:
 name='Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html'if cap['variant']=='HANDOFF'else'archive/v48/WIP_FUZE_ZEM_A/Aegis_SIM_v48_WIP_FUZE_ZEM_A.html';raw=(R/name).read_bytes();source=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)</script>',raw)[1])).decode();functions=[]
 for n,s in cap['functions'].items():functions.append({'name':n,'sha256':sha(s.encode()),'captureHashMatches':sha(s.encode())==cap['functionHashes'][n],'inSelectedMain':s in source})
 checks[cap['variant']+'.actualFunctionSource']=all(x['captureHashMatches']and x['inSelectedMain']for x in functions)
 checks[cap['variant']+'.htmlPin']=sha(raw)==cap['htmlSha256'];proof.append({'variant':cap['variant'],'functions':functions})
for v in result['variants']:
 checks[v['variant']+'.twoCategoriesReproduced']=v['contractFailures']==3 and all(not t['pass']for t in v['tests'])
 checks[v['variant']+'.pipeline']=all(v['pipelineChecks'].values())
 p=v['profile'];generated=p['monopulseNoiseDeg']/math.sqrt(.35+12)+p['monopulseGlintDeg']*.45
 checks[v['variant']+'.generatedNoiseFormula']=all(abs(n['generatedSigmaDeg']-generated)<1e-12 for n in v['noise'])
for f in read('input-provenance.json')['protectedFiles']:checks['preserved.'+f['path']]=sha((R/f['path']).read_bytes())==f['sha256']
(H/'active/source-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
out={'schema':'AEGIS_ARH_MEASUREMENT_CONTRACT_A_VERIFICATION_1','diagnosticPass':all(checks.values()),'checks':checks,'measurementContractsPass':False,'reproducedMismatchCategories':2,'activeContractFailureChecksPerVariant':3,'profileId':caps[1]['profile']['id'],'profileSha256':caps[1]['profileSha256'],'nativeGeometryPoints':22,'nativeVsVmMaxDifference':0,'isolatedNoisyMeasurements':40000,'newFlightIntegrationSteps':0,'productCodeChanges':0,'coefficientChanges':0,'productFixApplied':False,'newFlightRegressionRun':False,'reviewedAtKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat()};(H/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'diagnosticPass':out['diagnosticPass'],'failed':[k for k,v in checks.items()if not v],'mismatches':2,'productChanges':0}));raise SystemExit(0 if out['diagnosticPass']else 1)
