#!/usr/bin/env python3
"""Commit-C protected hash, source-scope and packed-product static gate."""
from __future__ import annotations
import base64,gzip,hashlib,json,re
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
BASELINE=json.loads((HERE/'BASELINE_AUDIT.json').read_text())
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def source(path:Path)->str:
 raw=path.read_bytes();m=re.search(rb'data-c55-index="13">([^<]+)',raw);return gzip.decompress(base64.b64decode(m[1])).decode()
def spans(text:str,name:str)->list[str]:
 out=[]
 for match in re.finditer(rf"function\s+{re.escape(name)}\s*\(",text):
  brace=text.find('{',match.end());depth=0;quote=None;escaped=False
  for index in range(brace,len(text)):
   char=text[index]
   if quote:
    if escaped:escaped=False
    elif char=='\\':escaped=True
    elif char==quote:quote=None
    continue
   if char in "'\"`":quote=char
   elif char=='{':depth+=1
   elif char=='}':
    depth-=1
    if depth==0:out.append(text[match.start():index+1]);break
 return out
def hashes(text:str,name:str)->list[str]:return [sha(q.encode()) for q in spans(text,name)]
def main()->None:
 base=source(ROOT/'Aegis_SIM_v48_WIP_EMITTER_A.html');candidate=source(ROOT/'Aegis_SIM_v48_WIP_EMCON_B.html')
 protected={};allowed_protected={'prepareElectronicF','electronicShipPhysicalEmittersDeclaredA'}
 for label,row in BASELINE['functionHashes'].items():
  name=label.split('.')[0];choices=spans(candidate,name)
  if label=='toggleEmcon.operator':choices=[q for q in choices if 'networkOverrideRadarG(ACTIVE_SHIP_RUNTIME)' in q]
  if len(choices)!=1:raise AssertionError(f'{label}:{len(choices)}')
  current=sha(choices[0].encode());protected[label]={'baseline':row['sha256'],'current':current,'changed':current!=row['sha256'],'allowed':name in allowed_protected}
 changed_expected=['electronicJammerSampleF','electronicShipPhysicalEmittersDeclaredA','friendlyIffPlotsF','heloMeasureIffRepliesE','observerSpyCycleC','observerAuxStepC','updateSpyScheduler','updateSpq9bRadar','updateBridgeMasterERadar','updateBridgeMasterEShorelineReturns','updateSlq32EaAllocator']
 named={name:{'baseline':hashes(base,name),'candidate':hashes(candidate,name)} for name in changed_expected}
 checks={
  'modeActive':"const EMCON_B_MODE='ACTIVE'" in candidate,
  'onlyAllowedProtectedChanged':all(not row['changed'] or row['allowed'] for row in protected.values()),
  'expectedProtectedChanged':all(any(label.split('.')[0]==name and row['changed'] for label,row in protected.items()) for name in allowed_protected),
  'allRuntimeConsumersChanged':all(row['baseline']!=row['candidate'] and len(row['baseline'])==len(row['candidate']) for row in named.values()),
  'twoAllocatorCopiesChanged':len(named['updateSlq32EaAllocator']['candidate'])==2,
  'policySingleCopy':candidate.count("const EMCON_B_SCHEMA='AEGIS_SHIP_EMCON_B_1'")==1,
  'legacyMasterOwnersPreserved':'function emconMasterSilentB(r){return r===ACTIVE_SHIP_RUNTIME?!!emconActive:!!r?.combatSystem?.observerC?.emcon;}' in candidate,
  'communicationsNotGated':'configureOffboardSourceC' in candidate and "emconCategoryAllowsB(r,'ECM')" in candidate,
  'productHasNoDiagnosticProbe':'__EMCON_B_C_DIAG__' not in candidate,
 }
 result={'schema':'AEGIS_EMCON_B_COMMIT_C_STATIC_1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'protectedFunctions':protected,'runtimeFunctions':named}
 (HERE/'C_STATIC.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':checks},indent=2));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
