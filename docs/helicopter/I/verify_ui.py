"""Actual pointer AIR controls on CG desktop and mobile viewport."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/helicopter/H'))
from browser import load_fleet,launch

def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();checks={};rows=[];errors=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for w,h in [(1100,800),(390,1000)]:
   x=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',width=w,height=h,errors=errors);x.locator('#modeAirBtn').click();x.locator('#airHeloA1').click();x.locator('#airLaunchA').click();x.wait_for_timeout(270);checks[f'{w}.queueCancelLabel']='출격 대기 취소'in x.locator('#airLaunchA').inner_text();x.locator('#airLaunchA').click();x.wait_for_timeout(270);checks[f'{w}.cancelWorks']=x.evaluate('__HELO__.snapshot().queue.length===0&&__HELO__.snapshot().aircraft[1].state==="HANGARED"')
   x.locator('#airHeloA0').click();x.locator('#airLaunchA').click();x.evaluate('__NAVAL_SIM_DIAG__.stepTicks(1)');x.locator('#airHeloA1').click();x.wait_for_timeout(270);x.locator('#airLaunchA').click();x.evaluate('__NAVAL_SIM_DIAG__.stepTicks(1)');q=x.evaluate('__HELO__.snapshot()');checks[f'{w}.singleDoorQueued']=len(q['doors'])==1 and q['aircraft'][0]['state']=='HANGAR_OPEN'and q['aircraft'][1]['state']=='QUEUED'
   x.locator('#airRadarModeFPERI').click();x.locator('#airAltitudeC').click();x.locator('#airAltitudeInputC').fill('300');x.locator('#airAltitudeApplyC').click();q=x.evaluate('__HELO__.snapshot()');checks[f'{w}.commonRadarAndAltitude']=q['aircraft'][1]['targetAltitudeM']==300 and q['aircraft'][1]['radarMode']=='PERI'
   checks[f'{w}.oneTabTwoAircraft']=x.locator('#modeAirBtn').count()==1 and x.locator('#airAircraftA button').count()==2;checks[f'{w}.oldViewButtonsAbsent']=x.locator('#controlDeckAirPage button').filter(has_text='모함 보기').count()==0 and x.locator('#controlDeckAirPage button').filter(has_text='헬기 보기').count()==0;checks[f'{w}.noWeaponSideEffect']=x.evaluate('__HARPOON_JOURNAL_F1__.snapshot().records.length===0')
   x.screenshot(path=str(a.out/f'air-{w}.png'));rows.append(q);x.close()
  b.close()
 out={'pass':all(checks.values())and not errors,'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'ui.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
