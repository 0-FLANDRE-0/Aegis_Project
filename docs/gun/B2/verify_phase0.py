"""Final Phase0 completeness/provenance validation. Run only after all workers."""
from pathlib import Path
import collections,hashlib,json,math
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for p in(E/'trials').glob('worker*.jsonl'):rows.extend(json.loads(x)for x in p.read_text().splitlines())
originalRows=rows;corrected=[json.loads(x)for p in(E/'a-stop-corrected').glob('worker*.jsonl')for x in p.read_text().splitlines()];replacement={r['caseId']:r for r in corrected}
assert len(corrected)==len(replacement)==480 and set(replacement)=={r['caseId']for r in originalRows if r['experiment']=='A'}
rows=[replacement[r['caseId']]if r['experiment']=='A'else r for r in originalRows]
checks={};records={}
checks['exact2400Cases']=len(rows)==2400 and{r['caseId']for r in rows}==set(range(2400))
groups=collections.defaultdict(list)
for r in rows:groups[r['ship'],r['bearing'],r['count'],r['experiment']].append(r)
checks['80Conditions30Seeds']=len(groups)==80 and all(len(a)==30 and{r['seed']for r in a}==set(range(419010,419040))for a in groups.values())
checks['everyCaseFreshGameWindow']=all(r['isolation']=='FRESH_GAME_PAGE_PER_CASE'for r in rows)
checks['knownInstrumentedSources']=({r['instrumentedHtmlSha256']for r in originalRows}=={'39dc367caa065db140fc606b208c895245d97aa36342575b47cb23f977c447f7'}and{r['instrumentedHtmlSha256']for r in corrected}=={'85089cee8bac6e7acc5008ffa2dbf1d558cb457e30e948dd6bad67d1aa8b2537'})
checks['allShotsLogged']=all(len(r['data']['shots'])==r['data']['result']['shots']for r in rows)
checks['BReleasedSolutionCurrentTick']=all(s['solutionAgeS']==0 for r in rows if r['experiment']=='B'for s in r['data']['shots'])
checks['BSolverActuallyCalled']=all(r['data']['refreshSummary']['attempts']>=len(r['data']['shots'])for r in rows if r['experiment']=='B')
checks['cuesRecorded']=all(s['cueStep']is not None and s['slewS']>=0 for r in rows for s in r['data']['shots'])
checks['ownshipStoppedA']=all(math.hypot(s['shipVelocityMps']['x'],s['shipVelocityMps']['y'])<1e-6 for r in rows if r['experiment']=='A'for s in r['data']['shots'])
completions=[load(E/'trials'/f'worker{i}-complete.json')for i in range(4)];checks['fourWorkersComplete']=all(q['cases']==600 and not q['errors']for q in completions)
for name,path in [('static','static-audit.json'),('nativeVsHooks','hook-equivalence/results.json'),('httpTransport','http-boot/results.json'),('repeats','repeats/results.json'),('unitProbes','unit-probes/results.json'),('originContract','origin-contract/results.json'),('approvedReferences','approved-reference-validation.json'),('approvedGuard','reference-guard-tests.json'),('correctedAControl','a-stop-audit.json')]:
 q=load(E/path);checks[name]=q['pass'];records[name]={'path':path,'sha256':sha(E/path)}
checks['productUnchanged']=sha(R/'Aegis_SIM_v48_WIP_GUN_B1.html')=='c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc'
checks['noPhase1HtmlProduced']=not(R/'Aegis_SIM_v48_WIP_GUN_B2.html').exists()
start=load(E/'execution-start.json');checks['loggerCoreFrozen']=all(sha(B/p)==v for p,v in start['files'].items()if Path(p).name in ['hooks.js','build_fixture.py'])
result={'pass':all(checks.values()),'checks':checks,'cases':len(rows),'shots':sum(len(r['data']['shots'])for r in rows),'records':records,'productHtmlSha256':sha(R/'Aegis_SIM_v48_WIP_GUN_B1.html'),'phase':'PHASE0_ONLY_AWAIT_USER_APPROVAL','completions':completions};(E/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['records','completions']}));raise SystemExit(not result['pass'])
