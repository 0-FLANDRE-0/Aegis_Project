"""Reuse the original descriptive analysis, not any new flight/kill model."""
from pathlib import Path
import ast,collections,csv,gzip,hashlib,json,math,statistics,sys,subprocess
from source import P,B,R,provenance,sha
E=P/'evidence';rows=sorted([json.loads(l)for p in E.glob('worker*.jsonl')for l in p.read_text().splitlines()],key=lambda r:r['caseId'])
assert len(rows)==60 and {r['caseId']for r in rows}==set(range(60))
key=lambda r:(r['ship'],r['bearing'],r['count'],r['seed'],r['experiment'])
assert len({key(r)for r in rows})==60 and all(r['count']==1 and r['flags']=={}and r['experiment']=='BASE'for r in rows)
scope={'math':math,'statistics':statistics,'collections':collections};tree=ast.parse((B/'analyze.py').read_text());names=['stats','norm','resolve','budget','summarize'];functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names];assert len(functions)==len(names);exec(compile(ast.Module(body=functions,type_ignores=[]),str(B/'analyze.py')+'::FUNCTIONS_ONLY','exec'),scope);summarize=scope['summarize'];resolve=scope['resolve'];stats=scope['stats']
selected={};source_files=[];old_lines=[]
for p in sorted((B/'evidence/trials').glob('worker*.jsonl')):
 digest=hashlib.sha256()
 with p.open('rb')as f:
  for line in f:
   digest.update(line);r=json.loads(line)
   if key(r)in {key(q)for q in rows}:assert key(r)not in selected;selected[key(r)]=r;old_lines.append(line)
 source_files.append({'path':str(p.relative_to(R)),'sha256':digest.hexdigest()})
assert len(selected)==60
old=[selected[key(r)]for r in rows];assert all(r['data']['caseBootState']==selected[key(r)]['data']['caseBootState']for r in rows),'INITIAL_STATE_PROTOCOL_DIFFERED'
(E/'reviewed-before-60.jsonl.gz').write_bytes(gzip.compress(b''.join(old_lines),9,mtime=0))
groups=[]
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 for bearing in [0,90]:
  a=[r for r in old if r['ship']==ship and r['bearing']==bearing];b=[r for r in rows if r['ship']==ship and r['bearing']==bearing];assert len(a)==len(b)==15
  groups.append({'ship':ship,'bearing':bearing,'before':summarize(a),'after':summarize(b)})
changes=[]
for b,a in zip(old,rows):
 before,after=b['data']['result'],a['data']['result'];fields=[k for k in before.keys()|after.keys()if k!='elapsedMs'and before.get(k)!=after.get(k)]
 changes.append({'key':key(a),'phase0CaseId':b['caseId'],'caseId':a['caseId'],'fieldsChanged':fields,'before':{k:before[k]for k in ['shots','ciwsUsed','hpAfter','shipAlive','seconds','targets']},'after':{k:after[k]for k in ['shots','ciwsUsed','hpAfter','shipAlive','seconds','targets']}})
static=json.loads((E/'static.json').read_text());equivalence=json.loads((E/'equivalence.json').read_text());execution=json.loads((E/'execution.json').read_text());completions=[json.loads((E/f'worker{i}-complete.json').read_text())for i in range(2)];adverse=json.loads((E/'adverse-native.json').read_text());assert adverse['pass']
checks={'matrix60':len(rows)==60,'15PerGroup':all(g['after']['trials']==15 for g in groups),'sameBootState':True,'staticPass':static['pass'],'runtimeFunctionsExact':all(c['runtimeFunctionHashes']==static['runtimeExpectedHashes']for c in completions),'pageErrors0':all(not c['errors']for c in completions),'nativeAndReplayEquivalent':equivalence['pass'],'sourceExactlyMergedMain':provenance()['productHtmlSha256']=='4c5191753025406697520c63afcc97c116a83c4b6b924a4b605b49233c697eeb','flagsOff':all(not r['flags']for r in rows),'diagnosticBudgetClosure':all(g['after']['metrics']['budget.closureErrorM']['max']is None or g['after']['metrics']['budget.closureErrorM']['max']<1e-8 for g in groups),'noGameEdits':not subprocess.check_output(['git','diff','--name-only','cce180255e0f76b804a2ae6a3b6078aec2f9dea8','--',':(top,glob)Aegis_SIM_*.html'],cwd=R,text=True).strip()}
checks['adverseNativeExact']=adverse['pass'];worse=[r for r in changes if r['after']['hpAfter']<r['before']['hpAfter']]
residual=[]
for r in rows:
 for s in r['data']['shots']:
  if r['ship'].startswith('CG')and r['bearing']==90 and s['outcome']=='MFF_ET_BACKUP'and s.get('assignedTargetAliveBeforeBurst'):
   residual.append({'seed':r['seed'],'shell':s['id'],'solutionAgeS':s['solutionAgeS'],'cachedSolveVzMps':s['solveTarget']['vzMps'],'currentObservedVzMps':s['observation']['velocityMps']['z'],'truthVzMpsAfterActionOnly':s['truthAtRelease']['velocityMps']['z'],'pointingVerticalM':s['pointing']['verticalMissM'],'cpa':s['cpa'],'budget':scope['budget'](s)})
