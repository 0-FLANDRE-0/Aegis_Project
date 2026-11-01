from pathlib import Path
import json,hashlib,statistics,csv
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence';sha=lambda b:hashlib.sha256(b).hexdigest()
def rows(p):return [json.loads(l)for l in p.open()]
def scrub(v):
 if isinstance(v,dict):return{k:scrub(x)for k,x in v.items()if k not in ['elapsedMs','elapsedS','refreshMs','wallS','htmlSha256','ship','caseId']}
 if isinstance(v,list):return[scrub(x)for x in v]
 return v
def index(rr):return{(r['bearing'],r['rangeKm'],r['seed']):r for r in rr}
current=rows(E/'range-pk.jsonl');before=[]
for b in[0,90]:before+=rows(R/f'docs/gun/B2/phase1b/evidence/range-intercept/CG_52_LATE_TICONDEROGA-{b}.jsonl')
old=index(before);pk=[]
for b in[0,90]:
 for km in range(1,10):
  a=[r for r in current if r['bearing']==b and r['rangeKm']==km];o=[old[(b,km,r['seed'])]for r in a]
  meanReleased=lambda rr:statistics.mean(r['pk']for r in rr if r.get('release',{}).get('projectileId'))if any(r.get('release',{}).get('projectileId')for r in rr)else None
  pk.append({'bearing':b,'rangeKm':km,'n':len(a),'oldMeanPk':meanReleased(o),'newMeanPk':meanReleased(a),'meanPkDenominator':'ACTUAL_NATIVE_RELEASES_ONLY; NULL_IF_NONE','oldReleases':sum(bool(r.get('release',{}).get('projectileId'))for r in o),'newReleases':sum(bool(r.get('release',{}).get('projectileId'))for r in a),'oldKills':sum(r.get('outcome')in['KILL','STRUCT_FAIL']for r in o),'newKills':sum(r.get('outcome')in['KILL','STRUCT_FAIL']for r in a),'reasons':{k:sum(r.get('reason')==k for r in a)for k in sorted(set(str(r.get('reason'))for r in a))}})
surface=rows(E/'range-surface.jsonl');oldSurface=rows(R/'docs/gun/B2/phase1a/evidence/surface/CG_52_LATE_TICONDEROGA-ON.jsonl');surf=[]
for k in[5,10,15]:
 a=[r for r in surface if r['rangeKm']==k];o=[r for r in oldSurface if r['rangeKm']==k];surf.append({'rangeKm':k,'n':len(a),'oldHits':sum(r['result']['checks']['firstRoundHit']for r in o),'newHits':sum(r['result']['checks']['firstRoundHit']for r in a),'oldFixturePass':sum(r['result']['pass']for r in o),'newFixturePass':sum(r['result']['pass']for r in a)})
out={'pk':pk,'surface':surf,'attempts':len(current),'actualReleases':sum(bool(r.get('release',{}).get('projectileId'))for r in current)}
if(E/'render.json').exists():
 d=json.loads((E/'render.json').read_text());out['renderChecks']=d['checks'];out['maxMuzzleErrorM']=d['records']['current']['poses']['maxErrorM'];a=d['records']['B2B'];b=d['records']['current'];performance=[]
 for oldspec,newspec in zip(a['specs'],b['specs']):
  q=scrub(newspec);q['spec']['installation']=oldspec['spec']['installation'];q['spec']['mount']['trunnionOffsetM']=oldspec['spec']['mount']['trunnionOffsetM'];q['spec']['mount']['exposedBarrelM']=oldspec['spec']['mount']['exposedBarrelM'];performance.append({'id':newspec['id'],'exactOutsideInstallationOrigin':q==oldspec})
 out['performance']=performance;clear=[]
 for o,n in zip(a['clearance'],b['clearance']):
  changes=[{'before':x,'after':y}for x,y in zip(o['rows'],n['rows'])if (x['ok'],x['reason'],x['obstruction'])!=(y['ok'],y['reason'],y['obstruction'])];clear.append({'mount':n['id'],'samples':len(n['rows']),'changed':len(changes),'oldClear':sum(r['ok']for r in o['rows']),'newClear':sum(r['ok']for r in n['rows']),'changes':changes})
 out['clearance']=clear
