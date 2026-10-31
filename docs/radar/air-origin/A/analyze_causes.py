"""Attribute strict-state differences, requiring instrumentation equivalence first."""
from pathlib import Path
import gzip,hashlib,json
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(name):
 p=E/name
 return json.loads(p.read_text()if p.exists()else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes()))
def physical(v):
 if isinstance(v,dict):return {k:physical(x)for k,x in v.items()if k not in ['performance','aviation']}
 if isinstance(v,list):return list(map(physical,v))
 return v
def delta(a,b,p=''):
 if type(a)!=type(b):return [{'path':p,'before':a,'after':b}]
 if isinstance(a,dict):return [d for k in sorted(a.keys()|b.keys())for d in(delta(a[k],b[k],p+'.'+k)if k in a and k in b else[{'path':p+'.'+k,'before':a.get(k),'after':b.get(k)}])]
 if isinstance(a,list):
  if len(a)!=len(b):return [{'path':p+'.length','before':len(a),'after':len(b)}]
  return [d for i,(x,y)in enumerate(zip(a,b))for d in delta(x,y,p+f'[{i}]')]
 return []if a==b else[{'path':p,'before':a,'after':b}]
def firsts(a,b):
 out={}
 for key in ['tracks','massKg','cgM','heel','trim','draft','rng','target','missiles']:
  row=next(((i,x,y)for i,(x,y)in enumerate(zip(a,b))if x.get(key)!=y.get(key)),None)
  out[key]=None if row is None else {'tick':row[1]['tick'],'timeS':row[1]['tick']/60,'before':row[1].get(key),'after':row[2].get(key)}
 return out
original=read('regression/AIR_ORIGIN_A/paired42/baseline-comparison.json');raid=read('causes-raid.json');world=read('causes-world.json');summary=read('summary.json');records=[]
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 pair=[x for x in raid['rows']if x['ship']==ship];case=next(x for x in original['cases']if x['ship']==ship and x['scenario']=='raid')
 for r in pair:
  ref=case['pair']['baseline'if r['tag']=='MAIN'else'candidate']
  assert all(physical(r['result'][k])==physical(ref[k])for k in ['state','dynamics','rng']),'PASSIVE_RAID_LOGGER_CHANGED_PHYSICS'
 a,b=[r['result']['trace']['rows']for r in pair];first=firsts(a,b);assert first['tracks']['tick']<first['missiles']['tick']<first['massKg']['tick']==first['heel']['tick']
 old,new=case['pair']['baseline'],case['pair']['candidate'];assert old['afterActionTruth']==new['afterActionTruth']
 records.append({'mode':'raid','ship':ship,'passiveLoggerEquivalent':True,'firstDifferences':first,'launches':{r['tag']:r['result']['trace']['launches']for r in pair},'physicalDifferences':delta(physical({'state':old['state'],'dynamics':old['dynamics']}),physical({'state':new['state'],'dynamics':new['dynamics']})),'observerDifferences':delta(physical(old['observers']),physical(new['observers'])),'afterActionTruth':old['afterActionTruth'],'finalPoseBefore':old['dynamics']['pose'],'finalPoseAfter':new['dynamics']['pose'],'cause':'Receiver metadata changes EKF/association from tick 3; existing AUTO release timings differ; the unchanged mass ledger removes the same 708 kg SM2 rounds on different ticks; transient mass/CG changes drive small attitude phase differences. Final inventory, HP/damage and RNG are unchanged at the fixed 32 s endpoint. No claim about an entire raid beyond that endpoint.'})
pair=world['rows'];ref=next(r for r in summary['world']if r['mode']=='combat')
for r in pair:assert r['result']['stateSha256']==ref['beforeHash'if r['tag']=='MAIN'else'afterHash'],'PASSIVE_WORLD_LOGGER_CHANGED_PHYSICS'
first=firsts(*[r['result']['trace']['rows']for r in pair]);assert first['tracks']['tick']<first['missiles']['tick']<first['target']['tick']==first['rng']['tick'];assert all(first[k]is None for k in ['massKg','cgM','heel','trim','draft'])
records.append({'mode':'world120-combat','ship':'DDG_119_LATE_FLIGHT_IIA','passiveLoggerEquivalent':True,'firstDifferences':first,'cause':'Corrected observations differ at tick 56. Same release tick 900 and same initial missile position. At tick 4032 the original missile is ACTIVE with essmActiveSeeker=true while the candidate is IOG/false. At tick 4034 the original target enters threatened=true while the candidate does not; updateTarget uses existing active-RF/beam/LOS threat evidence to enter evasion and consume RNG. The final hash differs in target motion (7 fields) and global RNG only; ship physics/inventory/damage are identical. Not an RF Pd/noise or global RNG algorithm change.'})
archives=[]
for name in ['causes-raid.json','causes-world.json']:
 p=E/name
 if p.exists():
  raw=p.read_bytes();z=gzip.compress(raw,9,mtime=0);dest=p.with_suffix(p.suffix+'.gz');dest.write_bytes(z);assert gzip.decompress(dest.read_bytes())==raw;p.unlink()
 else:raw=gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes())
 archives.append({'path':name+'.gz','rawSha256':hashlib.sha256(raw).hexdigest(),'rawBytes':len(raw)})
out={'pass':True,'expectedValuesUpdated':False,'passiveLoggerEquivalent':True,'records':records,'archives':archives,'extraElapsedS':raid['elapsedS']+world['elapsedS'],'audit':'Retained truth fields are AFTER_ACTION_TRUTH diagnostic-only. Passive wrappers are not shipped. Original regression output and all failed assertions remain untouched.'}
(E/'cause-analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':True,'cases':len(records),'allPassiveLoggersEquivalent':True}))