(E/'residual-et.json').write_text(json.dumps({'rows':residual,'count':len(residual),'policy':'AFTER_ACTION diagnostic bookkeeping. No truth input to control. Cached/current velocities come from the existing real solver/observed track.'},indent=2)+'\n')
q={'pass':all(checks.values()),'passMeans':'Diagnostic integrity and source preservation, not approval of all combat outcome changes.','checks':checks,'cases':60,'additionalNativeCases':4,'additionalReplayCases':2,'adverseNativeCases':2,'adverseHpCases':worse,'noHpOutcomeRegression':not worse,'seeds':list(range(419010,419025)),'groups':groups,'caseChanges':changes,'historicalSourceFiles':source_files,'provenance':provenance(),'matrixElapsedS':execution['elapsedS'],'equivalenceElapsedS':equivalence['elapsedS'],'adverseNativeElapsedS':adverse['elapsedS'],'comparison':'Same 60 inputs, same fresh-page/native G7 protocol; only the product AIR receiver contract differs. Outcome populations can differ and no per-shell success matching is assumed.','rules':'Truth read only in diagnostic and native physical fuze; no coefficient tuning or expectation updates.'}
(E/'summary.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
with(E/'case-comparison.csv').open('w',newline='')as f:
 fields=['ship','bearing','seed','oldCaseId','newCaseId','shotsBefore','shotsAfter','ciwsBefore','ciwsAfter','hpBefore','hpAfter','targetBefore','targetAfter'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
 for d in changes:w.writerow(dict(zip(fields,[d['key'][0],d['key'][1],d['key'][3],d['phase0CaseId'],d['caseId'],d['before']['shots'],d['after']['shots'],d['before']['ciwsUsed'],d['after']['ciwsUsed'],d['before']['hpAfter'],d['after']['hpAfter'],json.dumps(d['before']['targets']),json.dumps(d['after']['targets'])])))
with(E/'shot-comparison.csv').open('w',newline='')as f:
 fields=['version','ship','bearing','seed','shell','outcome','releaseStep','solutionAgeS','observationCrossM','observationVerticalM','cpaM','cpaCrossM','cpaVerticalM','assignedArrivalM','assignedAliveBeforeBurst','pointingCrossM','pointingVerticalM','limitM'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
 for tag,data in [('BEFORE',old),('AFTER',rows)]:
  for r in data:
   for s in r['data']['shots']:
    obs=resolve(s['trackPositionErrorM'],s['launchVelocityMps']);cpa=s.get('cpa')or{};res=cpa.get('resolvedM')or{};w.writerow(dict(zip(fields,[tag,r['ship'],r['bearing'],r['seed'],s['id'],s['outcome'],s['launchStep'],s['solutionAgeS'],obs['cross'],obs['vertical'],cpa.get('missM'),res.get('cross'),res.get('vertical'),s.get('assignedArrivalDiagnostic',{}).get('arrivalMissM'),s.get('assignedTargetAliveBeforeBurst'),s['pointing']['crossMissM'],s['pointing']['verticalMissM'],s['pointing']['limitM']])))
print(json.dumps({'pass':q['pass'],'cases':60,'shotsBefore':sum(g['before']['shots']for g in groups),'shotsAfter':sum(g['after']['shots']for g in groups),'groups':[{k:g[k]for k in ['ship','bearing']}for g in groups]}));raise SystemExit(not q['pass'])
