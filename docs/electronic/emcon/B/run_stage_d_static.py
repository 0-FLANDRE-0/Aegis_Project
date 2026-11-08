#!/usr/bin/env python3
"""Commit-D protected hash and profile-derived UI static gate."""
from __future__ import annotations
import base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];BASELINE=json.loads((HERE/'BASELINE_AUDIT.json').read_text())
def sha(v:bytes)->str:return hashlib.sha256(v).hexdigest()
def src(path:Path)->str:
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
 text=src(ROOT/'Aegis_SIM_v48_WIP_EMCON_B.html');protected={};allowed={'prepareElectronicF','electronicShipPhysicalEmittersDeclaredA','exportOperationalState','prepareOperationalStateV48Wip11B','resetElectronicFleetF'}
 for label,row in BASELINE['functionHashes'].items():
  name=label.split('.')[0];choices=span(text,name,'networkOverrideRadarG(ACTIVE_SHIP_RUNTIME)' if label=='toggleEmcon.operator' else None)
  if len(choices)!=1:raise AssertionError(f'{label}:{len(choices)}')
  current=sha(choices[0].encode());protected[label]={'baseline':row['sha256'],'current':current,'changed':current!=row['sha256'],'allowed':name in allowed}
 module=(HERE/'emcon_ui.js').read_text();policy=(HERE/'emcon_policy.js').read_text();checks={
  'modeActive':"const EMCON_B_MODE='ACTIVE'" in text,
  'onlyAllowedProtectedChanged':all(not q['changed'] or q['allowed'] for q in protected.values()),
  'schemaV2Once':text.count("const EMCON_B_SCHEMA='AEGIS_SHIP_EMCON_B_2'")==1,
  'globalAuthorityPerRuntime':'allRadiationSilent:false' in policy and 'EMCON_B_ALL_RADIATION_MEMORY' not in text,
  'existingMenuSingle':text.count("menu.id='mapEmconMenuE'")==1 and text.count("emconChip.id='uiEmconChipA'")==1,
  'registryDriven':all(token in module for token in ['SHIP_EMITTER_CATEGORIES_A','shipEmitterRegistryA(r)','registry?.entries']),
  'noShipIdsInUiModule':all(token not in module for token in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA','AN_SPY_1DV','AN_SPY_1A_MODERNIZED']),
  'singleGlobalControl':text.count("dom.all=button('전파방사통제 OFF','mapAllRadiationE'")==1 and 'mapRadarE' not in text,
  'globalAriaAuthoritative':"String(q.allRadiationSilent)" in text and "String(allSilent)" in text,
  'communicationSeparationShown':'통신 링크는 별도' in module,
  'fireControlEmptyPath':'등록 장비 없음' in module,
  'productHasNoStageDiagnostic':'__EMCON_B_C_DIAG__' not in text,
 }
 result={'schema':'AEGIS_EMCON_B_COMMIT_D_STATIC_1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'protectedFunctions':protected};(HERE/'D_STATIC.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':checks},indent=2));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
