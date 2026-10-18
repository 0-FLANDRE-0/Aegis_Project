"""Read-only UI geometry census, including explicitly revealed conditional UI.

Reveals are local DOM presentation only; no combat buttons are invoked. Each
record identifies native visibility or a diagnostic reveal, never pretends a
hidden widget is simultaneously on screen in the normal layout.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
CAPTURE=r'''state=>{const special=['external3DReadout','c14ControlsToggle','external3DTerminalSummary','external3DQuickState','external3DCanvas','c5ModelPanel'],out=[];for(const e of document.querySelectorAll('[id],[style],.c14-topbar,.external3d-toolbar,.scanline,.vignette')){const css=getComputedStyle(e),r=e.getBoundingClientRect(),isDialog=e.tagName==='DIALOG';if(!['fixed','absolute'].includes(css.position)&&!special.includes(e.id)&&!isDialog)continue;const screen=e.closest('#external3DView')?'3D':e.closest('#wip200MissileCatalog')?'CATALOG':'2D';if(e.id==='c'||e.id==='external3DView'||e.id==='external3DCanvas'||e.id==='aegisSafeAreaProbeVpA')continue;out.push({id:e.id||'(no id) '+(e.className?'.'+String(e.className).replaceAll(' ','.'):'#'+(e.parentElement?.id||e.parentElement?.tagName)+'>'+e.tagName+':nth-child('+([...e.parentElement.children].indexOf(e)+1)+')'),tag:e.tagName,screen,state,position:css.position,display:css.display,visible:!!(r.width&&r.height)&&css.visibility!=='hidden',x:r.x,y:r.y,w:r.width,h:r.height,ancestor:e.parentElement?.id||e.parentElement?.className||e.parentElement?.tagName,classes:e.className});}return out;}'''
REVEAL=r'''()=>{window.__vpAuditRestores=[];const elems=[...document.querySelectorAll('[id],[style],.c14-topbar,.external3d-toolbar')];for(const e of elems){if(e.id==='c'||e.id==='external3DView'||e.id==='external3DCanvas'||e.id==='aegisSafeAreaProbeVpA'||e.id==='wip125PreSailOverlay')continue;const s=getComputedStyle(e);if(!['fixed','absolute'].includes(s.position)&&e.tagName!=='DIALOG')continue;__vpAuditRestores.push([e,e.style.cssText,e.hidden,e.inert,e.className]);e.hidden=false;e.inert=false;if(e.id==='c14ControlsDrawer')e.classList.add('open');if(e.tagName==='DIALOG'){try{e.showModal();}catch(_){} }else if(s.display==='none')e.style.display=/Panel|Drawer|Toolbar|toolbar|topbar/.test(e.id+' '+e.className)?'flex':'block';}}'''
RESTORE=r'''()=>{for(const [e,style,hidden,inert,cls]of window.__vpAuditRestores??[]){if(e.tagName==='DIALOG')e.close();e.style.cssText=style;e.hidden=hidden;e.inert=inert;e.className=cls;}window.__vpAuditRestores=[];}'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--coarse',action='store_true');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();rows=[];errors=[];controls=[]
 with sync_playwright()as pw:
  b=launch(pw,True)
  class Device:
   def new_page(self,**kw):return b.new_page(**kw,has_touch=a.coarse,is_mobile=a.coarse)
  p=load_fleet(Device(),raw,errors=errors,width=1400,height=900)
  p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(1)');p.wait_for_timeout(100)
  p.evaluate("""async()=>{const v=__WIP148_3D_VIEW__;await v.open();v.c12ApplyPreset('LOW');v.render(performance.now());v.close();__WIP200_MISSILE_CATALOG__.ensureUi();for(const id of ['damageControlToggleV1','damageFloodToggleV1']){const e=document.getElementById(id);e?.click();await new Promise(resolve=>setTimeout(resolve,350));e?.click();}}""")
  for w,h in [(1400,900),(1400,560),(600,900),(844,390)]:
   p.set_viewport_size({'width':w,'height':h});p.wait_for_timeout(350)
   for tab in ['NAV','ARM','FLEET','AIR','DEBUG']:
    p.locator('[data-tab='+tab+']').click();p.wait_for_timeout(200);rows.append({'size':[w,h],'state':'2D_'+tab,'visible':p.evaluate('AEGIS_VIEWPORT.snapshot()'),'elements':p.evaluate(CAPTURE,'2D_'+tab)})
   p.evaluate(REVEAL);p.wait_for_timeout(200);rows.append({'size':[w,h],'state':'2D_CONDITIONAL_REVEALED','elements':p.evaluate(CAPTURE,'2D_CONDITIONAL_REVEALED')});p.evaluate(RESTORE)
   p.evaluate("document.getElementById('external3DView').classList.add('active')");p.wait_for_timeout(200);rows.append({'size':[w,h],'state':'3D_DEFAULT','elements':p.evaluate(CAPTURE,'3D_DEFAULT')});p.evaluate(REVEAL);p.wait_for_timeout(200);rows.append({'size':[w,h],'state':'3D_CONDITIONAL_REVEALED','elements':p.evaluate(CAPTURE,'3D_CONDITIONAL_REVEALED')});p.evaluate(RESTORE);p.evaluate("document.getElementById('external3DView').classList.remove('active')")
  controls=p.evaluate("()=>[...document.querySelectorAll('button,select,input,textarea,[role=tab]')].map(e=>({id:e.id||'(no id)',tag:e.tagName,label:(e.textContent||e.getAttribute('aria-label')||e.title||'').trim().slice(0,180),parent:e.closest('[data-page]')?.dataset.page??e.closest('#external3DView')?.id??e.closest('[id]')?.parentElement?.closest('[id]')?.id??'',classes:e.className,data:{...e.dataset}}))")
  media=p.evaluate("()=>[...document.styleSheets].flatMap((s,i)=>[...s.cssRules].filter(r=>r.type===CSSRule.MEDIA_RULE).map(r=>({styleSheetIndex:i,condition:r.conditionText,css:r.cssText})))")
  b.close()
 out={'htmlSha256':hashlib.sha256(raw).hexdigest(),'inputMedia':'coarse/mobile'if a.coarse else'fine/desktop','rows':rows,'controls':controls,'media':media,'errors':errors,'limits':'Browser CSS boxes. Conditional overlays revealed without invoking commands; these are potential positions, not simultaneous native visibility. GPU is not required for UI census.'};(a.out/'ui-layout.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'rows':len(rows),'uniqueFloatingIds':len({e['id']for r in rows for e in r['elements']}),'controls':len(controls),'errors':errors}));raise SystemExit(0 if not errors else 1)
if __name__=='__main__':main()
