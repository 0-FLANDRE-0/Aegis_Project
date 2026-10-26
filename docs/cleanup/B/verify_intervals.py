"""Independent Python reconstruction from audited point counts, not JS run grouping."""
from pathlib import Path
from itertools import groupby
import json
H=Path(__file__).resolve().parent;A=H.parent/'A';m=json.loads((H/'results/measurement.json').read_text());table=json.loads((H/'ENVELOPE_TABLE_D.json').read_text());old=json.loads((A/'ENVELOPE_TABLE_D.json').read_text());oldby={r['cellId']:r for r in old['rows']};by={r['cellId']:r for r in table['rows']};checks={};changed=[]
assert json.loads((H/'evidence/shot-audit.json').read_text())['pass']
def groups(points):return[(passed,list(it))for passed,it in groupby(points,key=lambda q:q['lethalCount']>=3)]
for r in m['rows']:
 points=r['gridChecks'];index={q['rangeKm']:q for q in points};base=list(range(1,min(30,int(r['maxRangeKm']))+1))+list(range(35,int(r['maxRangeKm'])+1,5));assert set(base).issubset(index)
 coarse=groups([index[x]for x in base]);last=[g for p,g in coarse if p][-1];start=last[0]['rangeKm'];refine=list(range(base[base.index(start)-1]+1,start))if start>30 else[]
 checks[r['cellId']+'.exactRequiredGrid']=set(index)==set(base)|set(refine)and r['refinedDistancesKm']==refine
 gs=groups(points);passes=[g for p,g in gs if p];selected=passes[-1]
 bounds=lambda g:(g[0]['rangeKm'],g[-1]['rangeKm'])
 checks[r['cellId']+'.farthestRun']=bounds(selected)==(r['effectiveMinKm'],r['effectiveMaxKm'])
 checks[r['cellId']+'.otherRuns']=[bounds(g)for g in passes[:-1]]==[(g['startKm'],g['endKm'])for g in r['otherRuns']]
 dead=[g for p,g in gs if not p and any(v[-1]['rangeKm']<g[0]['rangeKm']for v in passes)and any(v[0]['rangeKm']>g[-1]['rangeKm']for v in passes)]
 checks[r['cellId']+'.deadZones']=[bounds(g)for g in dead]==[(g['startKm'],g['endKm'])for g in r['deadZones']]and all(g['representativeFailureReason']for g in r['deadZones'])
 t=by[r['cellId']];p=oldby[r['cellId']]
 checks[r['cellId']+'.previousExact']=t['previous']==p
 checks[r['cellId']+'.outerUnchanged']=t['maxRangeKm']==p['maxRangeKm']and t['outerBoundary']==p['outerBoundary']and t['maxInterceptPoint']==p['maxInterceptPoint']
 checks[r['cellId']+'.oldPassAnchorsRetained']=t['effectiveMinKm']>=p['effectiveMinKm']and t['effectiveMaxKm']>=p['effectiveMaxKm']
 checks[r['cellId']+'.minMaxPresent']=isinstance(t['effectiveMinKm'],(int,float))and isinstance(t['effectiveMaxKm'],(int,float))and t['effectiveMinKm']<=t['effectiveMaxKm']and t['effectiveMinInterceptPoint']is not None and t['effectiveMaxInterceptPoint']is not None
 if(p['effectiveMinKm'],p['effectiveMaxKm'])!=(t['effectiveMinKm'],t['effectiveMaxKm']):changed.append({'cellId':r['cellId'],'weapon':r['weapon'],'altM':r['altM'],'motion':r['motion'],'before':[p['effectiveMinKm'],p['effectiveMaxKm']],'after':[t['effectiveMinKm'],t['effectiveMaxKm']],'otherRuns':r['otherRuns'],'deadZones':r['deadZones']})
checks['rows120']=len(m['rows'])==len(table['rows'])==120;checks['schema3']=table['schema']=='AEGIS_ENVELOPE_TABLE_D_3';out={'pass':all(checks.values()),'checks':checks,'changed':changed,'changedCells':len(changed),'unchangedCells':120-len(changed),'independentAlgorithm':'Python itertools.groupby on ordered audited counts; refinement gap explicitly reconstructed','unmeasured':0};(H/'evidence/interval-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['checks','changed']}));assert out['pass']
