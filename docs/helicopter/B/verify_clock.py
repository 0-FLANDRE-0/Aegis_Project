"""Same fixed ticks through 1/8/16/64x with moving ship and wind."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch,load_fleet
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  # Keep the production HTML bytes intact. Suppress only background RAF before
  # bootstrap, so every case starts at tick zero; advanceFrameNoRender below
  # supplies the actual 1/8/16/64x frame accumulator and all fixed subsystems.
  class ControlledBrowser:
   def new_page(self,**options):
    page=b.new_page(**options);page.add_init_script('window.requestAnimationFrame=()=>0;');return page
  controlled=ControlledBrowser()
  for scale in [1,8,16,64]:
   page=load_fleet(controlled,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors)
   row=page.evaluate('''scale=>{const d=__NAVAL_SIM_DIAG__,api=__HELO__;__WIP125_DIAG__.forcePreSail();document.getElementById('wip125DepartBtn').click();d.setTerrainDiagBypass(true);const s=api.snapshot();for(const h of s.aircraft){api.command(h.id,'LAUNCH');api.command(h.id,'WAYPOINT',{x:2000+h.slot*1000,y:1500});}const run=d.runFramesToTicks(60,scale,16000),after=api.snapshot();return {scale,run,after,rng:__HARPOON_DIAG_A__.snapshot().rng,core:__CORE_SELFTEST_FAILURES__};}''',scale);rows.append(row);page.close()
  b.close()
 ref=json.dumps({'after':rows[0]['after'],'rng':rows[0]['rng']},sort_keys=True);checks={str(r['scale'])+'.exact':json.dumps({'after':r['after'],'rng':r['rng']},sort_keys=True)==ref for r in rows};checks['core']=all(not r['core']for r in rows)
 out={'pass':all(checks.values())and not errors,'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest()};(a.out/'clock.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
