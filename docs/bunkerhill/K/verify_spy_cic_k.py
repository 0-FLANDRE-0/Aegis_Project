"""Observe real canvas face labels and arcs; compare DDG pixels to exact J."""
from pathlib import Path
import argparse,json,hashlib,math,base64
from playwright.sync_api import sync_playwright
from browser_i import launch,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('baseline_j');p.add_argument('out');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
checks={};details={};errors=[]
hook="""(()=>{window.__SPY_DRAW_K__={labels:{},arcs:[]};const proto=CanvasRenderingContext2D.prototype,f=proto.fillText,arc=proto.arc;proto.fillText=function(t,x,y,...rest){if(this.canvas.id==='c'&&/^F[1-4] (\\d+%|OFF)$/.test(t)){const m=this.getTransform();window.__SPY_DRAW_K__.labels[t.slice(0,2)]={text:t,x,y,a:m.a,b:m.b,c:m.c,d:m.d};}return f.call(this,t,x,y,...rest);};proto.arc=function(x,y,r,a,b,...rest){if(this.canvas.id==='c'&&x===0&&y===0&&Math.abs(b-a-(Math.PI/2-Math.PI/30))<1e-10){window.__SPY_DRAW_K__.arcs.push({r,a,b,color:this.strokeStyle});if(window.__SPY_DRAW_K__.arcs.length>32)window.__SPY_DRAW_K__.arcs.splice(0,16);}return arc.call(this,x,y,r,a,b,...rest);};})();"""
def delta(a,b):return abs((a-b+math.pi)%(2*math.pi)-math.pi)
with sync_playwright()as pw:
 b=launch(pw)
 def fresh(path,ship):
    page=b.new_page(viewport={'width':648,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.add_init_script('window.__NAVAL_SIM_SEED__=0x6d2b79f5;'+hook)
    page.route('https://aegis.test/**',lambda r:r.fulfill(body=served_bytes(path),content_type='text/html'));page.goto('https://aegis.test/candidate?view3d=0',wait_until='load',timeout=90000)
    page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000);page.locator('#aegisShipSelect').select_option(ship);page.locator('#aegisShipConfirmBtn').click()
    page.wait_for_function('window.C55Packaging?.ready&&window.__NAVAL_SIM_DIAG__',timeout=120000)
    page.evaluate("()=>{document.getElementById('wip125DepartBtn').click();const d=window.__NAVAL_SIM_DIAG__;d.ciwsB1Closure.setPaused(true);d._resetShipTest();d.setEmcon(false);window.__AEGIS_ACTIVE_SHIP_RUNTIME__.navigation.heading=0;}")
    page.wait_for_timeout(200);return page
 for ship,relative in [('CG_52_LATE_TICONDEROGA',[0,math.pi/2,math.pi,-math.pi/2]),('DDG_119_LATE_FLIGHT_IIA',[-math.pi/4,math.pi/4,math.pi*3/4,-math.pi*3/4])]:
    old=fresh(a.baseline_j,ship);oldLabels=old.evaluate('window.__SPY_DRAW_K__.labels');oldPng=old.locator('#c').evaluate('c=>c.toDataURL()');old.close()
    page=fresh(a.html,ship);checks[ship+'CoreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[]
    cases=[]
    for heading in [0,math.pi/4,math.radians(123),math.radians(229)]:
      page.evaluate('h=>{window.__AEGIS_ACTIVE_SHIP_RUNTIME__.navigation.heading=h;window.__SPY_DRAW_K__={labels:{},arcs:[]};}',heading);page.wait_for_timeout(130)
      q=page.evaluate('({draw:window.__SPY_DRAW_K__,layout:window.__NAVAL_SIM_DIAG__.spyCicFaceLayoutK()})');cases.append({'heading':heading,**q})
      expected=[row['angleRad']for row in q['layout']]
      checks[ship+f'LabelsAt{round(math.degrees(heading))}']=len(q['draw']['labels'])==4 and all(delta(math.atan2(q['draw']['labels']['F'+str(i+1)]['y'],q['draw']['labels']['F'+str(i+1)]['x']),ang)<1e-10 for i,ang in enumerate(expected)) and all(delta(ang,heading+rel)<2e-4 for ang,rel in zip(expected,relative))
      actual=q['draw']['arcs'][-4:];checks[ship+f'ArcsAt{round(math.degrees(heading))}']=len(actual)==4 and all(delta((row['a']+row['b'])/2,ang)<1e-10 for row,ang in zip(actual,expected))
    if ship.startswith('CG'):
      checks['BaselineCgHadBurkeAngles']=all(delta(math.atan2(oldLabels['F'+str(i+1)]['y'],oldLabels['F'+str(i+1)]['x']),rel-math.pi/4)<1e-10 for i,rel in enumerate(relative))
      page.evaluate("()=>{const d=window.__NAVAL_SIM_DIAG__,r=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,layout=d.spyCicFaceLayoutK();r.damage.flood.setDamage(layout[1].moduleName,100);}");page.wait_for_timeout(150)
      damaged=page.evaluate('window.__SPY_DRAW_K__.labels');checks['DamagedFaceLabelStaysPhysical']=damaged['F2']['text']=='F2 OFF' and delta(math.atan2(damaged['F2']['y'],damaged['F2']['x']),math.radians(229)+math.pi/2)<2e-4
      details['damagedFace']=damaged
    else:
      page.evaluate('window.__AEGIS_ACTIVE_SHIP_RUNTIME__.navigation.heading=0');page.wait_for_timeout(150)
      newPng=page.locator('#c').evaluate('c=>c.toDataURL()');checks['DdgCanvasPixelsExactJ']=oldPng==newPng
      (out/'ddg-J.png').write_bytes(base64.b64decode(oldPng.split(',',1)[1]));(out/'ddg-K.png').write_bytes(base64.b64decode(newPng.split(',',1)[1]))
    page.screenshot(path=str(out/(ship+'.png')));details[ship]={'baselineLabels':oldLabels,'cases':cases};page.close()
 b.close()
checks['PageErrorsZero']=not errors;r={'schema':'AEGIS_SPY_CIC_K_1','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'checks':checks,'details':details,'errors':errors,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':r['pass']}),flush=True)
if not r['pass']:raise SystemExit(1)
