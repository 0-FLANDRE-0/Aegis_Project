"""Real reusable DDG/CG physical shapes through common RF -> ISAR features/classifier."""
import argparse,hashlib,json,sys,importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/helicopter/H'));from browser import load_fleet,launch
sp=importlib.util.spec_from_file_location('class_hover',ROOT/'docs/helicopter/F/verify_native.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
RUN='()=>{const d=__NAVAL_SIM_DIAG__,api=__HELO__;'+m.HOVER+'''hover(300,'SHORT');const w=__AEGIS_ENGAGEMENT_RUNTIME__,r=[...w.ships.values()].find(r=>r!==__AEGIS_ACTIVE_SHIP_RUNTIME__);d.tacticalCommandH1(r.entityId,{enabled:false});d.attackCommandH3(r.entityId,{enabled:false});d.maneuverCommandH2(r.entityId,{enabled:false});const n=r.navigation;Object.assign(n,{heading:0,speed:0,swayMps:0,targetSpeedKt:0,targetRudder:0,rudder:0,turnRate:0,vx:0,vy:0});n.positionWorld.x=20000*.0038;n.positionWorld.y=0;d.stepTicks(600);const id=api.snapshot().aircraft[0].id,q=__AEGIS_ACTIVE_SHIP_RUNTIME__.aviation.heloSensorsE.get(id).radar,c=[...q.contacts.values()].find(c=>c.point.x>10000&&c.point.x<30000);if(!c)throw Error('NO_MEASURED_SHIP_CONTACT');const begin=api.command(id,'SET_RADAR_MODE',{mode:'ISAR'}),target=api.command(id,'ISAR_TARGET',{x:c.point.x,y:c.point.y});d.stepTicks(1000);return {begin,target,isar:__ISAR_F2__.snapshot(),h:api.snapshot().aircraft[0],core:__CORE_SELFTEST_FAILURES__};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];checks={};rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for ship,expected in [('DDG_119_LATE_FLIGHT_IIA','BURKE_IIA'),('CG_52_LATE_TICONDEROGA','TICONDEROGA')]:
   x=load_fleet(b,raw,ally=ship,errors=errors);x.evaluate('window.requestAnimationFrame=()=>0');r=x.evaluate(RUN);rows.append(r);f=r['isar']['aircraft'][0]['isar']['result'];checks[expected+'.realRF']=r['begin']['ok']and r['target']['ok']and bool(f);checks[expected+'.measuredClass']=f['result']['candidates'][0]['classId']==expected;checks[expected+'.anonymous']=not any(s in json.dumps(f)for s in ['truthRef','profileId','entityId','targetId','_truthObject']);checks[expected+'.core']=not r['core'];x.close()
  b.close()
 out={'pass':all(checks.values())and not errors,'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'limits':'Friendly physical DDG/CG staged at20km, actual shared physical/RF synthesis. Expected class is test-only; no truth sent to target command or classifier.'};(a.out/'classes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
