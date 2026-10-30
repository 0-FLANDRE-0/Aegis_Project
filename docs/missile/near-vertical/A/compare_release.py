from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[3];pairs=['normal','dual','fault','battery','request'];records=[]
for kind in pairs:
 before=json.loads((R/'docs/missile/arh-measurement/FIX_A/release'/f'{kind}.json').read_text())['results'];after=json.loads((H/'release'/f'{kind}.json').read_text())['results'];assert len(before)==len(after)
 changes=[];stf=[];fts=[]
 for i,(b,a)in enumerate(zip(before,after)):
  if b.get('success')and not a.get('success'):stf.append(i)
  if not b.get('success')and a.get('success'):fts.append(i)
  if b.get('success')!=a.get('success')or b.get('reason')!=a.get('reason'):changes.append({'index':i,'condition':{k:a.get(k)for k in('weapon','rangeKm','altM','targetSpeedMps','seed','enabled')},'before':{k:b.get(k)for k in('success','reason','closestM','fuzeMissM')},'after':{k:a.get(k)for k in('success','reason','closestM','fuzeMissM')}})
 records.append({'kind':kind,'shots':len(after),'successToFailure':stf,'failureToSuccess':fts,'statusChanges':changes,'errors':json.loads((H/'release'/f'{kind}.json').read_text()).get('errors',[])})
out={'schema':'AEGIS_NEAR_VERTICAL_PATH_FIX_A_RELEASE_300_1','shots':sum(x['shots']for x in records),'successToFailure':[{'kind':x['kind'],'index':i}for x in records for i in x['successToFailure']],'failureToSuccess':[{'kind':x['kind'],'index':i}for x in records for i in x['failureToSuccess']],'browserErrors':sum(len(x['errors'])for x in records),'records':records};out['pass']=not out['successToFailure']and out['browserErrors']==0;(H/'release-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'shots':out['shots'],'successToFailure':out['successToFailure'],'failureToSuccess':out['failureToSuccess'],'browserErrors':out['browserErrors'],'statusChanges':sum(len(x['statusChanges'])for x in records)},indent=2));raise SystemExit(0 if out['pass']else 1)
