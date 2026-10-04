import shutil
"""Exercise CG-52 sensor plots, common track fusion and gun release authority."""
from pathlib import Path
import json,sys,os
from playwright.sync_api import sync_playwright

src=Path(sys.argv[1]);out=Path(sys.argv[2]if len(sys.argv)>2 else os.environ.get('AEGIS_EVIDENCE_DIR',str(src.resolve().parent/'artifacts'/'bunkerhill')));out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE') or shutil.which('chromium') or None,headless=True,args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
 context=None;errors=[];rows=[];details={}
 def fresh(phase):
  global context
  if context:context.close()
  context=b.new_context();page=context.new_page()
  page.on('pageerror',lambda e:errors.append({'phase':phase,'error':str(e)}))
  page.add_init_script('window.__NAVAL_SIM_SEED__=0x6d2b79f5')
  page.route('https://aegis.test/**',lambda r:r.fulfill(body=src.read_bytes(),content_type='text/html'))
  page.goto('https://aegis.test/candidate',wait_until='domcontentloaded',timeout=90000)
  page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000)
  page.locator('#aegisShipSelect').select_option('CG_52_LATE_TICONDEROGA');page.locator('#aegisShipConfirmBtn').click()
  page.wait_for_function('window.C55Packaging?.ready&&window.__NAVAL_SIM_DIAG__',timeout=90000)
  return page
 def check(name,value,detail=None):rows.append({'name':name,'pass':bool(value),'detail':detail})
 page=fresh('pointed-dwells')
 check('core zero',page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[])
 pointed=page.evaluate('window.__NAVAL_SIM_DIAG__.runWip13b13PointedSurfaceDwellFixture()')
 details['pointed']=pointed
 for k,v in pointed['checks'].items():check('pointed '+k,v,pointed['counts'])
 print(json.dumps({'stage':'pointed','checks':pointed['checks'],'counts':pointed['counts']}),flush=True)
 page=fresh('sensor-roles')
 role=page.evaluate('window.__NAVAL_SIM_DIAG__.runWip13b9SurfaceSensorRoleFixture()')
 details['roles']=role
 for k,v in role['checks'].items():check('roles '+k,v)
 print(json.dumps({'stage':'roles','checks':role['checks']}),flush=True)
 page=fresh('time-and-damage')
 for name,expression in [('surface/flood','runWip13aSurfaceTargetDiagnostics()'),('surface time-scale','runWip13aTimeScaleRegression()'),('gun time-scale','runWip13b2TimeScaleRegression()')]:
  q=page.evaluate('window.__NAVAL_SIM_DIAG__.'+expression);details[name]=q
  check(name,q.get('pass',all(q.get('checks',{}).values())))
 damage=page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB3Damage.audit()');details['ciwsDamage']=damage
 check('two independently degraded Phalanx mounts',len(damage['mounts'])==2 and all(m['type']=='GUN' and m['rows'][0]['oneSecondRounds']>m['rows'][1]['oneSecondRounds']>m['rows'][2]['oneSecondRounds']>m['rows'][3]['oneSecondRounds'] for m in damage['mounts']))
 page=fresh('ew-pods')
 ew=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__;document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);
   d.setEmcon(false);d.setJammerAutoTrack(false);d.setNoiseJam(true);d.setDeceptionJam(true);d.setJammerBearingDeg(0);d.advanceFrameNoRender(.5,1);
   const stbd=d.bunkerEwPathProbe(),port=d.bunkerEwPathProbe({x:0,y:-10000,z:10});
   d.wip101SetModuleDamage('AN/SLQ-32(우현)',40);const degraded=d.bunkerEwPathProbe();
   d.wip101SetModuleDamage('AN/SLQ-32(우현)',100);const failed=d.bunkerEwPathProbe();
   const portStillWorks=d.bunkerEwPathProbe({x:0,y:-10000,z:10});
   return {stbd,port,degraded,failed,portStillWorks};}''');details['ew']=ew
 check('visible outboard EW pod selected',ew['stbd']['emitter']['podId']=='SLQ32_STBD' and ew['port']['emitter']['podId']=='SLQ32_PORT')
 check('noise and deception power degrade continuously',0<ew['degraded']['noise']['effectiveErpW']<ew['stbd']['noise']['effectiveErpW'] and 0<ew['degraded']['deception']['effectiveReplayErpW']<ew['stbd']['deception']['effectiveReplayErpW'])
 check('blocked failed pod cannot emit',ew['failed']['emitter'] is None and not ew['failed']['noise']['active'] and not ew['failed']['deception']['active'])
 check('opposite EW pod remains available',ew['portStillWorks']['emitter']['podId']=='SLQ32_PORT')
 check('page errors zero',not errors,errors)
 result={'schema':'AEGIS_CG52_RUNTIME_REGRESSION_V1','bootSeed':0x6d2b79f5,'rows':rows,'details':details,'errors':errors,'passed':sum(r['pass'] for r in rows),'total':len(rows),'pass':all(r['pass'] for r in rows)}
 (out/'cg52-runtime.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({'passed':result['passed'],'total':result['total'],'pass':result['pass'],'failed':[r['name']for r in rows if not r['pass']]}),flush=True)
 b.close()
 if not result['pass']:raise SystemExit(1)
