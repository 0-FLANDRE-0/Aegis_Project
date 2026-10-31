"""Matched whole-world runs for G7 conditional reuse; reconstruct measured HTML first."""
from pathlib import Path
import sys,json,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
sources={'measured':Path(__import__('os').environ.get('GUN_B1_MEASURED_HTML','/tmp/aegis-gun-b1/measured-engine.html')).read_bytes(),'delivery':(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes()};fixture='\n'.join(p.read_text()for p in [R/'docs/map/E/test-helper.js',R/'docs/map/D/extension-fixture.js',H/'test-fixture.js'])+'''
__GB_TEST__.effectCheck=c=>{const q=__GB_TEST__.scenario(c);delete q.elapsedMs;return {q,rng:SIM_RNG_STATE,harpoonCount:harpoonWorldA().length,ownSurfaceAttack:attackSettingsH3(ACTIVE_SHIP_RUNTIME).enabled,npcShips:physicalShipsB().length,airPhysicalCount:targetPool.length};};
'''
E=H/'evidence/effect-equivalence';E.mkdir(parents=True,exist_ok=True);rows=[];errors=[];start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  pages={n:load_fleet(b,instrument(raw,fixture),own=ship,errors=errors)for n,raw in sources.items()}
  for p in pages.values():p.set_default_timeout(240000)
  for bearing in [0,90]:
   for count in [1,4]:
    for on in [False,True]:
     c={'seed':419010,'bearing':bearing,'count':count,'on':on};results={n:p.evaluate('c=>__GB_TEST__.effectCheck(c)',c)for n,p in pages.items()};q={'ship':ship,'condition':c,'equal':results['measured']==results['delivery'],'results':results};rows.append(q);print(ship,c,'equal',q['equal'],flush=True);(E/'progress.json').write_text(json.dumps({'rows':rows,'errors':errors},separators=(',',':'))+'\n')
  for p in pages.values():p.close()
 b.close()
out={'pass':all(r['equal']and all(v['harpoonCount']==0 and not v['ownSurfaceAttack']and v['npcShips']==0 and v['airPhysicalCount']==0 for v in r['results'].values())for r in rows)and not errors,'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-start,'htmlSha256':{n:hashlib.sha256(raw).hexdigest()for n,raw in sources.items()}};(E/'results.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(json.dumps({'pass':out['pass'],'pairs':len(rows),'elapsedS':out['elapsedS']}));raise SystemExit(not out['pass'])
