#!/usr/bin/env python3
"""Static ship-class-neutral binding checks for PR74 correction 3."""
from __future__ import annotations
import base64,gzip,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def unpack()->str:
 raw=(ROOT/'Aegis_SIM_v48_WIP_EMCON_B.html').read_bytes();m=re.search(rb'data-c55-index="13">([^<]+)',raw);assert m;return gzip.decompress(base64.b64decode(m[1])).decode()
def main():
 text=unpack();policy=(HERE/'emcon_policy.js').read_text();ui=(HERE/'emcon_ui.js').read_text();bindings=(HERE/'emcon_consumer_bindings.js').read_text();builder=(HERE/'build_product.py').read_text()
 forbidden=[]
 for m in re.finditer(r'emconConsumer(?:Allows|Decision|Resolve)\w*\([^\n;]*',text):
  call=m.group(0)
  if any(q in call for q in ("'SPY'","'SPQ'","'NAV'",'"SPY"','"SPQ"','"NAV"')):forbidden.append(call)
 checks={
  'schemaV2Unchanged':text.count("const EMCON_B_SCHEMA='AEGIS_SHIP_EMCON_B_2'")==1 and 'AEGIS_SHIP_EMCON_B_3' not in text,
  'neutralConsumerIds':all(q in bindings for q in ['AIR_SEARCH_VOLUME','SURFACE_SEARCH_SCAN','NAVIGATION_SCAN']),
  'ddgBindingsExact':all(q in bindings for q in ["equipmentId:'AN_SPY_1DV'","equipmentId:'AN_SPQ_9B'","equipmentId:'BRIDGEMASTER_E'"]),
  'cgBindingsExact':all(q in bindings for q in ["equipmentId:'AN_SPY_1A_MODERNIZED'","equipmentId:'AN_SPQ_9'","equipmentId:'AN_SPS_73'"]),
  'profileRegistryOwnsBindings':text.count('consumerBindings:emconConsumerBindingsForProfileB(')==2,
  'legacyReceiverApiRemoved':'emconReceiver' not in text and 'emconReceiver' not in policy,
  'legacyConsumerKeysRemoved':not forbidden,
  'neutralArrayMount':'FIRST_HEALTHY_SPY_FACE' not in text and "mountKind:'FIRST_HEALTHY_ARRAY_FACE'" in text,
  'failClosedReasons':all(q in policy for q in ['CONSUMER_BINDING_MISSING','CONSUMER_BINDING_AMBIGUOUS','CONSUMER_EQUIPMENT_MISSING','CONSUMER_EQUIPMENT_AMBIGUOUS','CONSUMER_CATEGORY_MISMATCH']),
  'noCategoryFallback':'emconCategoryAllowsB(r,spec.category)' not in policy and 'emconCategoryAllowsB(r,category)' not in policy[policy.find('function emconResolveConsumerBindingB'):policy.find('function emconEcmAllowsB')],
  'stateValidationIncludesBindings':'emconConsumerBindingsValidateB(r)' in policy and "errors.push(...bindingValidation.errors.map(q=>'CONSUMER_BINDING:'+q))" in policy,
  'uiProfileGenerated':all(q in ui for q in ['SHIP_EMITTER_CATEGORIES_A','shipEmitterRegistryA(r)','registry?.entries']),
  'uiNoSpecificEquipmentOrConsumerIds':all(q not in ui for q in ['AN_SPY_1DV','AN_SPY_1A_MODERNIZED','AN_SPQ_9B','AN_SPQ_9','AN_SPS_73','BRIDGEMASTER_E','AIR_SEARCH_VOLUME','SURFACE_SEARCH_SCAN','NAVIGATION_SCAN']),
  'sensorGatesNeutral':all(q in text for q in ["emconConsumerAllowsB(ACTIVE_SHIP_RUNTIME,'AIR_SEARCH_VOLUME')","emconConsumerAllowsB(ACTIVE_SHIP_RUNTIME,'SURFACE_SEARCH_SCAN')","emconConsumerAllowsB(ACTIVE_SHIP_RUNTIME,'NAVIGATION_SCAN')","emconConsumerAllowsB(r,spq?'SURFACE_SEARCH_SCAN':'NAVIGATION_SCAN')"]),
  'iffGatesNeutral':text.count("emconConsumerAllowsB(r,'AIR_SEARCH_VOLUME')")>=2 and "emconConsumerAllowsB(ship,'AIR_SEARCH_VOLUME')" in text,
  'buildOwnsBindingModule':'emcon_consumer_bindings.js' in builder,
  'diagnosticAbsent':all(q not in text for q in ['__EMCON_B_CORRECTION_3__','emconCorr3VirtualB'])
 }
 result={'schema':'AEGIS_EMCON_B_PR74_CORRECTION_3_STATIC_1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'forbiddenConsumerCalls':forbidden}
 (HERE/'CORRECTION_3_STATIC.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
