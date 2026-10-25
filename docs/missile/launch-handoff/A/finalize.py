"""Validate evidence provenance and disclose failure; never upgrade to PASS."""
from pathlib import Path
import hashlib,json,datetime,platform,subprocess,sys
from zoneinfo import ZoneInfo
H=Path(__file__).resolve().parent;R=H.parents[3]
read=lambda n:json.loads((H/n).read_text());s=read('analysis/SUMMARY.json');build=read('build.json');checks={}
for n in ['static','gates','core','equivalence','clock-view-damage','surface','log-immutability','final-smoke']:
 checks[n]=read('final-evidence/'+n+'.json')['pass']
checks['ui88']=read('final-evidence/ui/ui.json')['pass'];checks['webgl29']=read('final-evidence/observed-HANDOFF/observed-world.json')['pass'];checks['idle120']=read('final-evidence/world120/world120.json')['checks']['idleSameTruthHash']
html=(R/'Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html').read_bytes();checks['rootIsTestedProduct']=hashlib.sha256(html).hexdigest()==build['htmlSha256'];checks['priorSevenByteExact']=len(read('final-evidence/archive-proof.json'))==7 and all(q['byteIdentical']for q in read('final-evidence/archive-proof.json'))
checks['common180NoNewFailure']=not s['common']['newFailures'];checks['naturalNoNewFailure']=not s['natural']['newFailures']
# Distinguish implementation checks from full regression approval.
checks['originalDomain420']=read('final-evidence/domain-acceptance.json')['pass'];checks['originalRelease300NoNewFailure']=read('final-evidence/release-comparison.json')['noNewFailures'];checks['extraBoundaryNoNewFailure']=not s['boundaryComparison']['newFailures']
mechanism=all(v for k,v in checks.items()if k not in ['originalDomain420','originalRelease300NoNewFailure','extraBoundaryNoNewFailure'])
v={'schema':'AEGIS_LAUNCH_HANDOFF_A_VERIFICATION_1','launchMechanismChecksPass':mechanism,'allRegressionPass':all(checks.values()),'releaseApproved':False,'checks':checks,'baseCommit':build['baseCommit'],'branch':'launch-handoff-a','htmlSha256':build['htmlSha256'],'htmlBytes':len(html),'knownNewFailureShots':3,'distinctNewFailureConditions':2,'domain':s['domain'],'fullEnvelopeSweep':False,'newRangeTable':False,'priorRangeData':'HISTORICAL_ENV_D_RECALC_REQUIRED','actionsDispatched':False,'mainMerged':False,'newReleaseOrTag':False,'reviewedAtKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat()}
(H/'final-evidence/verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert mechanism and not v['allRegressionPass'] and s['domain']['failed']==6 and len(s['boundaryComparison']['newFailures'])==1
assert sum(len(q['newFailures'])for q in s['release']['records'])==2
print(json.dumps({'mechanismPass':mechanism,'allRegressionPass':v['allRegressionPass'],'releaseApproved':False,'newFailureShots':3,'failedDomainAssertions':6}))
