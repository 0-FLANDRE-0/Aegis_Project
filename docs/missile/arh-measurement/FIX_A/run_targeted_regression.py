"""Targeted five-seed OFF/ON regression on final AU bytes."""
from pathlib import Path
import hashlib,json,sys,time
from playwright.sync_api import sync_playwright

H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
build=json.loads((H/'build.json').read_text());info=build['variants']['AU'];raw=Path(info['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==info['htmlSha256']
fixture=(R/'docs/missile/termination/A/live-fixture.js').read_text();cases=json.loads((R/'docs/missile/termination/A/cases/normal.json').read_text());indices=list(range(150,160))
reference=json.loads((R/'docs/missile/launch-handoff/A/final-evidence/release-HANDOFF/normals.json').read_text())['results']

def main():
 errors=[];rows=[];start=time.perf_counter()
 with sync_playwright() as pw:
  browser=launch(pw);page=load_fleet(browser,instrument(raw,fixture),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(240000)
  try:
   for i in indices:
    result=page.evaluate('c=>__TERM_LIVE_TEST__.run(c)',cases[i]);before=reference[i]
    row={'caseIndex':i,'condition':cases[i],'before':before,'after':result,'successChanged':before.get('success')!=result.get('success')}
    rows.append(row);print(json.dumps({'caseIndex':i,'seed':cases[i]['seed'],'terminationOn':cases[i]['enabled'],'beforeSuccess':before.get('success'),'afterSuccess':result.get('success'),'beforeClosestM':before.get('closestM'),'afterClosestM':result.get('closestM'),'reason':result.get('reason')},ensure_ascii=False),flush=True)
  finally:page.close();browser.close()
 result={'schema':'AEGIS_ARH_MEASUREMENT_FIX_A_TARGETED_REGRESSION_1','htmlSha256':info['htmlSha256'],'rows':rows,
  'historicalSuccessToNewFailure':[r['caseIndex'] for r in rows if r['before'].get('success') and not r['after'].get('success')],
  'historicalFailureToNewSuccess':[r['caseIndex'] for r in rows if not r['before'].get('success') and r['after'].get('success')],
  'errors':errors,'elapsedS':time.perf_counter()-start}
 (H/'targeted-regression.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'successToFailure':result['historicalSuccessToNewFailure'],'failureToSuccess':result['historicalFailureToNewSuccess'],'errors':errors,'elapsedS':result['elapsedS']}));raise SystemExit(0 if not result['historicalSuccessToNewFailure'] and not errors else 1)
if __name__=='__main__':main()
