from pathlib import Path
import sys,json,hashlib,math
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
E=H/'evidence/motion';E.mkdir(parents=True,exist_ok=True);raw=(R/'Aegis_SIM_v48_WIP_MAP_C.html').read_bytes();checks={};rows=[];errors=[]
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
MONITOR='''async cfg=>{const el=document.getElementById('mapEngagementB'),same=el,canvas=document.getElementById(cfg.surface==='MAIN'?'c':'external3DMiniCicCanvas');const samples=[],mutations=[];let start=null,shifted=false;const mo=new MutationObserver(rs=>{for(const r of rs)if(r.attributeName==='hidden')mutations.push({old:r.oldValue,value:el.hidden})});mo.observe(el,{attributes:true,attributeOldValue:true,attributeFilter:['hidden']});await new Promise(done=>{function f(t){if(start===null)start=t;const c=__MAP_C__.snapshot(),p=c.painted[cfg.surface],a=window.__C_ARC__?.[cfg.surface];if(c.tag.anchor&&p){const rect=el.getBoundingClientRect(),style=getComputedStyle(el);samples.push({t,sim:c.clockS,anchor:c.tag.anchor,painted:p.screen,arc:a,world:c.tag.world,rect:{x:rect.x,y:rect.y,w:rect.width,h:rect.height},side:c.tag.side,hidden:el.hidden,visibility:style.visibility,same:el===same&&el===document.getElementById('mapEngagementB')});}if(!shifted&&t-start>4000){__MC_TEST__.nudgeMotion(1000);shifted=true;}if(t-start<10000)requestAnimationFrame(f);else done()}requestAnimationFrame(f)});mo.disconnect();__MC_TEST__.stopMotion();document.getElementById('uiPauseA').click();return{samples,hiddenMutations:mutations,stats:__MAP_C__.snapshot().stats}}'''
# Test-only capture of the actual 2D basic plot arc, including canvas transform/DPR.
ARC='''(()=>{const original=CanvasRenderingContext2D.prototype.arc;window.__C_ARC__={};CanvasRenderingContext2D.prototype.arc=function(x,y,r,...rest){const c=window.__MAP_C__?.snapshot(),surface=this.canvas.id==='external3DMiniCicCanvas'?'PIP':this.canvas.id==='c'?'MAIN':null;if(surface&&c?.tag?.world){const tr=this.getTransform(),box=this.canvas.getBoundingClientRect(),px=box.x+(tr.a*x+tr.c*y+tr.e)*box.width/this.canvas.width,py=box.y+(tr.b*x+tr.d*y+tr.f)*box.height/this.canvas.height;const a=c.tag.anchor;if(Math.hypot(px-a.x,py-a.y)<.05&&r*Math.hypot(tr.a,tr.b)*box.width/this.canvas.width>1&&r*Math.hypot(tr.a,tr.b)*box.width/this.canvas.width<8)window.__C_ARC__[surface]={x:px,y:py,at:performance.now()};}return Reflect.apply(original,this,[x,y,r,...rest]);};})();'''
with sync_playwright()as pw:
 b=launch(pw,True)
 for w,h in [(1400,900),(832,384)]:
  p=load_fleet(b,instrument(raw,(H/'test-helper.js').read_text()+'\n'+(H/'motion-helper.js').read_text()),width=w,height=h,errors=errors);p.set_default_timeout(180000);p.evaluate(ARC)
  for surface in ['MAIN','PIP']:
   if surface=='PIP':
    p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000)
   for speed in [1,8,64]:
    p.evaluate('__MC_TEST__.stopMotion()');reset(p)
    if surface=='PIP':p.evaluate('__UI_A__.open("CIC");__PIP_A__.setDistance(300)')
    else:p.evaluate('__WIP148_3D_VIEW__.close()')
    p.evaluate('__VIEWPORT_A__.setDistance(300)');select(p,'SM6');tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');p.wait_for_timeout(150);o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',tid);pos=p.evaluate('a=>a.surface==="PIP"?__PIP_A__.worldToScreen(a.o.x,a.o.y):__VIEWPORT_A__.worldToScreen(a.o.x,a.o.y)',{'o':o,'surface':surface});p.mouse.click(pos['x'],pos['y']);p.wait_for_timeout(150);p.evaluate('id=>__MC_TEST__.startMotion(id)',tid);p.locator('.time-btn[data-tw="'+str(speed)+'"]').click();q=p.evaluate(MONITOR,{'surface':surface,'id':tid});samples=q['samples'];errs=[math.hypot(s['anchor']['x']-s['painted']['x'],s['anchor']['y']-s['painted']['y'])for s in samples];arcs=[math.hypot(s['anchor']['x']-s['arc']['x'],s['anchor']['y']-s['arc']['y'])for s in samples if s['arc']];flips=sum(a['side']!=bb['side']for a,bb in zip(samples,samples[1:]));tag=f'{w}.{surface}.{speed}x';ck(tag+'.samples10s',len(samples)>=3 and samples[-1]['t']-samples[0]['t']>=9900);ck(tag+'.anchorError3px',max(errs,default=999)<=3);ck(tag+'.actualCanvasArc3px',len(arcs)>=3 and max(arcs,default=999)<=3);ck(tag+'.sameNodeNoHidden',not q['hiddenMutations']and all(s['same']and not s['hidden']and s['visibility']=='visible'for s in samples));ck(tag+'.noSideJitter',flips<=1)
    # Expected continuous movement is bounded by observed speed and cubic 150ms correction.
    factor=p.evaluate('a=>a.surface==="PIP"?__PIP_A__.view().rect.shortSide*.42/300:__VIEWPORT_A__.snapshot().viewport.twoD.shortSide*.42/300',{'surface':surface});max_extra=0
    for a,bb in zip(samples,samples[1:]):
     dt=(bb['t']-a['t'])/1000;ds=bb['sim']-a['sim'];travel=math.hypot(bb['anchor']['x']-a['anchor']['x'],bb['anchor']['y']-a['anchor']['y']);bound=(.25*max(0,ds)+min(1,3*dt/.15))*factor+.5;max_extra=max(max_extra,travel-bound)
    ck(tag+'.noInstantaneousJump',max_extra<=1);row={'size':[w,h],'surface':surface,'scale':speed,'frames':len(samples),'wallDurationS':(samples[-1]['t']-samples[0]['t'])/1000,'simDurationS':samples[-1]['sim']-samples[0]['sim'],'maxAnchorErrorPx':max(errs,default=None),'maxActualArcErrorPx':max(arcs,default=None),'sideFlips':flips,'maxJumpExcessPx':max_extra,'stats':q['stats']};rows.append(row);(E/(tag+'.json')).write_text(json.dumps(q,separators=(',',':')))
   p.evaluate('__MC_TEST__.stopMotion()')
  p.close()
 b.close()
ck('pageErrors0',not errors);q={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(E/'motion.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));raise SystemExit(0 if q['pass']else 1)
