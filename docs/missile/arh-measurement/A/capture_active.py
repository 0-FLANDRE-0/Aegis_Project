"""Capture actual SM-6 runtime profile and live functions; zero flight steps."""
from pathlib import Path
import json,sys,hashlib
from playwright.sync_api import sync_playwright
T=Path(__file__).resolve().parent;R=T.parents[3];O=T/'active';O.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
files={'DZT':R/'archive/v48/WIP_FUZE_ZEM_A/Aegis_SIM_v48_WIP_FUZE_ZEM_A.html','HANDOFF':R/'Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html'}
expected={'DZT':'edc159fa347d721d61d80228e2512665f22da0adb4f02fdf4e2dbe82789e0c9c','HANDOFF':'e42a2e05b8ff2096dfb334e7b9427cd2cd6da46d567083f06620ffdf35729ed7'}
names=['getSamArhProfile','_arhMonopulseMeasurement','_arhV2MonopulseMeasurement','_arhDecorateMeasurementFromCluster','_arhMeasurementCov','_arhServoCue','_arhInnovationStats','_sarhMeasurementModel','_sarhMeasurementJacobian','_sarhUnitGeometry','_arhEkfInit','_arhEkfUpdate','_arhBuildMeasurementSet','_v1UpdateArhMeasurementCore','_arhSeekerRandom','_arhSeekerRandn','clamp','deg','lerp','angNorm','_mIdx']
obj=','.join(n+':'+n+'.toString()'for n in names)
helper=(R/'docs/missile/termination/A/live-fixture.js').read_text()+r'''
window.__ARH_MEAS_CONTRACT_CAPTURE__=()=>{const m=TERM_LIVE_LAST_MISSILE_A;return {
 rfModel:getArhSeekerModel(),simStepCounter,
 runtime:{id:m?.id,lifeS:m?.life,isSM6:m?.isSM6,isESSM:m?.isESSM,guidanceCore:m?.guidanceCore,profileId:m?._v1Profile?.id,weaponType:m?.weaponType,vlsRelease:m?._vlsReleaseB2??null},
 profile:JSON.parse(JSON.stringify(getSamArhProfile(m))),functions:{'''+obj+r'''}};};
'''
case=json.loads((R/'docs/missile/termination/A/cases/normal.json').read_text())[152];case={**case,'maxTimeS':0}
errors=[];rows=[]
with sync_playwright()as pw:
 b=launch(pw)
 for variant,file in files.items():
  raw=file.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected[variant]
  p=load_fleet(b,instrument(raw,helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(120000)
  result=p.evaluate('c=>__TERM_LIVE_TEST__.run(c)',case);q=p.evaluate('__ARH_MEAS_CONTRACT_CAPTURE__()');q.update(variant=variant,htmlSha256=expected[variant],scope='Native VLS constructs actual SM6 object; fixture maxTimeS=0, no flight integration. No claim of replaying the 240km flight.',coreFailures=p.evaluate('__CORE_SELFTEST_FAILURES__'))
  assert q['runtime']['isSM6']and q['runtime']['profileId']=='SM6_BLKIA_SIM'and q['runtime']['lifeS']==0 and q['simStepCounter']==0,q['runtime']
  q['functionHashes']={k:hashlib.sha256(s.encode()).hexdigest()for k,s in q['functions'].items()};assert q['functionHashes']['_arhV2MonopulseMeasurement']=='9b206aa5727f5bffc11513f0bea56e0d82615352689454b0c3144fd57368579a';q['profileSha256']=hashlib.sha256(json.dumps(q['profile'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
  (O/(variant+'-capture.json')).write_text(json.dumps(q,indent=2)+'\n');rows.append({'variant':variant,'htmlSha256':q['htmlSha256'],'profileSha256':q['profileSha256'],'lifeS':q['runtime']['lifeS'],'ticks':q['simStepCounter'],'functions':len(names),'coreFailures':q['coreFailures']});p.close();print(json.dumps(rows[-1]),flush=True)
 b.close()
(O/'capture-summary.json').write_text(json.dumps({'rows':rows,'errors':errors,'newFlightSteps':0,'productChanges':0},indent=2)+'\n');assert not errors and all(not r['coreFailures']for r in rows)
