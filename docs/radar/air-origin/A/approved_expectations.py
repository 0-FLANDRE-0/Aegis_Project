"""Exactly five user-approved expectations, bound to the reviewed product.

This module changes test expectations only. It is never bundled in game HTML.
Existing exact comparisons are retained; no tolerances or game state writes.
"""
from pathlib import Path
import base64,gzip,hashlib,json,re

SCHEMA='AEGIS_AIR_ORIGIN_A_APPROVED_EXPECTATIONS_1'
SHIPS=('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA')
PAIR_CHECKS=('samePhysicalState','sameExistingObserverState')
IDS={f'{ship}:raid:{check}'for ship in SHIPS for check in PAIR_CHECKS}|{'world120:combat:truthSha256'}
sha=lambda b:hashlib.sha256(b).hexdigest()
value_hash=lambda v:sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())

def physical(v):
 if isinstance(v,dict):
  d={k:physical(x)for k,x in v.items()if k not in ['performance','aviation']}
  if v.get('schema')=='AEGIS_OFFBOARD_PORT_C_1':
   d.pop('helicopterImplemented',None);d['sources']=[s for s in d.get('sources',[])if s.get('sourceId')not in ['H1','H2']]
  if v.get('schema')=='AEGIS_SHIP_OBSERVER_C_1'and'deferred'in d:d['deferred']=[s for s in d['deferred']if s!='helicopterFlightAndSensors']
  return d
 if isinstance(v,list):return [physical(x)for x in v]
 return v

def pair_value(row,check,normalizer=physical):
 if check=='samePhysicalState':return normalizer({k:row[k]for k in ['state','dynamics']})
 if check=='sameExistingObserverState':return normalizer(row['observers'])
 raise AssertionError('EXPECTATION_NOT_APPROVED:'+check)

def load_approval(path,raw):
 q=json.loads(Path(path).read_text());assert q['schema']==SCHEMA
 entries=q['entries'];assert len(entries)==5 and {r['id']for r in entries}==IDS,'EXACTLY_FIVE_APPROVED_EXPECTATIONS_REQUIRED'
 assert sha(raw)==q['reviewedHtmlSha256'],'APPROVAL_REQUIRES_REVIEWED_HTML'
 main=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1]))
 assert sha(main)==q['reviewedMainSha256'],'APPROVAL_REQUIRES_REVIEWED_GAME_CORE'
 for r in entries:
  assert value_hash(r['oldExpected'])==r['oldValueSha256'] and value_hash(r['newExpected'])==r['newValueSha256'],'APPROVAL_VALUE_HASH_MISMATCH'
  assert r['oldExpected']!=r['newExpected']and r['causePath']and r['reason'],'APPROVAL_MUST_RECORD_CHANGE_AND_CAUSE'
 assert q['otherExpectationsChanged']==0 and q['tolerancesChanged']==0
 return q

def apply_pair(q,ship,scenario,pair,checks,observations,normalizer):
 if scenario!='raid':return
 entries=[r for r in q['entries']if r.get('ship')==ship and r.get('scenario')==scenario]
 assert {r['check']for r in entries}==set(PAIR_CHECKS),'ONLY_TWO_RAID_CHECKS_APPROVED'
 original=dict(checks);changes=[]
 for r in entries:
  assert pair_value(pair['baseline'],r['check'],normalizer)==r['oldExpected'],'APPROVED_BASELINE_INPUT_CHANGED'
  actual=pair_value(pair['candidate'],r['check'],normalizer)
  checks[r['check']]=actual==r['newExpected']
  changes.append({'id':r['id'],'oldValueSha256':r['oldValueSha256'],'newValueSha256':r['newValueSha256'],'actualValueSha256':value_hash(actual),'reason':r['reason']})
 assert all(checks[k]==v for k,v in original.items()if k not in PAIR_CHECKS),'UNAPPROVED_CHECK_CHANGED'
 observations['airOriginApproval']={'originalChecks':original,'applied':changes,'tolerance':'EXACT_EQUALITY'}

def world_expectations(q,old):
 r=next(r for r in q['entries']if r['id']=='world120:combat:truthSha256')
 assert old['combat']==r['oldExpected'],'APPROVED_OLD_WORLD_HASH_CHANGED'
 new=dict(old);new['combat']=r['newExpected']
 assert {k for k in new if new[k]!=old[k]}=={'combat'},'ONLY_COMBAT_WORLD_HASH_APPROVED'
 return new
