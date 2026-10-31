"""Document the rejected A stop control and verify its diagnostic-only replacement."""
from pathlib import Path
import copy,hashlib,json,math
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(d):return [json.loads(l)for p in sorted(d.glob('worker*.jsonl'))for l in p.read_text().splitlines()]
def clean(q):
 q=copy.deepcopy(q);q['result'].pop('elapsedMs',None);q['refreshSummary'].pop('totalMs',None)
 for s in q['refreshSummary']['samples']:s.pop('elapsedMs',None)
 return q
def digest(q):return hashlib.sha256(json.dumps(clean(q),sort_keys=True,separators=(',',':')).encode()).hexdigest()
original=read(E/'trials');corrected=read(E/'a-stop-corrected');probe=read(E/'a-stop-probe');old={r['caseId']:r for r in original};new={r['caseId']:r for r in corrected};bad=[]
for r in original:
 if r['experiment']!='A':continue
 for s in r['data']['shots']:
  speed=math.hypot(s['shipVelocityMps']['x'],s['shipVelocityMps']['y'])
  if speed>=1e-6:bad.append({'caseId':r['caseId'],'ship':r['ship'],'bearing':r['bearing'],'count':r['count'],'seed':r['seed'],'shell':s['id'],'step':s['launchStep'],'speedMps':speed})
nonA=[{'caseId':r['caseId'],'experiment':r['experiment'],'equal':digest(r['data'])==digest(old[r['caseId']]['data']),'originalHash':digest(old[r['caseId']]['data']),'correctedHash':digest(r['data'])}for r in probe if r['experiment']!='A']
repeats=[{'caseId':r['caseId'],'equal':r['caseId']in new and digest(r['data'])==digest(new[r['caseId']]['data']),'probeHash':digest(r['data']),'replayHash':digest(new[r['caseId']]['data'])if r['caseId']in new else None}for r in probe if r['experiment']=='A']
checks={'corrected480UniqueA':len(corrected)==len(new)==480 and set(new)=={r['caseId']for r in original if r['experiment']=='A'},'sameInputs':all(all(r[k]==old[r['caseId']][k]for k in ['ship','seed','bearing','count','experiment','flags'])for r in corrected),'strictZeroAtRelease':all(math.hypot(s['shipVelocityMps']['x'],s['shipVelocityMps']['y'])<1e-6 for r in corrected for s in r['data']['shots']),'nonAExactIsolation':len(nonA)==4 and all(r['equal']for r in nonA),'correctedARepeat':bool(repeats)and all(r['equal']for r in repeats),'fourWorkersComplete':all((E/'a-stop-corrected'/f'worker{i}-complete.json').exists()and not json.loads((E/'a-stop-corrected'/f'worker{i}-complete.json').read_text())['errors']for i in range(4)),'oldGuardNotWeakened':len(bad)==10}
result={'pass':all(checks.values()),'checks':checks,'originalPrimaryMatrixCases':2400,'originalAReleaseCount':sum(len(r['data']['shots'])for r in original if r['experiment']=='A'),'originalFailedStopReleases':bad,'originalMaxResidualShipSpeedMps':max(r['speedMps']for r in bad),'cause':'Native dynamics owns a private sway closure. STOP reset public shipNav.swayMps but impactImpulse changed the private sway, which navigation wrote back before launch.','correction':'Diagnostic A calls existing getShipDynamicsV15().haltHorizontalContact() before each fixed tick. Original hooks.js/build_fixture.py and product are unchanged.','nonAComparisons':nonA,'correctedARepeat':repeats,'correctedCases':len(corrected),'correctedShots':sum(len(r['data']['shots'])for r in corrected),'correctedSourceHashes':sorted({r['instrumentedHtmlSha256']for r in corrected}),'originalAResultsPreserved':'evidence/trials/worker*.jsonl','primarySelection':'1920 original non-A cases + 480 corrected A cases by identical caseId/inputs; original A remains nonprimary, never overwritten.'}
result['correctedADifferences']=[{'caseId':r['caseId'],'originalHash':digest(old[r['caseId']]['data']),'correctedHash':digest(r['data']),'oldShots':len(old[r['caseId']]['data']['shots']),'newShots':len(r['data']['shots'])}for r in corrected if digest(r['data'])!=digest(old[r['caseId']]['data'])]
(E/'a-stop-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'checks':checks,'oldResidualMps':result['originalMaxResidualShipSpeedMps'],'correctedCases':len(corrected)},ensure_ascii=False));raise SystemExit(not result['pass'])
