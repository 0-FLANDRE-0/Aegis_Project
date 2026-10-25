"""Unforced onboard RF/EKF regression on 28 frozen natural cases."""
from pathlib import Path
import gzip,hashlib,json,sys,time
from playwright.sync_api import sync_playwright

H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument,fixture
build=json.loads((H/'build.json').read_text());info=build['variants']['AU'];file=Path(info['file']);raw=file.read_bytes();assert hashlib.sha256(raw).hexdigest()==info['htmlSha256']
cases=json.loads((R/'docs/missile/fuze-zem/A/natural-cases.json').read_text());historical=json.loads(gzip.decompress((R/'docs/missile/launch-handoff/A/final-results/natural.json.gz').read_bytes()))
before={x['condition']['caseId']:x['result'] for x in historical['rows'] if x['variant']=='HANDOFF'}
extra=r'''
const amfaNativeDyn=updateSamSixDofLiteDynamics;
updateSamSixDofLiteDynamics=function(m,dt,y,p,env){const result=amfaNativeDyn(m,dt,y,p,env);const key=[m.vlsPhase,m.pitchoverPhase,m._v1GuidancePhase,m._v1GuidanceAuthority,m.dead].join('/');if(m._amfaNativeLast!==key){m._amfaNativeLast=key;(m._amfaNativeTrace??=[]).push(JSON.parse(JSON.stringify({lifeS:m.life,vls:m.vlsPhase,pitchover:m.pitchoverPhase,handoffAt:m._pitchoverCompleteAt??null,owner:m._v1LaunchControlAuthority?'LAUNCH':m._wip79KappaActive?'KAPPA':m._v1TerminalActive?'TERMINAL':'GUIDANCE_OR_FALLBACK',guidance:m._v1GuidancePhase,source:m._v1GuidanceAuthority,actualG:m.sam6dofActualNormalG,deliveredG:m.sam6dofDeliveredG,limitedCommandG:m._v1GAchieved})));}return result;};
'''
helper=fixture();helper=helper.replace('return {diagnostic:diagCaseA,','return {handoffAtS:m._pitchoverCompleteAt??null,handoffTrace:m._amfaNativeTrace??[],diagnostic:diagCaseA,',1)+extra

def main():
 rows=[];errors=[];start=time.perf_counter()
 with sync_playwright() as pw:
  browser=launch(pw);page=load_fleet(browser,instrument(raw,helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(240000)
  try:
   for c in cases:
    q=page.evaluate('c=>__TERM_LIVE_TEST__.run(c)',c);b=before[c['caseId']];row={'condition':c,'result':q,'before':b};rows.append(row)
    print(c['caseId'],q.get('reason'),q.get('success'),q.get('closestM'),flush=True)
  finally:page.close();browser.close()
 changed=[x for x in rows if x['result']!=x['before']];stf=[x['condition']['caseId'] for x in rows if x['before'].get('success') and not x['result'].get('success')];fts=[x['condition']['caseId'] for x in rows if not x['before'].get('success') and x['result'].get('success')]
 result={'schema':'AEGIS_ARH_MEASUREMENT_FIX_A_NATURAL_28_1','htmlSha256':info['htmlSha256'],'rows':rows,'changedCount':len(changed),'successToFailure':stf,'failureToSuccess':fts,'errors':errors,'elapsedS':time.perf_counter()-start}
 (H/'natural-28.json.gz').write_bytes(gzip.compress(json.dumps(result,separators=(',',':')).encode(),9,mtime=0));(H/'natural-28-summary.json').write_text(json.dumps({k:result[k] for k in ('changedCount','successToFailure','failureToSuccess','errors','elapsedS')},indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ('changedCount','successToFailure','failureToSuccess','errors','elapsedS')}));raise SystemExit(0 if not stf and not errors else 1)
if __name__=='__main__':main()
