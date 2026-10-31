"""Reusable exact hash guard; no tolerant comparison and no implicit approvals."""
from pathlib import Path
import base64,copy,gzip,hashlib,json,re
B=Path(__file__).resolve().parent;R=B.parents[2]
sha=lambda x:hashlib.sha256(x).hexdigest()
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def validate(raw,ref):
 assert sha(raw)==ref['htmlSha256'],'UNREVIEWED_HTML'
 main=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1]));assert sha(re.sub(rb'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',b'',main))==ref['gameCoreWithoutEnvelopeSha256'],'UNREVIEWED_CORE'
 for e in ref['entries']:
  assert sha(canonical(e['old']))==e['oldHash']and sha(canonical(e['expected']))==e['newHash'],'ALTERED_APPROVED_VALUE'
 for e in ref['ewEntries']:assert sha(canonical(e['expected']))==e['newHash'],'ALTERED_EW_VALUE'
 return True
if __name__=='__main__':
 raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();ref=json.loads((B/'approved-gun-baselines.json').read_text());checks={'reviewedCoreAccepted':validate(raw,ref)}
 cases=[('wrongHtmlRejected',raw+b'changed',ref),('wrongCoreRejected',raw,{**ref,'gameCoreWithoutEnvelopeSha256':'0'*64})]
 bad=copy.deepcopy(ref);bad['entries'][0]['expected']['state']['shipHP']-=1;cases.append(('oneHpChangeRejected',raw,bad))
 bad=copy.deepcopy(ref);bad['ewEntries'][0]['expected']['base']['shipHP']=99;cases.append(('extraEwChangeRejected',raw,bad))
 for name,data,r in cases:
  try:validate(data,r);checks[name]=False
  except AssertionError:checks[name]=True
 result={'pass':all(checks.values()),'checks':checks,'htmlSha256':sha(raw),'referenceSha256':sha((B/'approved-gun-baselines.json').read_bytes())};(B/'evidence/reference-guard-tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(not result['pass'])
