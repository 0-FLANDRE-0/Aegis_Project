"""Real desktop/touch AIR commands and CAMERA entries in the original HTML."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch,load_fleet

def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for width,height in [(1000,760),(390,844)]:
   page=load_fleet(b,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,width=width,height=height,touch=width<500,errors=errors);checks={}
   before=page.evaluate('JSON.stringify(__HELO__.snapshot())');page.locator('#modeAirBtn').click();checks['fiveTabs']=page.locator('.control-deck-tab[data-tab]').count()==5;checks['tabReadOnly']=before==page.evaluate('JSON.stringify(__HELO__.snapshot())');page.locator('#airHeloA0').click()
   old=page.evaluate('JSON.stringify(__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state)')
   for x in [.4,.55,.7]:page.locator('#c').click(position={'x':width*x,'y':height*.18});page.wait_for_timeout(100)
   checks['threeMapWaypoints']=page.evaluate('__HELO__.snapshot().aircraft[0].route.length===3');checks['shipWeaponCursorsUntouched']=old==page.evaluate('JSON.stringify(__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state)');page.locator('#airUndoB').click();checks['undoLastWaypoint']=page.evaluate('__HELO__.snapshot().aircraft[0].route.length===2');page.locator('#airFollowB').click();checks['followButton']=page.evaluate('__HELO__.snapshot().aircraft[0].navigationMode==="FOLLOW_SHIP"&&__HELO__.snapshot().aircraft[0].route.length===0');page.locator('#c').click(position={'x':width*.62,'y':height*.16});checks['mapReturnsToRoute']=page.evaluate('__HELO__.snapshot().aircraft[0].navigationMode==="ROUTE"&&__HELO__.snapshot().aircraft[0].route.length===1')
   page.locator('#airLaunchA').click();page.locator('#airHeloA1').click();page.wait_for_timeout(300);page.locator('#airLaunchA').click();checks['twoLaunchesQueued']=page.evaluate('__HELO__.snapshot().queue.length===2');page.locator('#airCancelA').click();checks['queuedCancel']=page.evaluate('__HELO__.snapshot().queue.length===1')
   checks['controlsLeftListRight']=page.evaluate('document.getElementById("airControlsB").getBoundingClientRect().right<=document.getElementById("airListB").getBoundingClientRect().left')
   checks['listHasEmptySpace']=page.evaluate('''()=>{const l=document.getElementById('airAircraftA'),rows=[...l.children],sum=rows.reduce((s,r)=>s+r.getBoundingClientRect().height,0);return l.clientHeight>sum+12;}''')
   checks['listScrollEnabled']=page.evaluate('["auto","scroll"].includes(getComputedStyle(document.getElementById("airAircraftA")).overflowY)');checks['noHorizontalOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth');checks['cameraEntries']=page.locator('#c15CameraFlyout #external3DHeloB0').count()==1 and page.locator('#c15CameraFlyout #external3DHeloB1').count()==1
   page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(1500)');page.locator('#airHeloA0').click();checks['livePhaseStatus']='갑판 이동'in page.locator('#airHeloA0').inner_text();page.screenshot(path=str(a.out/f'air-{width}.png'));rows.append({'viewport':[width,height],'checks':checks});page.close()
  b.close()
 out={'pass':not errors and all(all(r['checks'].values())for r in rows),'cases':rows,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest()};(a.out/'ui.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':sum(len(r['checks'])for r in rows),'failed':[k for r in rows for k,v in r['checks'].items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
