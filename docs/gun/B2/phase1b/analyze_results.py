"""Read-only post-action aggregation. No statistical fitting or expected-value edits."""
from pathlib import Path
import collections,csv,hashlib,json,statistics
P=Path(__file__).resolve().parent;OLD=P.parent/'phase1';PREVIOUS=P.parent/'phase1a';mean=lambda v:statistics.mean(v)
source=(OLD/'collect_effects.py').read_text();fn=source[source.index('def metrics(row):'):source.index('\nflat=')];scope={};exec(fn,scope);metrics=scope['metrics'];rows=[json.loads(l)for l in(P/'evidence/g7/trials.jsonl').open()];assert len(rows)==120 and len({r['caseId']for r in rows})==120;original={r['caseId']:r for f in(OLD/'evidence/g7').glob('worker*.jsonl')for l in f.open()if(r:=json.loads(l))};previous={r['caseId']:r for r in map(json.loads,(PREVIOUS/'evidence/g7/trials.jsonl').read_text().splitlines())};build=json.loads((P/'measurement-build.json').read_text());flat=[];pairs=[];off=[]
for r in rows:
 b=previous[r['caseId']];o=original[r['caseId']-1];assert r['on']and r['count']in[1,4]and 419010<=r['seed']<=419024
 for k in['ship','bearing','count','seed','on']:assert r[k]==b[k]
 for k in['ship','bearing','count','seed']:assert r[k]==o[k]
 assert not o['on']and o['result']['shots']==0 and not o['diagnostic']['bursts']and not o['diagnostic']['b2']['releases'];assert r['htmlSha256']==build['htmlSha256'];assert all(r['diagnostic']['b2']['flags'].values());assert r['result']['shots']==len(r['diagnostic']['b2']['releases']);assert all(x['ageS']==0 and x['step']==x['computedStep']for x in r['diagnostic']['b2']['releases']);assert not r['diagnostic']['core'];assert len(r['diagnostic']['afterAction']['targets'])==r['count'];after=metrics(r);before=metrics(b);flat.append(after);off.append(metrics(o));pairs.append({'caseId':r['caseId'],'ship':r['ship'],'bearing':r['bearing'],'count':r['count'],'seed':r['seed'],'before':before,'after':after,'hpWorse':after['hpAfter']<before['hpAfter'],'hpBetter':after['hpAfter']>before['hpAfter'],'pre3kmKillsBetter':after['physicalAsmKillsBefore3km']>before['physicalAsmKillsBefore3km']})
def groups(data):
 out=[]
 for key in sorted({(r['ship'],r['bearing'],r['count'],r['autoAA'])for r in data}):
  rr=[r for r in data if(r['ship'],r['bearing'],r['count'],r['autoAA'])==key];m=lambda k:mean(r[k]for r in rr);out.append(dict(zip(['ship','bearing','count','autoAA'],key),n=len(rr),meanPre3kmAsmKills=m('physicalAsmKillsBefore3km'),meanShots=m('mffShots'),meanCiwsUsed=m('ciwsUsed'),hpDamageTrials=sum(r['shipDamage']for r in rr),meanHp=m('hpAfter'),minHp=min(r['hpAfter']for r in rr),hpPositive=sum(r['shipAlive']for r in rr)))
 return out
execution=json.loads((P/'evidence/g7/execution.json').read_text());assert execution['complete']and execution['cases']==120 and not execution['errors'];assert all(x==build['modelFingerprints']['nativeSourceHashes']for x in execution['actualSources'])
q={'complete':True,'freshOnTrials':120,'reusedOffTrials':120,'previousB2AOnComparisonTrials':120,'freshGroups':groups(flat),'reusedOffGroups':groups(off),'previousB2AOnGroups':groups([p['before']for p in pairs]),'pairedComparison':pairs,'hpWorse':sum(p['hpWorse']for p in pairs),'hpBetter':sum(p['hpBetter']for p in pairs),'hpSame':sum(p['before']['hpAfter']==p['after']['hpAfter']for p in pairs),'metricFunctionSha256':hashlib.sha256(fn.encode()).hexdigest(),'metricSource':'Unchanged Phase1 collect_effects.metrics; real ASM references and pre3km evidence, never legacy counters','checks':{'exact120CaseControl':True,'sameFrozenProduct':True,'allCurrentTickReleases':True,'allNativeShotsRecorded':True,'allNativeSourceFingerprints':True,'noCoreOrPageErrors':True},'offReuseReason':'B2B changes only the active Mk45 fragmentation model and fixed fuze center. AutoAA OFF rows have no gun shots, bursts, or releases; all other game code and RNG are source-identical.'};(P/'evidence/g7-summary.json').write_text(json.dumps(q,indent=2)+'\n')
fields=[k for k in flat[0]if k not in ['releaseAges','creditEvidence']]
with(P/'evidence/g7-trials.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows({k:r[k]for k in fields}for r in flat)
# Historical CIWS anomalies: full original30, not the reduced15 or fresh evidence.
ciws=[]
for ship,bearing in[('CG_52_LATE_TICONDEROGA',0),('DDG_119_LATE_FLIGHT_IIA',90)]:
 rr=[r for r in original.values()if(r['ship'],r['bearing'],r['count'],r['on'])==(ship,bearing,1,False)];assert len(rr)==30;ciws.append({'ship':ship,'bearing':bearing,'n':30,'meanCiwsUsed':mean(r['result']['ciwsUsed']for r in rr),'hpDamageTrials':sum(r['result']['hpAfter']<r['result']['hpBefore']for r in rr),'hpZeroTrials':sum(r['result']['hpAfter']==0 for r in rr),'source':'HISTORICAL_PHASE1_AUTOAA_OFF_UNCHANGED_NOT_FIXED'})
(P/'evidence/ciws-reference-only.json').write_text(json.dumps(ciws,indent=2)+'\n')
print(json.dumps({'complete':True,'cases':120,'hpWorse':q['hpWorse'],'hpBetter':q['hpBetter'],'hpSame':q['hpSame']}))
