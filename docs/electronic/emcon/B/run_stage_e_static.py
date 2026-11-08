#!/usr/bin/env python3
"""Commit-E static scope, schema, and protected-hash gate."""
from __future__ import annotations
import base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];BASE=json.loads((HERE/'BASELINE_AUDIT.json').read_text())
def sha(v:bytes)->str:return hashlib.sha256(v).hexdigest()
def unpack(path:Path)->str:
 raw=path.read_bytes();m=re.search(rb'data-c55-index="13">([^<]+)',raw);return gzip.decompress(base64.b64decode(m[1])).decode()
def span(text:str,name:str,contains:str|None=None)->list[str]:
 out=[]
 for match in re.finditer(rf'function\s+{re.escape(name)}\s*\(',text):
  brace=text.find('{',match.end());depth=0;quote=None;escaped=False
  for i in range(brace,len(text)):
   c=text[i]
   if quote:
    if escaped:escaped=False
    elif c=='\\':escaped=True
    elif c==quote:quote=None
    continue
   if c in "'\"`":quote=c
   elif c=='{':depth+=1
   elif c=='}':
    depth-=1
    if depth==0:
     body=text[match.start():i+1]
     if contains is None or contains in body:out.append(body)
     break
 return out
def main():
 text=unpack(ROOT/'Aegis_SIM_v48_WIP_EMCON_B.html');allowed={'prepareElectronicF','electronicShipPhysicalEmittersDeclaredA','exportOperationalState','prepareOperationalStateV48Wip11B','applyPreparedOperationalStateV48Wip11B','resetElectronicFleetF'};protected={}
 for label,row in BASE['functionHashes'].items():
  name=label.split('.')[0];choices=span(text,name,'networkOverrideRadarG(ACTIVE_SHIP_RUNTIME)' if label=='toggleEmcon.operator' else None)
  if len(choices)!=1:raise AssertionError(f'{label}:{len(choices)}')
  current=sha(choices[0].encode());protected[label]={'baseline':row['sha256'],'current':current,'changed':current!=row['sha256'],'allowed':name in allowed}
 checks={'modeActive':"const EMCON_B_MODE='ACTIVE'" in text,'onlyAllowedProtectedChanged':all(not q['changed'] or q['allowed'] for q in protected.values()),'schemaOnce':text.count("const EMCON_B_SCHEMA='AEGIS_SHIP_EMCON_B_1'")==1,'saveExports':text.count('emconB:emconExportStateB(')==2,'migrationBeforeCodecs':text.index('migrateEmconSaveB(src,harpoonMigrations)')<text.index('for(const codec of OPERATIONAL_STATE_CODECS_V48_WIP11B)'),'strictPreflight':text.count('validateEmconSaveB(')>=3,'networkFunctionsUnchanged':all(not protected[k]['changed'] for k in ['networkSetRadarG','networkGroupStepG','networkExportElectronicG','networkCommandG']),'tacticalFunctionsUnchanged':all(token not in (HERE/'emcon_lifecycle.js').read_text() for token in ['function tacticalEvaluateH1','function tacticalCommandH1']),'communicationsNotGated':'Hawklink' not in (HERE/'emcon_lifecycle.js').read_text() and 'Link 16' not in (HERE/'emcon_lifecycle.js').read_text(),'fireControlNoPhysicalImplementation':"category==='FIRE_CONTROL'" not in (HERE/'emcon_active_runtime.js').read_text(),'diagnosticAbsent':'__EMCON_B_E_DIAG__' not in text}
 result={'schema':'AEGIS_EMCON_B_COMMIT_E_STATIC_1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'protectedFunctions':protected};(HERE/'E_STATIC.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':checks},indent=2));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
