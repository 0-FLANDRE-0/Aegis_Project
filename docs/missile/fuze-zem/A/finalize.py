"""Gate the submitted DZT build on completed measured evidence."""
from pathlib import Path
import json,hashlib,datetime
from zoneinfo import ZoneInfo
H=Path(__file__).resolve().parent;R=H.parents[3];read=lambda n:json.loads((H/n).read_text());checks={}
for n in ['core','deterministic-unit','term-unit','static','equivalence','browser','clutter-preservation','deterministic-replay','domain-acceptance','release-comparison']:
 checks[n]=read('evidence/'+n+'.json')['pass']
checks['ui88']=read('evidence/ui/ui.json')['pass'];checks['wholeWorld120']=read('evidence/world120/world120.json')['pass']
for v in ['BASE','DZT']:checks['nativeWebgl.'+v]=read('evidence/observed-'+v+'/observed-world.json')['pass']
s=read('SUMMARY.json');checks['oldFRejected16Regressions']=len(s['F']['losses'])==16;checks['oldFGains20']=len(s['F']['gains'])==20
for v in ['D','Z','T','ZT','DZT']:checks[v+'.noNewFailure']=not s[v]['losses']
checks['D.restoresAll16']=not set(s['F']['losses'])&set(s['D']['losses']);checks['D.retainsAll20']=set(s['F']['gains'])<=set(s['D']['gains']);checks['natural.noNewFailure']=all(not s['natural'][v]['losses']for v in ['D','Z','T','ZT','DZT'])
html=(R/'Aegis_SIM_v48_WIP_FUZE_ZEM_A.html').read_bytes();build=next(x for x in read('build-variants.json')['records']if x['variant']=='DZT');checks['finalHtmlIsTestedDZT']=hashlib.sha256(html).hexdigest()==build['htmlSha256'];checks['archiveSevenUnchanged']=len(read('evidence/archive-proof.json'))==7 and all(x['byteIdentical']for x in read('evidence/archive-proof.json'))
checks['noFullEnvelopeRemeasurement']=read('evidence/tool-versions.json')['fullEnvelopeSweepRun']is False
out={'schema':'AEGIS_FUZE_ZEM_A_VERIFICATION_1','verificationPass':all(checks.values()),'checks':checks,'htmlSha256':hashlib.sha256(html).hexdigest(),'htmlBytes':len(html),'baseCommit':'058273c1f4b91c0d0c595e5399aaa967aa443f1c','branch':'fuze-zem-a','finalVariant':'DZT','supersededStochasticVariantFApproved':False,'successToFailure':len(s['DZT']['losses']),'failureToSuccess':len(s['DZT']['gains']),'fullEnvelopeSweep':False,'newRangeTable':False,'priorRangeData':'HISTORICAL_ENV_D_RECALC_REQUIRED','reviewedAtKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat()};(H/'evidence/verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['verificationPass'],'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if out['verificationPass']else 1)
