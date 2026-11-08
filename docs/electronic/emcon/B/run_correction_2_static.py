#!/usr/bin/env python3
"""Static fail-closed checks for PR74 correction 2."""
from __future__ import annotations
import base64,gzip,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def unpack()->str:
 raw=(ROOT/'Aegis_SIM_v48_WIP_EMCON_B.html').read_bytes();m=re.search(rb'data-c55-index="13">([^<]+)',raw);assert m;return gzip.decompress(base64.b64decode(m[1])).decode()
def body(text:str,name:str)->str:
 m=re.search(rf'function\s+{re.escape(name)}\s*\(',text);assert m,name;b=text.find('{',m.end());depth=0;quote=None;escaped=False
 for i in range(b,len(text)):
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
   if depth==0:return text[m.start():i+1]
 raise AssertionError(name)
def main():
 text=unpack();policy=(HERE/'emcon_policy.js').read_text();ui=(HERE/'emcon_ui.js').read_text();life=(HERE/'emcon_lifecycle.js').read_text();decision=body(text,'emconEquipmentDecisionB')
 order=[decision.index(x) for x in ["if(!entry)return",'if(operational.ok)',"if(allRadiationSilent)","else if(masterSilent)","else if(networkSilent)","else if(override==='FORCE_SILENT')","else if(override==='FORCE_RADIATE')","else if(categoryPolicy==='SILENT')"]]
 checks={
  'schemaV2Single':text.count("const EMCON_B_SCHEMA='AEGIS_SHIP_EMCON_B_2'")==1,
  'v1MigrationExplicit':all(x in life for x in ['EMCON_B_V1_TO_V2','migrateEmconStateV1B','ALL_RADIATION_SILENT_FALSE']),
  'explicitRuntimeAuthority':all(x in policy for x in ['allRadiationSilent:false','allRadiationRestoreMasterSilent:null','ALL_RADIATION_SILENT']),
  'priorityExact':order==sorted(order),
  'forceCannotBypassHardStops':decision.index("if(allRadiationSilent)")<decision.index("override==='FORCE_RADIATE'") and decision.index('if(operational.ok)')<decision.index("override==='FORCE_RADIATE'"),
  'exactNeutralConsumerContract':all(x in text for x in ["emconConsumerAllowsB(ACTIVE_SHIP_RUNTIME,'AIR_SEARCH_VOLUME')","emconConsumerAllowsB(ACTIVE_SHIP_RUNTIME,'SURFACE_SEARCH_SCAN')","emconConsumerAllowsB(ACTIVE_SHIP_RUNTIME,'NAVIGATION_SCAN')","emconConsumerAllowsB(r,'AIR_SEARCH_VOLUME')","emconConsumerAllowsB(r,spq?'SURFACE_SEARCH_SCAN':'NAVIGATION_SCAN')"]) and 'emconReceiver' not in text,
  'ecmPhysicalGates':text.count('emconEcmAllowsB(')>=4 and 'if(!emconEcmAllowsB(r))return null;' in text,
  'uiRegistryGenerated':all(x in ui for x in ['SHIP_EMITTER_CATEGORIES_A','shipEmitterRegistryA(r)','registry?.entries']),
  'uiNoShipOrEquipmentIds':all(x not in ui for x in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA','AN_SPY_1DV','AN_SPY_1A_MODERNIZED','AN_SLQ_32']),
  'uiNoAuthorityMap':'EMCON_B_ALL_RADIATION_MEMORY' not in ui and 'allRadiationSilent:new Map' not in ui,
  'singleTopControl':text.count("dom.all=button('전파방사통제 OFF','mapAllRadiationE'")==1 and 'mapRadarE' not in text,
  'topAriaUsesAuthority':"chip.setAttribute('aria-pressed',String(q.allRadiationSilent))" in text and "dom.all.setAttribute('aria-pressed',String(allSilent))" in text,
  'communicationsUngated':all(x not in policy+life for x in ['Hawklink','Link 16']),
  'strictGlobalValidation':all(x in policy for x in ['ALL_RADIATION_TYPE','ALL_RADIATION_RESTORE','ALL_RADIATION_RESTORE_STALE']),
  'diagnosticAbsent':all(x not in text for x in ['__EMCON_B_CORRECTION_2__','__EMCON_B_E_DIAG__','__EMCON_B_LOCK_DEBT__']),
 }
 result={'schema':'AEGIS_EMCON_B_PR74_CORRECTION_2_STATIC_1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'CORRECTION_2_STATIC.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
