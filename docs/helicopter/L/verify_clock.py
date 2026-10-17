"""ISAR fixed-tick equivalence at 1/8/16/64x; local aircraft settings/sensors only."""
import argparse,hashlib,json,sys,importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/helicopter/H'));from browser import load_fleet,launch
sp=importlib.util.spec_from_file_location('clock_hover',ROOT/'docs/helicopter/F/verify_native.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
FIXTURE='scale=>{const d=__NAVAL_SIM_DIAG__,api=__HELO__;'+m.HOVER+'''hover(300,'SHORT');d.createWip13aSurfaceTargetFixture({rangeKm:20,bearingDeg:0,headingDeg:0,speedKt:0});d.stepTicks(600);const id=api.snapshot().aircraft[0].id,q=__AEGIS_ACTIVE_SHIP_RUNTIME__.aviation.heloSensorsE.get(id).radar,c=[...q.contacts.values()].find(c=>c.point.x>10000);if(!c)throw Error('NO_OWN_CONTACT');api.command(id,'SET_RADAR_MODE',{mode:'ISAR'});api.command(id,'ISAR_TARGET',{x:c.point.x,y:c.point.y});const run=d.runFramesToTicks(60,scale,1024);return {run,helo:api.snapshot(),isar:__ISAR_F2__.snapshot(),radar:__APS153__.snapshot(),rng:__HARPOON_DIAG_A__.snapshot().rng,core:__CORE_SELFTEST_FAILURES__};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];rows=[];checks={}
 with sync_playwright()as pw:
  b=launch(pw)
  for scale in [1,8,16,64]:
   x=load_fleet(b,raw,errors=errors);x.evaluate('window.requestAnimationFrame=()=>0');r=x.evaluate(FIXTURE,scale);rows.append(r);x.close()
  b.close()
 sig=lambda r:{k:r[k]for k in ['helo','isar','radar','rng']}
 for i,s in enumerate([1,8,16,64]):checks[str(s)+'.sameFixedResult']=sig(rows[i])==sig(rows[0]);checks[str(s)+'.completed']=rows[i]['isar']['aircraft'][0]['isar']['stats']['completed']==1;checks[str(s)+'.core']=not rows[i]['core']
 out={'pass':all(checks.values())and not errors,'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'clock.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
