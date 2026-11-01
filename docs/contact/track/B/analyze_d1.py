"""Read-only AFTER_ACTION D1 comparison; never supplies inputs to the game.

The selected gameplay table is an aid, not an assertion replacement. Original
signatures, every native row and the frozen runner's full differences remain.
Timestamp-keyed event groups retain all fields and original per-group order.
"""
from pathlib import Path
import argparse,gzip,hashlib,json
from itertools import zip_longest

P=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()

def stream(path):
 with path.open()as source:
  for line in source:
   try:yield json.loads(line)
   except json.JSONDecodeError:return  # A live writer may not have flushed a row.

def gameplay(row):
 r=row['result'];events=row.get('events',[])
 return {k:r.get(k)for k in ['shipHits','hpBefore','hpAfter','shipAlive','targets','seconds','gunPreCiwsKills','preCiwsKills','shots','ciwsUsed','burstCount']}|{
  'gunRounds':sum(e.get('rounds',0)for e in events if e.get('kind')=='CIWS_FIRE'),
  'ramRounds':sum(e.get('rounds',0)for e in events if e.get('kind')=='RAM_AMMO')}

def keyed_events(events):
 groups={}
 for event in events:
  key=json.dumps([event.get('step'),event.get('kind'),event.get('mount')],separators=(',',':'))
  groups.setdefault(key,[]).append(event)
 return groups

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reference',type=Path,default=P/'evidence/runtime/baseline/friendly/ciws-d1.jsonl');parser.add_argument('--candidate',type=Path,default=P/'evidence/runtime/active/friendly/ciws-d1.jsonl');parser.add_argument('--out',type=Path,default=P/'evidence/runtime/active/d1-semantic');args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 rows=[];changed=[];indicators=[]
 for before,after in zip_longest(stream(args.reference),stream(args.candidate)):
  if before is None or after is None:break
  seed=after['case']['seed'];assert before['case']==after['case'];left,right=gameplay(before),gameplay(after);worse=[]
  if right['hpAfter']<left['hpAfter']:worse.append('LOWER_FINAL_HP')
  if right['shipHits']>left['shipHits']:worse.append('MORE_SHIP_IMPACTS')
  if left['shipAlive']and not right['shipAlive']:worse.append('NEW_SHIP_LOSS')
  if worse:indicators.append({'seed':seed,'indicators':worse})
  same=before['signatureSha256']==after['signatureSha256'];detail=None
  if not same:
   a,b=keyed_events(before.get('events',[])),keyed_events(after.get('events',[]));keys=set(a)|set(b)
   differences=[{'fixedTickKindMountKey':json.loads(key),'before':a.get(key,[]),'after':b.get(key,[])}for key in sorted(keys)if a.get(key,[])!=b.get(key,[])]
   payload={'classification':'AFTER_ACTION_EVENT_ALIGNMENT_NOT_GAME_INPUT','seed':seed,'alignmentKey':['step','kind','mount'],'allEventFieldsAndPerKeyOrderRetained':True,'groups':differences};raw=json.dumps(payload,separators=(',',':')).encode();file=args.out/f'{seed}-timestamp-keyed-events.json.gz';file.write_bytes(gzip.compress(raw,6,mtime=0));detail={'path':str(file),'rawSha256':sha(raw),'changedTimestampGroups':len(differences)};changed.append(seed)
  rows.append({'seed':seed,'sameOriginalSignature':same,'referenceSignature':before['signatureSha256'],'candidateSignature':after['signatureSha256'],'selectedGameplaySummaryEqual':left==right,'selectedGameplaySummaryIsNotPassCriterion':True,'referenceGameplay':left,'candidateGameplay':right,'rawResultPreservedReference':before['result'],'rawResultPreservedCandidate':after['result'],'outcomeWorseningIndicators':worse,'afterMountCueBefore':[m.get('cue')for m in before.get('after',{}).get('mounts',[])],'afterMountCueAfter':[m.get('cue')for m in after.get('after',{}).get('mounts',[])],'timestampKeyedEventDifferences':detail})
 result={'schema':'AEGIS_TRACK_B_D1_AFTER_ACTION_COMPARISON_1','status':'COMPLETE_OBSERVATION'if len(rows)==30 else'INCOMPLETE_OBSERVATION','classification':'AFTER_ACTION_TRUTH_ONLY_NOT_CONSUMED_BY_GAME','originalSignaturesNotRelaxed':True,'rawFieldsNotRemovedOrOverwritten':True,'originalFrozenComparisonPath':str(args.candidate.parents[1]/'d1-comparison.json'),'referencePath':str(args.reference),'candidatePath':str(args.candidate),'cases':len(rows),'sameOriginalSignatureCount':sum(r['sameOriginalSignature']for r in rows),'differentSignatureSeeds':changed,'outcomeWorseningIndicators':indicators,'automaticApproval':False,'releaseApproved':False,'rows':rows}
 (args.out/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','cases','sameOriginalSignatureCount','differentSignatureSeeds','outcomeWorseningIndicators','automaticApproval']},indent=2))

if __name__=='__main__':main()