if(E/'control-pk.jsonl').exists()and(E/'baseline-pk.jsonl').exists():
 control=rows(E/'control-pk.jsonl');base=index(rows(E/'baseline-pk.jsonl'));sbase={(r['rangeKm'],r['seed']):r for r in rows(E/'baseline-surface.jsonl')};pairs=[{'kind':'PK','key':list(k),'exact':scrub(v)==scrub(base[k])}for k,v in index(control).items()];pairs += [{'kind':'SURFACE','key':[r['rangeKm'],r['seed']],'exact':scrub(r)==scrub(sbase[(r['rangeKm'],r['seed'])])}for r in rows(E/'control-surface.jsonl')]
 historical=[]
 for k,v in base.items():
  a=scrub(old[k]);b=scrub(v);rawExact=a==b;oldId=a.get('release',{}).get('trackId');newId=b.get('release',{}).get('trackId')
  if 'release'in a and 'trackId'in a['release']:a['release']['trackId']=newId
  historical.append({'key':list(k),'rawExact':rawExact,'oldTrackId':oldId,'newTrackId':newId,'physicalExactAfterTrackIdAssociation':a==b})
 out['historicalBaselineRecheck']={'reason':'Reduced baseline sample creates fewer historical track IDs; only release.trackId differs, and all physical/output fields are checked exactly. Counterfactual31 comparisons require full equality without this association.','rows':historical,'allPhysicalExact':all(x['physicalExactAfterTrackIdAssociation']for x in historical)}
 if(E/'control-g7.jsonl').exists()and(E/'baseline-g7.jsonl').exists():
  bg={(r['bearing'],r['count'],r['seed']):r for r in rows(E/'baseline-g7.jsonl')};pairs += [{'kind':'G7','key':[r['bearing'],r['count'],r['seed']],'exact':scrub(r)==scrub(bg[(r['bearing'],r['count'],r['seed'])])}for r in rows(E/'control-g7.jsonl')]
 out['originIsolation']={'pairs':pairs,'allExact':all(r['exact']for r in pairs)}
if(E/'g7-execution.json').exists():
 rr=rows(E/'g7.jsonl');bb=rows(R/'docs/gun/B2/phase1b/evidence/g7/trials.jsonl');base={(r['bearing'],r['count'],r['seed']):r for r in bb if r['ship'].startswith('CG')};g7=[]
 for r in rr:
  o=base[(r['bearing'],r['count'],r['seed'])];g7.append({'bearing':r['bearing'],'count':r['count'],'seed':r['seed'],'oldHp':o['result']['hpAfter'],'newHp':r['result']['hpAfter'],'oldShots':o['result']['shots'],'newShots':r['result']['shots'],'oldCiws':o['result']['ciwsUsed'],'newCiws':r['result']['ciwsUsed'],'oldTargets':o['result']['targets'],'newTargets':r['result']['targets'],'oldShipAlive':o['result']['shipAlive'],'newShipAlive':r['result']['shipAlive']})
 out['g7']={'n':len(g7),'hpWorse':sum(r['newHp']<r['oldHp']-1e-9 for r in g7),'hpBetter':sum(r['newHp']>r['oldHp']+1e-9 for r in g7),'hpSame':sum(abs(r['newHp']-r['oldHp'])<1e-9 for r in g7),'rows':g7}
for name,rr in [('pk-comparison',out['pk']),('surface-comparison',out['surface']),('g7-comparison',out.get('g7',{}).get('rows',[]))]:
 if not rr:continue
 with(E/(name+'.csv')).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]),lineterminator='\n');w.writeheader();w.writerows({k:json.dumps(v,separators=(',',':'))if isinstance(v,(dict,list))else ('WITHHELD'if v is None else v)for k,v in r.items()}for r in rr)
(E/'summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['pk','clearance','g7']},indent=2))
