"""Exact native output comparisons; never changes an expectation/tolerance."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;E=P/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 checks={};rows=[];inputs={};build=read(P/'BUILD.json')
 for i,name in enumerate(['helo-hover','helo-route','harpoon-route']):
  a=E/f'extra-r4-natural/friendly/after-{i}.json';z=E/f'regression/natural/friendly/after-{i}.json';x,y=read(a),read(z);checks[name+'.entireNativeOutputExact']=x==y;checks[name+'.noUncommandedInventoryUse']=y['inventoryUnchanged'];checks[name+'.coreAndFaultsZero']=not y['core']and not any(y['faults']);rows.append({'case':name,'entireOutputExact':x==y,'R4Births':len(x['births']),'CBirths':len(y['births']),'R4FinalTracks':len(x['final']),'CFinalTracks':len(y['final']),'R4GlobalRng':x['rng'],'CGlobalRng':y['rng'],'note':'Truth diagnostic fields compared AFTER_ACTION only, never used by game.'});inputs.update({str(p.relative_to(P)):sha(p)for p in [a,z]})
 for task,file in [('auto-iff','auto-iff.json'),('idle','idle-and-dom.json')]:
  a=E/f'extra-r4-{task}/friendly'/file;z=E/f'regression/{task}/friendly'/file;x,y=read(a),read(z);assert not x['errors']and not y['errors'];checks[task+'.allOriginalChecksPass']=all(y['checks'].values());checks[task+'.exactChecks']=x['checks']==y['checks'];key='result'if task=='auto-iff'else'rows';checks[task+'.exactNativeResult']=x[key]==y[key];inputs.update({str(p.relative_to(P)):sha(p)for p in [a,z]})
 a=E/'reference-r4/webgl8-observed-world.json';z=E/'regression/webgl8/observed-world.json';x,y=read(a),read(z);assert x['htmlSha256']==build['baselineHtmlSha256']and y['htmlSha256']==build['htmlSha256'];webgl=[]
 for q,r in zip(x['records'],y['records']):
  assert(q['weapon'],q['enabled'])==(r['weapon'],r['enabled']);webgl.append({'weapon':r['weapon'],'terminationEnabled':r['enabled'],'R4Reason':q['final']['missile']['reason'],'CReason':r['final']['missile']['reason'],'R4TargetAlive':q['final']['targetAlive'],'CTargetAlive':r['final']['targetAlive'],'nativeFinalExact':q['final']==r['final'],'webglFramesAdvance':r['framesAfterFlight'][1]>r['framesAfterFlight'][0]})
 checks['webgl8.nativeOutcomesMatchR4']=all(r['R4Reason']==r['CReason']and r['R4TargetAlive']==r['CTargetAlive']for r in webgl);checks['webgl8.actualRenderFramesAdvanceAll8']=len(webgl)==8 and all(r['webglFramesAdvance']for r in webgl);checks['webgl8.original29Pass']=all(y['checks'].values())and not y['errors'];inputs.update({str(p.relative_to(P)):sha(p)for p in [a,z]})
 result={'schema':'AEGIS_TRACK_C_NATIVE_RUNTIME_COMPARISON_1','status':'PASS'if all(checks.values())else'REVIEW_REQUIRED','checks':checks,'natural':rows,'webgl':webgl,'inputs':inputs,'candidateSha256':build['htmlSha256'],'baselineSha256':build['baselineHtmlSha256'],'webglReferenceMeaning':'Hash-matched R4 historical actual-WebGL results, not another fresh R4 execution. Current C8 are fresh actual WebGL.','expectationsOrTolerancesUpdated':False};(P/'RUNTIME_COMPARISON.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':checks,'natural':rows,'webgl':webgl}));return 0 if result['status']=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())
