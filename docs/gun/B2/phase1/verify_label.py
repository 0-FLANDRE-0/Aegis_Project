from pathlib import Path
import sys,json,time,hashlib,base64,os
from playwright.sync_api import sync_playwright,Locator
P=Path(__file__).resolve().parent;R=P.parents[3];H=R/'docs/gun/B1';sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=Path(os.environ.get('B2_LABEL_HTML','/tmp/aegis-gun-b2/phase1-ui.html')).read_bytes();fixture='\n'.join(p.read_text()for p in [R/'docs/map/E/test-helper.js',R/'docs/map/D/extension-fixture.js',H/'test-fixture.js'])+'''
__GB_TEST__.labelBounds=surface=>{const fn=CanvasRenderingContext2D.prototype.fillText,out=[];CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...args){if(String(text).includes('대공 자동 9km')||String(text).includes('대공 유효')){const m=this.getTransform(),p=new DOMPoint(x,y).matrixTransform(m),r=this.canvas.getBoundingClientRect(),dpr=this.canvas.width/r.width,w=this.measureText(text),k=Math.hypot(m.a,m.b)/dpr;const pad=128,ink=document.createElement('canvas');ink.width=this.canvas.width+pad*2;ink.height=this.canvas.height+pad*2;const a=ink.getContext('2d');a.setTransform(m.a,m.b,m.c,m.d,m.e+pad,m.f+pad);a.font=this.font;a.textAlign=this.textAlign;a.textBaseline=this.textBaseline;a.direction=this.direction;a.fillStyle='white';fn.call(a,text,x,y,...args);const data=a.getImageData(0,0,ink.width,ink.height).data;let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;for(let yy=0;yy<ink.height;yy++)for(let xx=0;xx<ink.width;xx++)if(data[(yy*ink.width+xx)*4+3]){minX=Math.min(minX,xx);maxX=Math.max(maxX,xx+1);minY=Math.min(minY,yy);maxY=Math.max(maxY,yy+1);}out.push({text,left:r.x+(minX-pad)/dpr,right:r.x+(maxX-pad)/dpr,top:r.y+(minY-pad)/dpr,bottom:r.y+(maxY-pad)/dpr,font:this.font,textBaseline:this.textBaseline,metricBox:{top:r.y+p.y/dpr-w.actualBoundingBoxAscent*k,bottom:r.y+p.y/dpr+w.actualBoundingBoxDescent*k},boundsMethod:'NATIVE_GLYPH_ALPHA_WITH_UNCLIPPED_MARGIN',canvas:r.toJSON()});}return fn.call(this,text,x,y,...args);};try{if(surface==='PIP'){__PIP_A__.prepare();__PIP_A__.renderView(__PIP_A__.view());}else __VIEWPORT_A__.draw();}finally{CanvasRenderingContext2D.prototype.fillText=fn;}return out;};
'''
Locator.click=lambda self,*a,**kw:self.evaluate('e=>e.click()');checks={};records={};errors=[];E=Path(os.environ.get('B2_LABEL_OUT',str(P/'evidence/label-preview')));E.mkdir(parents=True,exist_ok=True)
with sync_playwright()as pw:
 b=launch(pw,True)
 if os.environ.get('B2_LABEL_DPR'):
  native_new_page=b.new_page
  def configured_page(**kwargs):
   kwargs['device_scale_factor']=float(os.environ['B2_LABEL_DPR']);return native_new_page(**kwargs)
  b.new_page=configured_page
 for w,h in [(1400,900),(832,384)]:
  p=load_fleet(b,instrument(raw,fixture),own='CG_52_LATE_TICONDEROGA',width=w,height=h,errors=errors);p.set_default_timeout(180000);records[str(w)+'.devicePixelRatio']=p.evaluate('devicePixelRatio');p.evaluate('__GB_TEST__.reset();Object.keys(__UI_A__.snapshot().windows).forEach(k=>__UI_A__.close(k))');p.locator('[data-weapon-b=MK45]').click();p.locator('[data-gun-mode-d=SINGLE]').click()
  for surface in ['MAIN','PIP']:
   if surface=='PIP':p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open();__UI_A__.open("CIC");__PIP_A__.setDistance(10)}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=240000,polling=50)
   else:p.evaluate('__VIEWPORT_A__.setDistance(10)')
   rows=p.evaluate('s=>__GB_TEST__.labelBounds(s)',surface);key=str(w)+'.'+surface;records[key]=rows;checks[key]=any('대공 유효 ≥9km'in q['text']for q in rows)and any('대공 자동 9km'in q['text']for q in rows)and all(q['left']>=q['canvas']['x']-1 and q['right']<=q['canvas']['right']+1 and q['top']>=q['canvas']['y']-1 and q['bottom']<=q['canvas']['bottom']+1 for q in rows);checks[key+'.labelGap']=next(q['top']for q in rows if '대공 유효'in q['text'])-next(q['bottom']for q in rows if '대공 자동'in q['text'])>=2;print(key,checks[key],rows,flush=True)
   c=p.context.new_cdp_session(p)
   try:(E/(key+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
   finally:c.detach()
  p.close()
 b.close()
out={'checks':checks,'records':records,'errors':errors,'pass':all(checks.values())and not errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(E/'results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');raise SystemExit(not out['pass'])
