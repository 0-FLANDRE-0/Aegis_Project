"""Read-only preset captures after native rendering and compositor settlement."""
from pathlib import Path
import argparse,sys,base64,json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
with sync_playwright()as pw:
 b=launch(pw,True)
 p=load_fleet(b,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',width=1400,height=900)
 p.evaluate('async()=>{if(document.fullscreenElement)await document.exitFullscreen();__WIP148_3D_VIEW__.c12ApplyPreset("LOW");}')
 c=p.context.new_cdp_session(p);rows=[]
 for name,key in [('PC 가로','pc'),('폰 가로','phone'),('세로','portrait')]:
  for w,h in [(1400,900),(844,390),(390,844)]:
   p.set_viewport_size({'width':w,'height':h});p.wait_for_function('s=>AEGIS_VIEWPORT.raw.w===s[0]&&AEGIS_VIEWPORT.raw.h===s[1]',arg=[w,h],polling=50);p.evaluate('n=>__UI_A__.preset(n)',name);p.wait_for_timeout(700)
   p.evaluate('async()=>{__VIEWPORT_A__.draw();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}')
   data=c.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data'];file=f'preset-{key}-{w}x{h}.png';(a.out/file).write_bytes(base64.b64decode(data));rows.append({'file':file,'preset':name,'viewport':p.evaluate('AEGIS_VIEWPORT.snapshot()')})
 for w,h in [(1400,900),(390,844)]:
  p.set_viewport_size({'width':w,'height':h});p.wait_for_function('s=>AEGIS_VIEWPORT.raw.w===s[0]&&AEGIS_VIEWPORT.raw.h===s[1]',arg=[w,h],polling=50);p.evaluate('n=>__UI_A__.preset(n)','PC 가로'if w>h else'세로');p.evaluate('async()=>{const v=__WIP148_3D_VIEW__;await v.open();v.render(performance.now());}');p.wait_for_timeout(700);p.evaluate('async()=>{const v=__WIP148_3D_VIEW__;v.render(performance.now());v.renderer.getContext().finish();await new Promise(r=>requestAnimationFrame(r));}');file=f'3d-{w}x{h}.png';(a.out/file).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']));p.evaluate('__WIP148_3D_VIEW__.close()');rows.append({'file':file,'viewport':p.evaluate('AEGIS_VIEWPORT.snapshot()')})
 c.detach();b.close()
(a.out/'captures.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
