#!/usr/bin/env python3
"""Fail-closed static gate for the manifest-selected EMCON_B candidate."""
from __future__ import annotations
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
EXPECTED_PRODUCT='e08cc2aede89e6452786efbf97fbd8ef49480ab33f8f8da178cbee0bff87377f'
EXPECTED_BASE='3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be'
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def strict(path:Path):return json.loads(path.read_text(),parse_constant=lambda x:(_ for _ in()).throw(ValueError(x)))
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--main-out',type=Path,required=True);a=p.parse_args()
 manifest=strict(ROOT/'AEGIS_CURRENT_PRODUCT.json');product=ROOT/manifest['path'];baseline=ROOT/manifest['baselinePath'];raw=product.read_bytes();m=re.search(rb'data-c55-index="13">([^<]+)',raw);assert m
 source=gzip.decompress(base64.b64decode(m[1])).decode();a.main_out.parent.mkdir(parents=True,exist_ok=True);a.main_out.write_text(source)
 build=strict(HERE/'BUILD_E.json');json_fail=[]
 for path in sorted(HERE.glob('*.json')):
  try:strict(path)
  except Exception as e:json_fail.append({'path':path.name,'error':str(e)})
 checks={
  'manifestStage':manifest['stage']=='EMCON_B' and manifest['branch']=='emcon-b' and manifest['release'] is False,
  'manifestProduct':manifest['path']==product.name and manifest['bytes']==len(raw) and manifest['sha256']==sha(raw)==EXPECTED_PRODUCT,
  'manifestBaseline':manifest['baselinePath']==baseline.name and manifest['baselineSha256']==sha(baseline.read_bytes())==EXPECTED_BASE,
  'buildReceipt':build['stage']=='E' and build['outputSha256']==sha(raw) and build['baseSha256']==EXPECTED_BASE,
  'activePolicy':"const EMCON_B_MODE='ACTIVE'" in source,
  'schemaSingle':source.count("const EMCON_B_SCHEMA='AEGIS_SHIP_EMCON_B_2'")==1,
  'categoryContract':all(x in source for x in ['AIR_SEARCH','SURFACE_SEARCH','NAV','FIRE_CONTROL','ECM']),
  'saveContract':source.count('emconB:emconExportStateB(')==2 and 'migrateEmconSaveB(src,harpoonMigrations)' in source,
  'communicationsSeparate':'Hawklink' not in (HERE/'emcon_lifecycle.js').read_text() and 'Link 16' not in (HERE/'emcon_lifecycle.js').read_text(),
  'releaseUninstrumented':'__EMCON_B_E_DIAG__' not in source and '__EMCON_B_LOCK_DEBT__' not in source,
  'strictJson':not json_fail,
 }
 out={'schema':'AEGIS_EMCON_B_CANDIDATE_STATIC_1','status':'PASS' if all(checks.values()) else'FAIL','checks':checks,'mainSha256':sha(source.encode()),'strictJsonFailures':json_fail,'manifest':manifest};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));raise SystemExit(0 if out['status']=='PASS' else 1)
if __name__=='__main__':main()
