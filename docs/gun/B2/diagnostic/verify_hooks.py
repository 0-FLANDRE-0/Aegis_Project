"""Matched native-versus-instrumented fixed-world check, plus operative flags."""
from pathlib import Path
import json,sys,time,hashlib
from playwright.sync_api import sync_playwright
from build_fixture import build,R,B
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
out=B/'evidence/hook-equivalence';out.mkdir(parents=True,exist_ok=True);errors=[];rows=[];start=time.perf_counter()
helper="""__GB_TEST__.check=c=>{const result=__GB_TEST__.scenario(c);return {result,rng:SIM_RNG_STATE,step:simStepCounter,coreState:{shipHP,navigation:{...shipNav,trail:undefined},gun:gunB1OwnGuns().map(([id,g])=>({id,q:g.snapshot()})),targets:enemyMissiles.map(t=>({id:t.id,p:{x:worldToMeters(t.x),y:worldToMeters(t.y),z:Number(t.z)||0},v:{x:worldSpeedToMps(t.vx??0),y:worldSpeedToMps(t.vy??0),z:Number(t.vz)||0},alive:t.alive})),lock:selectedLockId}};};"""
native=build(False,helper);configured=build();configured_sha=hashlib.sha256(configured).hexdigest()
with sync_playwright()as pw:
 browser=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  p=load_fleet(browser,native,own=ship,errors=errors);q=load_fleet(browser,configured,own=ship,errors=errors)
  for page in [p,q]:page.set_default_timeout(600000)
  for bearing in [0,90]:
   for count in [1,4]:
    c={'seed':419010,'bearing':bearing,'count':count,'on':True};a=p.evaluate('c=>__GB_TEST__.check(c)',c);b=q.evaluate('c=>__G2D__.run(c)',c);original={k:b[k]for k in a};a['result'].pop('elapsedMs',None);original['result'].pop('elapsedMs',None);row={'ship':ship,'c':c,'equal':a==original,'native':a,'instrumented':original};rows.append(row);(out/'progress.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');print(ship,bearing,count,row['equal'],flush=True)
  p.close();q.close()
 browser.close()
report={'pass':all(r['equal']for r in rows)and not errors,'rows':rows,'errors':errors,'instrumentedHtmlSha256':configured_sha,'elapsedS':time.perf_counter()-start};(out/'results.json').write_text(json.dumps(report,separators=(',',':'))+'\n');raise SystemExit(not report['pass'])
