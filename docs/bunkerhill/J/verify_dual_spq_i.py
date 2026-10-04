"""SPQ-9 antipodal sweep cadence, own face masks, 2D/clutter and source shell."""
from pathlib import Path
import argparse,hashlib,json
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');p.add_argument('--main-override');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];checks={};details={}
with sync_playwright()as pw:
 b=launch(pw);page=load(b,served_bytes(a.html,a.main_override),errors=errors)
 q=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,rows=[];for(let i=0;i<125;i++){d.wip13b9StepSurfaceSensors(1,{spy:false,spq:true,bme:true});const st=d.bunkerRenderState();rows.push({time:st.timeS,radars:st.auxNav,beams:{spq9b:st.radar.spq9bBeams,bridgeMasterE:st.radar.bridgeMasterEBeams}});}return {rows,audit:d.bunkerRadarAudit(),profile:d.shipProfileV48Wip11(),core:window.__CORE_SELFTEST_FAILURES__};}''');details['sweeps']=q
 # Render-state adapters expose the two scanned faces; the native receiver
 # evidence is separately checked by the pointed-dwell fixture.
 rows=q['rows'];beamRows=[r['beams']for r in rows]
 checks['DualRadarAudit']=q['audit']['pass'];checks['EveryFrameTwoAntipodalSPQFaces']=all(len(r['spq9b'])==2 and abs(abs((r['spq9b'][0]['azWorldRad']-r['spq9b'][1]['azWorldRad']+3.141592653589793)%(2*3.141592653589793)-3.141592653589793)-3.141592653589793)<1e-8 for r in beamRows)
 checks['OneNavigationBeam']=all(len(r['bridgeMasterE'])==1 for r in beamRows)
 checks['NominalOneSecondRevisit']=all(all(q['nominalRevisitS']==1 and q['rpm']==30 for q in r['spq9b'])for r in beamRows)
 checks['IndependentFaceMasks']=any(r['spq9b'][0]['masked']!=r['spq9b'][1]['masked']for r in beamRows)
 checks['NoInventedElevation']=all(all(q['elevationObservable']is False and q['channel']=='TWO_DIMENSIONAL_SURFACE'for q in r['spq9b'])for r in beamRows)
 checks['LayoutLabelledSimTune']=all(all('SIM_TUNED'in q['modelBasis']for q in r['spq9b'])for r in beamRows)
 pointed=page.evaluate('window.__NAVAL_SIM_DIAG__.runWip13b13PointedSurfaceDwellFixture()');details['pointedReceiver']=pointed;checks['RealReceiverRoleAndClutter']=all(pointed['checks'].values())
 checks['CoreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[];page.close();b.close()
checks['PageErrorsZero']=not errors
r={'schema':'AEGIS_CG52_DUAL_SPQ9_I','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'diagnosticOnlyMemoryOverride':bool(a.main_override),'checks':checks,'details':details,'errors':errors,'pass':all(checks.values())};(out/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':r['pass']},ensure_ascii=False),flush=True)
if not r['pass']:raise SystemExit(1)
