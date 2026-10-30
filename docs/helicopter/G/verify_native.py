"""Actual common RF on detached physical fixtures; active fixed-clock equality."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch,load_fleet
spec=importlib.util.spec_from_file_location('helo_f_native',ROOT/'docs/helicopter/F/verify_native.py');previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous);HOVER=previous.HOVER
PHYSICAL=r'''()=>{const d=__NAVAL_SIM_DIAG__,a=__APS153__,checks={},records={},fingerprint=()=>JSON.stringify({flight:__HELO__.snapshot(),radar:a.snapshot(),port:d.offboardSnapshotC(),rng:__HARPOON_DIAG_A__.snapshot().rng});d.setTerrainDiagBypass(true);d.setEmcon(true);
 for(const [name,options,hs]of [['PERI_ANCHOR',{mode:'PERI',windows:20000},.9],['SHORT_TARGET',{mode:'SHORT',windows:5000,rangeM:12500},.9],['LONG_LOW_SMALL',{mode:'LONG',windows:5000,rangeM:3000,altitudeM:25},.1],['LONG_HIGH_MEDIUM',{mode:'LONG',windows:5000,rangeM:50000,altitudeM:3000,rcsM2:180,targetHeightM:15},3]]){d.wip13a3SetManualWeather({hsM:hs,windSpeedMps:0,precipitation01:0});const before=fingerprint(),r=a.anchorExperiment(options);records[name]=r;checks[name+'Pd50']=r.ok&&Math.abs(r.pd-.5)<.035;checks[name+'NoWrites']=before===fingerprint();}
 const before=fingerprint(),table=a.performanceTable();checks.performancePure=before===fingerprint();checks.tablePRF=table.includes('prfHz=750')&&table.includes('prfHz=1200')&&table.includes('prfHz=2491')&&table.includes('pulseTune');checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;return {checks,records,table};}'''
CLOCK='scale=>{const d=__NAVAL_SIM_DIAG__,api=__HELO__;'+HOVER+r'''
 hover(152,'SHORT',true);const h=api.snapshot().aircraft;api.command(h[1].id,'SET_RADAR_MODE',{mode:'PERI'});d.createSurfaceFixture({rangeKm:20,bearingDeg:90,headingDeg:0,speedKt:0,sizeClass:'LARGE',radarHeightM:30});d.setEmcon(true);const run=d.runFramesToTicks(60,scale,1152);return {scale,run,aircraft:api.snapshot(),radar:__APS153__.snapshot(),port:d.offboardSnapshotC(),observers:d.observerSnapshotC(),rng:__HARPOON_DIAG_A__.snapshot().rng,core:__CORE_SELFTEST_FAILURES__};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];clock=[]
 with sync_playwright()as pw:
  b=launch(pw)
  class Controlled:
   def new_page(self,**kw):
    page=b.new_page(**kw);page.add_init_script('window.requestAnimationFrame=()=>0;');return page
  c=Controlled();page=load_fleet(c,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);r=page.evaluate(PHYSICAL)
  page.locator('#modeDebugBtn').click();before=page.evaluate('JSON.stringify(__HELO__.snapshot())');page.locator('#apsPerformanceF').click();text=page.locator('#apsPerformanceTextF').input_value();r['checks']['actualDebugModal']=page.locator('#apsPerformanceDialogF').is_visible()and'prfHz=2491'in text;r['checks']['actualModalReadOnly']=before==page.evaluate('JSON.stringify(__HELO__.snapshot())');page.screenshot(path=str(a.out/'performance-modal.png'));page.close()
  for scale in [1,8,16,64]:
   page=load_fleet(c,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);clock.append(page.evaluate(CLOCK,scale));page.close()
  b.close()
 sig=lambda x:json.dumps({k:x[k]for k in ['aircraft','radar','port','observers','rng']},sort_keys=True)
 for row in clock:r['checks']['fixedClock'+str(row['scale'])]=sig(row)==sig(clock[0])
 r['checks']['clockRealEmission']=all(all(h['sensorsE']['radar']['turn']>10 and h['sensorsE']['link']['transmittedTotal']>0 for h in row['aircraft']['aircraft'])for row in clock);r['checks']['clockPortsDelivered']=all(row['port']['accepted']>0 and row['port']['rejected']==0 for row in clock);r['checks']['clockCorePass']=all(not row['core']for row in clock)
 r.update(clock=clock,errors=errors,htmlSha256=hashlib.sha256(a.html.read_bytes()).hexdigest());r['pass']=all(r['checks'].values())and not errors;(a.out/'native.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':r['pass'],'checks':len(r['checks']),'failed':[k for k,v in r['checks'].items()if not v],'pd':{k:v['pd']for k,v in r['records'].items()},'errors':errors}));raise SystemExit(0 if r['pass']else 1)
if __name__=='__main__':main()
