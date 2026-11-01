from pathlib import Path
import json,time,os
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,load_fast_http,sha
E=P/'evidence';S=E/'screenshots';S.mkdir(parents=True,exist_ok=True);errors=[];results=json.loads((E/'render-progress.json').read_text())if os.environ.get('CG_RENDER_ONLY')else{};start=time.perf_counter()
extra=(P/'render-fixture.js').read_text()
with sync_playwright()as pw:
 b=launch(pw,True)
 for label,file,ship in [('current','Aegis_SIM_v48_WIP_CG_TURRET_A.html','CG_52_LATE_TICONDEROGA'),('MAP_E','Aegis_SIM_v48_WIP_MAP_E.html','CG_52_LATE_TICONDEROGA'),('B2B','Aegis_SIM_v48_WIP_GUN_B2.html','CG_52_LATE_TICONDEROGA'),('DDG-before','Aegis_SIM_v48_WIP_GUN_B2.html','DDG_119_LATE_FLIGHT_IIA'),('DDG-after','Aegis_SIM_v48_WIP_CG_TURRET_A.html','DDG_119_LATE_FLIGHT_IIA')]:
  if os.environ.get('CG_RENDER_ONLY')and label!=os.environ['CG_RENDER_ONLY']:continue
  raw=build(file=file,extra=extra);server,url=serve(raw);p=load_fast_http(b,url,own=ship,width=1400,height=900,errors=errors);p.set_default_timeout(180000)
  result={'specs':p.evaluate('__CG_AUDIT__.specs()'),'clearance':p.evaluate('__CG_AUDIT__.scan()')}if label!='MAP_E'else{'comparisonScope':'original render geometry only; pre-B1 has no gunB1OwnGuns API'}
  p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000)
  result['rendererAudit']=p.evaluate('__WIP148_3D_VIEW__.contractAudit()')if ship.startswith('CG')else None
  result['signatureSha256']=sha(json.dumps(p.evaluate('__CG_AUDIT__.signature()'),separators=(',',':')).encode())
  for w,h in[(1400,900),(832,384)]:
   p.set_viewport_size({'width':w,'height':h});p.wait_for_timeout(240)
   for key in(['mk45','mk45Aft']if ship.startswith('CG')else['mk45']):
    p.evaluate('k=>__CG_AUDIT__.camera(k)',key);p.wait_for_timeout(120);p.screenshot(path=str(S/f'{label}-{w}-{key}.png'))
  if label=='current':result['poses']=p.evaluate('__CG_AUDIT__.poses()')
  results[label]=result;(E/'render-progress.json').write_text(json.dumps(results,indent=2)+'\n');p.context.close();server.shutdown();print(label,round(time.perf_counter()-start,1),flush=True)
 b.close()
checks={'muzzle18':len(results['current']['poses']['rows'])==18,'muzzleWithin0_1M':results['current']['poses']['maxErrorM']<=.1,'ddgGeometryExact':results['DDG-before']['signatureSha256']==results['DDG-after']['signatureSha256'],'cgOriginalGeometryExact':results['current']['signatureSha256']==results['MAP_E']['signatureSha256'],'rendererConstraints':all(v for k,v in results['current']['poses']['renderAudit']['checks'].items()if k!='sourcePreserved'),'errors0':not errors}
if results['B2B'].get('rendererAudit'):
 checks['sourceCountBaselineExact']=all(results['current']['poses']['renderAudit'][k]==results['B2B']['rendererAudit'][k]for k in['retainedTriangles','sourceTriangles','declaredSourceTriangles'])
out={'pass':all(checks.values()),'checks':checks,'records':results,'errors':errors,'elapsedS':time.perf_counter()-start};(E/'render.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':checks,'maxErrorM':results['current']['poses']['maxErrorM'],'errors':errors}));raise SystemExit(not out['pass'])
