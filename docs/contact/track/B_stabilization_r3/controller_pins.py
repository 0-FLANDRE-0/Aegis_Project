"""Read-only source proof for unchanged R1 native fixtures/controllers."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;R=P.parents[3]
def verify():
 raw=(P/'NATIVE_TEST_INPUT_PINS.json').read_bytes();pins=json.loads(raw);rows=[]
 for name,expected in pins['files'].items():
  actual=hashlib.sha256((R/name).read_bytes()).hexdigest()
  if actual!=expected:raise ValueError('FROZEN_R1_NATIVE_TEST_INPUT_CHANGED:'+name)
  rows.append({'path':name,'sha256':actual,'expectedSha256':expected,'exact':True})
 return {'schema':pins['schema'],'pinsSha256':hashlib.sha256(raw).hexdigest(),'status':'PASS','rows':rows,'browserRuns':0,'R1SourceChanged':False}
