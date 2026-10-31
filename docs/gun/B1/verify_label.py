from pathlib import Path
import sys,json,time,hashlib,base64
from playwright.sync_api import sync_playwright,Locator
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();fixture='\n'.join(p.read_text()for p in [R/'docs/map/E/test-helper.js',R/'docs/map/D/extension-fixture.js',H/'test-fixture.js'])+'''
__GB_TEST__.labelBounds=surface=>{const fn=CanvasRenderingContext2D.prototype.fillText,out=[];CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...args){if(String(text).includes('대공 자동 9km')){const m=this.getTransform(),p=new DOMPoint(x,y).matrixTransform(m),r=this.canvas.getBoundingClientRect(),dpr=this.canvas.width/r.width,w=this.measureText(text),k=Math.hypot(m.a,m.b)/dpr;out.push({text,left:r.x+p.x/dpr-w.actualBoundingBoxLeft*k,right:r.x+p.x/dpr+w.actualBoundingBoxRight*k,top:r.y+p.y/dpr-w.actualBoundingBoxAscent*k,bottom:r.y+p.y/dpr+w.actualBoundingBoxDescent*k,canvas:r.toJSON()});}return fn.call(this,text,x,y,...args);};try{if(surface==='PIP'){__PIP_A__.prepare();__PIP_A__.renderView(__PIP_A__.view());}else __VIEWPORT_A__.draw();}finally{CanvasRenderingContext2D.prototype.fillText=fn;}return out;};
'''
Locator.click=lambda self,*a,**kw:self.evaluate('e=>e.click()');checks={};records={};errors=[];E=H/'evidence/label';E.mkdir(parents=True,exist_ok=True)
with sync_playwright()as pw:
 b=launch(pw,True)
 for w,h in [(1400,900),(832,384)]:
  p=load_fleet(b,instrument(raw,fixture),own='CG_52_LATE_TICONDEROGA',width=w,height=h,errors=errors);p.set_default_timeout(180000);p.evaluate('__GB_TEST__.reset();Object.keys(__UI_A__.snapshot().windows).forEach(k=>__UI_A__.close(k))');p.locator('[data-weapon-b=MK45]').click();p.locator('[data-gun-mode-d=SINGLE]').click()
  for surface in ['MAIN','PIP']:
   if surface=='PIP':p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open();__UI_A__.open("CIC");__PIP_A__.setDistance(10)}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=240000,polling=50)
   else:p.evaluate('__VIEWPORT_A__.setDistance(10)')
   rows=p.evaluate('s=>__GB_TEST__.labelBounds(s)',surface);key=str(w)+'.'+surface;records[key]=rows;checks[key]=bool(rows)and all(q['left']>=q['canvas']['x']-1 and q['right']<=q['canvas']['right']+1 and q['top']>=q['canvas']['y']-1 and q['bottom']<=q['canvas']['bottom']+1 for q in rows);print(key,checks[key],rows,flush=True)
   c=p.context.new_cdp_session(p)
   try:(E/(key+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
   finally:c.detach()
  p.close()
 b.close()
out={'checks':checks,'records':records,'errors':errors,'pass':all(checks.values())and not errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(E/'results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');raise SystemExit(not out['pass'])
